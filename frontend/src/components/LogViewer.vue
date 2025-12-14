<template>
  <el-card class="log-viewer-card">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <span class="header-icon">📝</span>
          <span>执行日志</span>
          <el-tag v-if="isStreaming" type="success" size="small" effect="dark">
            <el-icon class="is-loading"><Loading /></el-icon>
            实时
          </el-tag>
        </div>
        <div class="header-center">
          <el-radio-group v-model="agentFilter" size="small">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="main_agent">主Agent</el-radio-button>
            <el-radio-button value="extract_agent">提取Agent</el-radio-button>
          </el-radio-group>
        </div>
        <div class="header-right">
          <el-button text size="small" @click="scrollToBottom">
            <el-icon><Bottom /></el-icon>
          </el-button>
        </div>
      </div>
    </template>
    
    <div ref="logContainer" class="log-container">
      <div v-if="logs.length === 0" class="empty-logs">
        <el-icon class="empty-icon"><Document /></el-icon>
        <p>等待执行日志...</p>
      </div>
      
      <div v-else class="log-items">
        <div 
          v-for="log in filteredLogs" 
          :key="log.step" 
          class="log-item"
          :class="getLogClass(log.type)"
        >
          <div class="log-header">
            <span class="log-step">Step {{ log.step }}</span>
            <el-tag :type="getLogTagType(log.type)" size="small" effect="plain">
              {{ getLogTypeText(log.type) }}
            </el-tag>
            <el-tag 
              v-if="log.tool_name && (log.type === 'tool_call' || log.type === 'tool_result')" 
              type="warning" 
              size="small" 
              effect="plain"
              class="tool-name-tag"
            >
              {{ log.tool_name }}
            </el-tag>
            <el-tag 
              v-if="log.agent_type" 
              :type="log.agent_type === 'main_agent' ? 'primary' : 'success'" 
              size="small" 
              effect="plain"
              class="agent-type-tag"
            >
              {{ log.agent_type === 'main_agent' ? '主Agent' : '提取Agent' }}
            </el-tag>
            <span v-if="log.tokens" class="log-tokens">
              <el-icon><Coin /></el-icon>
              {{ log.tokens }} tokens
            </span>
          </div>
          <div class="log-content">
            <pre v-if="isJsonContent(log.content)">{{ formatJson(log.content) }}</pre>
            <div v-else class="log-text">{{ log.content }}</div>
          </div>
        </div>
        
        <div v-if="isStreaming" class="log-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>正在执行...</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { Loading, Bottom, Document, Coin } from '@element-plus/icons-vue'
import { createExecutionLogStream, getExecutionLogs } from '@/api/tasks'

const props = defineProps({
  taskId: {
    type: String,
    required: true
  },
  executionId: {
    type: String,
    required: true
  },
  taskStatus: {
    type: String,
    default: ''
  },
  executionStatus: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['complete'])

const logContainer = ref(null)
const logs = ref([])
const isStreaming = ref(false)
const agentFilter = ref('all')
let eventSource = null

// 根据筛选条件过滤日志
const filteredLogs = computed(() => {
  if (agentFilter.value === 'all') {
    return logs.value
  }
  return logs.value.filter(log => log.agent_type === agentFilter.value)
})

onMounted(async () => {
  const status = props.executionStatus || props.taskStatus
  if (status === 'running') {
    startStreaming()
  } else if (props.executionId) {
    // 已完成的执行，加载历史日志
    await loadHistoryLogs()
  }
})

onUnmounted(() => {
  stopStreaming()
})

watch(() => props.executionStatus, (newStatus) => {
  if (newStatus === 'running') {
    startStreaming()
  } else {
    stopStreaming()
  }
})

watch(() => props.taskStatus, (newStatus) => {
  if (newStatus === 'running') {
    startStreaming()
  } else {
    stopStreaming()
  }
})

// 监听 executionId 变化
watch(() => props.executionId, async (newId, oldId) => {
  if (newId !== oldId) {
    stopStreaming()
    logs.value = []
    
    const status = props.executionStatus || props.taskStatus
    if (status === 'running') {
      startStreaming()
    } else if (newId) {
      // 切换到已完成的执行，加载历史日志
      await loadHistoryLogs()
    }
  }
})

function startStreaming() {
  if (eventSource) {
    eventSource.close()
  }
  
  isStreaming.value = true
  logs.value = []
  
  eventSource = createExecutionLogStream(props.taskId, props.executionId, {
    onStep: (data) => {
      // SSE 返回的数据已包含 agent_type 和 tool_name
      logs.value.push({
        step: data.step,
        type: data.type,
        content: data.content,
        tokens: data.tokens,
        agent_type: data.agent_type,
        tool_name: data.tool_name
      })
      nextTick(() => scrollToBottom())
    },
    onComplete: (data) => {
      isStreaming.value = false
      emit('complete', data)
    },
    onTimeout: () => {
      isStreaming.value = false
    },
    onError: () => {
      isStreaming.value = false
    }
  })
}

function stopStreaming() {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
  isStreaming.value = false
}

async function loadHistoryLogs() {
  try {
    const data = await getExecutionLogs(props.taskId, props.executionId)
    // 转换数据格式，API 返回的字段名与组件期望的不同
    logs.value = (data.items || []).map(item => ({
      step: item.step_number,
      type: item.step_type,
      content: item.output_content || item.input_content,
      tokens: (item.input_tokens || 0) + (item.output_tokens || 0),
      agent_type: item.agent_type,
      tool_name: item.tool_name
    }))
  } catch (error) {
    console.error('加载历史日志失败:', error)
  }
}

function scrollToBottom() {
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

function getLogClass(type) {
  const map = {
    think: 'log-think',
    tool_call: 'log-tool-call',
    tool_result: 'log-tool-result',
    extract: 'log-extract',
    final: 'log-final'
  }
  return map[type] || ''
}

function getLogTagType(type) {
  const map = {
    think: 'primary',
    tool_call: 'warning',
    tool_result: 'info',
    extract: 'success',
    final: ''
  }
  return map[type] || 'info'
}

function getLogTypeText(type) {
  const map = {
    think: '思考',
    tool_call: '工具调用',
    tool_result: '工具结果',
    extract: '信息提取',
    final: '最终结果'
  }
  return map[type] || type
}

function isJsonContent(content) {
  if (!content) return false
  try {
    const trimmed = content.trim()
    return trimmed.startsWith('{') || trimmed.startsWith('[')
  } catch {
    return false
  }
}

function formatJson(content) {
  try {
    return JSON.stringify(JSON.parse(content), null, 2)
  } catch {
    return content
  }
}

// 暴露方法给父组件
defineExpose({
  setLogs: (newLogs) => {
    logs.value = newLogs
  }
})
</script>

<style scoped>
.log-viewer-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.log-viewer-card :deep(.el-card__body) {
  flex: 1;
  padding: 0;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #e0e0e0;
}

.header-icon {
  font-size: 20px;
}

.log-container {
  height: 400px;
  overflow-y: auto;
  padding: 16px;
}

.empty-logs {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #606060;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.log-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.log-item {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 12px;
  border-left: 3px solid #409eff;
}

.log-think {
  border-left-color: #409eff;
}

.log-tool-call {
  border-left-color: #e6a23c;
}

.log-tool-result {
  border-left-color: #909399;
}

.log-extract {
  border-left-color: #67c23a;
}

.log-final {
  border-left-color: #f56c6c;
}

.log-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.log-step {
  font-weight: 600;
  color: #a0a0a0;
  font-size: 12px;
}

.tool-name-tag {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

.agent-type-tag {
  margin-left: 4px;
}

.log-tokens {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #808080;
}

.log-content {
  color: #c0c0c0;
  font-size: 13px;
  line-height: 1.6;
}

.log-content pre {
  margin: 0;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 12px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.log-text {
  white-space: pre-wrap;
  word-break: break-word;
}

.log-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  color: #409eff;
}
</style>
