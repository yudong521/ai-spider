<template>
  <el-card class="token-stats-card">
    <template #header>
      <div class="card-header">
        <span class="header-icon">📊</span>
        <span>Token 统计</span>
      </div>
    </template>
    
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
    
    <div v-else-if="!stats" class="empty-state">
      <p>暂无统计数据</p>
    </div>
    
    <div v-else class="stats-content">
      <div class="stats-summary">
        <div class="stat-item main-agent">
          <div class="stat-label">
            <el-tag size="small" type="primary" effect="dark">主 Agent</el-tag>
          </div>
          <div class="stat-value">{{ formatNumber(getAgentTotalTokens('main_agent')) }}</div>
          <div class="stat-sub">tokens</div>
        </div>
        <div class="stat-item extract-agent">
          <div class="stat-label">
            <el-tag size="small" type="success" effect="dark">提取 Agent</el-tag>
          </div>
          <div class="stat-value">{{ formatNumber(getAgentTotalTokens('extract_agent')) }}</div>
          <div class="stat-sub">tokens</div>
        </div>
      </div>
      
      <el-divider />
      
      <div class="stats-by-agent">
        <h4>详细统计</h4>
        <div class="agent-items">
          <div v-for="(agent, key) in stats.by_agent" :key="key" class="agent-item">
            <div class="agent-name">
              <el-tag size="small" :type="key === 'main_agent' ? 'primary' : 'success'">
                {{ key === 'main_agent' ? '主 Agent' : '提取 Agent' }}
              </el-tag>
            </div>
            <div class="agent-stats">
              <span>输入: {{ formatNumber(agent.input_tokens) }}</span>
              <span>输出: {{ formatNumber(agent.output_tokens) }}</span>
              <span>{{ agent.calls }} 次调用</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { getTaskTokenStats, getExecutionTokenStats } from '@/api/stats'

const props = defineProps({
  taskId: {
    type: String,
    default: ''
  },
  executionId: {
    type: String,
    default: ''
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

const stats = ref(null)
const loading = ref(false)

onMounted(() => {
  fetchStats()
})

watch(() => props.taskStatus, (newStatus, oldStatus) => {
  if (oldStatus === 'running' && newStatus !== 'running') {
    fetchStats()
  }
})

watch(() => props.executionStatus, (newStatus, oldStatus) => {
  if (oldStatus === 'running' && newStatus !== 'running') {
    fetchStats()
  }
})

async function fetchStats() {
  loading.value = true
  try {
    if (props.executionId) {
      stats.value = await getExecutionTokenStats(props.executionId)
    } else if (props.taskId) {
      stats.value = await getTaskTokenStats(props.taskId)
    }
  } catch (error) {
    console.error('获取统计失败:', error)
  } finally {
    loading.value = false
  }
}

function formatNumber(num) {
  if (num >= 10000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num?.toLocaleString() || '0'
}

function getAgentTotalTokens(agentType) {
  const agent = stats.value?.by_agent?.[agentType]
  if (!agent) return 0
  return (agent.input_tokens || 0) + (agent.output_tokens || 0)
}

// 暴露刷新方法
defineExpose({
  refresh: fetchStats
})
</script>

<style scoped>
.token-stats-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
}

.card-header {
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

.loading-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: #606060;
}

.stats-content {
  padding: 8px 0;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 12px;
}

.stat-label {
  font-size: 12px;
  color: #808080;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #e0e0e0;
}

.stat-sub {
  font-size: 12px;
  color: #606060;
  margin-top: 2px;
}

.stat-item.main-agent {
  border-left: 3px solid #409eff;
}

.stat-item.extract-agent {
  border-left: 3px solid #67c23a;
}

.stats-by-agent h4 {
  font-size: 14px;
  color: #a0a0a0;
  margin-bottom: 12px;
}

.agent-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.agent-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px;
  background: rgba(0, 0, 0, 0.15);
  border-radius: 6px;
}

.agent-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909090;
}
</style>
