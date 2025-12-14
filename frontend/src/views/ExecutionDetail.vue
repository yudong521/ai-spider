<template>
  <div class="execution-detail-page">
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <el-button text @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <div class="breadcrumb" v-if="task && execution">
            <span class="task-name" @click="goToTask">{{ task.name }}</span>
            <el-icon><ArrowRight /></el-icon>
            <span class="execution-number">执行 #{{ execution.execution_number }}</span>
          </div>
        </div>
        <div class="header-actions" v-if="execution">
          <el-tag :type="getStatusType(execution.status)" effect="dark" size="large">
            {{ getStatusText(execution.status) }}
          </el-tag>
          <el-button 
            v-if="execution.status === 'running'" 
            type="warning"
            @click="handleCancel"
          >
            <el-icon><VideoPause /></el-icon>
            取消执行
          </el-button>
        </div>
      </div>
    </header>
    
    <main class="page-main" v-if="task && execution">
      <div class="main-content">
        <!-- 执行信息 -->
        <div class="execution-meta">
          <el-descriptions :column="4" border size="small">
            <el-descriptions-item label="执行ID">{{ execution.id }}</el-descriptions-item>
            <el-descriptions-item label="任务">{{ task.name }}</el-descriptions-item>
            <el-descriptions-item label="主Agent模型">{{ task.model }}</el-descriptions-item>
            <el-descriptions-item label="提取Agent模型">{{ task.extract_model || task.model }}</el-descriptions-item>
            <el-descriptions-item label="执行序号">#{{ execution.execution_number }}</el-descriptions-item>
            <el-descriptions-item label="开始时间">{{ formatTime(execution.started_at) || '-' }}</el-descriptions-item>
            <el-descriptions-item label="完成时间">{{ formatTime(execution.completed_at) || '-' }}</el-descriptions-item>
            <el-descriptions-item label="耗时">{{ getDuration() }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(execution.status)" size="small">
                {{ getStatusText(execution.status) }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <!-- Token统计和执行日志 -->
        <div class="detail-grid">
          <div class="grid-left">
            <TokenStats 
              ref="tokenStatsRef"
              :execution-id="execution.id" 
              :execution-status="execution.status" 
            />
          </div>
          <div class="grid-right">
            <LogViewer 
              ref="logViewerRef"
              :task-id="task.id"
              :execution-id="execution.id" 
              :execution-status="execution.status"
              @complete="handleExecutionComplete"
            />
          </div>
        </div>
        
        <!-- 执行结果 -->
        <div class="result-section">
          <ResultPreview 
            :result="execution.result"
            :status="execution.status"
            :error-message="execution.error_message"
            :task-name="task.name"
          />
        </div>
      </div>
    </main>
    
    <div v-else class="loading-page">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft,
  ArrowRight,
  VideoPause, 
  Loading 
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import { formatDateTime, formatDuration } from '@/utils/time'
import TokenStats from '@/components/TokenStats.vue'
import LogViewer from '@/components/LogViewer.vue'
import ResultPreview from '@/components/ResultPreview.vue'

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()

const task = ref(null)
const execution = ref(null)
const tokenStatsRef = ref(null)
const logViewerRef = ref(null)
let refreshInterval = null

onMounted(async () => {
  const taskId = route.params.taskId
  const executionId = route.params.executionId
  
  // 并行获取任务和执行信息
  const [taskData, executionData] = await Promise.all([
    taskStore.fetchTask(taskId),
    taskStore.fetchExecution(taskId, executionId)
  ])
  
  task.value = taskData
  execution.value = executionData
  
  // 如果执行中，定期刷新状态
  if (execution.value?.status === 'running') {
    startRefresh()
  }
})

onUnmounted(() => {
  stopRefresh()
})

function startRefresh() {
  refreshInterval = setInterval(async () => {
    const taskId = route.params.taskId
    const executionId = route.params.executionId
    execution.value = await taskStore.fetchExecution(taskId, executionId)
    
    if (execution.value?.status !== 'running') {
      stopRefresh()
    }
  }, 3000)
}

function stopRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

function goBack() {
  router.push(`/task/${route.params.taskId}`)
}

function goToTask() {
  router.push(`/task/${route.params.taskId}`)
}

async function handleCancel() {
  try {
    execution.value = await taskStore.cancelExecution(
      route.params.taskId, 
      route.params.executionId
    )
    ElMessage.success('执行已取消')
    stopRefresh()
  } catch (error) {
    console.error('取消执行失败:', error)
  }
}

function handleExecutionComplete(data) {
  // 执行完成时更新状态
  if (data.status) {
    execution.value.status = data.status
    execution.value.result = data.result
    execution.value.error_message = data.error
  }
  
  // 刷新统计
  tokenStatsRef.value?.refresh()
  stopRefresh()
  
  // 重新获取完整执行数据
  taskStore.fetchExecution(route.params.taskId, route.params.executionId).then(e => {
    execution.value = e
  })
}

function getStatusType(status) {
  const map = {
    pending: 'info',
    running: 'primary',
    completed: 'success',
    failed: 'danger',
    cancelled: 'warning'
  }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = {
    pending: '等待中',
    running: '执行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return map[status] || status
}

function formatTime(time) {
  return formatDateTime(time)
}

function getDuration() {
  return formatDuration(execution.value?.started_at, execution.value?.completed_at)
}
</script>

<style scoped>
.execution-detail-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #808080;
  font-size: 14px;
}

.task-name {
  color: #58a6ff;
  cursor: pointer;
}

.task-name:hover {
  text-decoration: underline;
}

.execution-number {
  color: #e0e0e0;
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-main {
  flex: 1;
  padding: 24px;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
}

.execution-meta {
  margin-bottom: 24px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.result-section {
  margin-top: 24px;
}

.loading-page {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  height: 100vh;
  color: #808080;
  font-size: 16px;
}

@media (max-width: 1024px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>

