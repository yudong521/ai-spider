<template>
  <el-card class="execution-list-card">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <span class="header-icon">📊</span>
          <span>执行历史</span>
          <el-tag type="info" size="small">{{ total }} 次执行</el-tag>
        </div>
        <div class="header-right">
          <el-button text @click="handleRefresh" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </template>
    
    <div v-if="executions.length === 0" class="empty-state">
      <el-empty description="暂无执行记录" :image-size="80">
        <el-button type="primary" @click="handleNewExecution">
          <el-icon><VideoPlay /></el-icon>
          立即执行
        </el-button>
      </el-empty>
    </div>
    
    <div v-else class="execution-items">
      <div 
        v-for="execution in executions" 
        :key="execution.id" 
        class="execution-item"
        :class="{ 'is-running': execution.status === 'running' }"
        @click="handleView(execution)"
      >
        <div class="execution-header">
          <div class="execution-number">
            <span class="number-badge">#{{ execution.execution_number }}</span>
            <el-tag :type="getStatusType(execution.status)" size="small" effect="dark">
              {{ getStatusText(execution.status) }}
            </el-tag>
          </div>
          <span class="execution-time">{{ formatTime(execution.created_at) }}</span>
        </div>
        
        <div class="execution-info">
          <div class="info-item" v-if="execution.started_at">
            <span class="info-label">开始时间</span>
            <span class="info-value">{{ formatDateTime(execution.started_at) }}</span>
          </div>
          <div class="info-item" v-if="execution.completed_at">
            <span class="info-label">完成时间</span>
            <span class="info-value">{{ formatDateTime(execution.completed_at) }}</span>
          </div>
          <div class="info-item" v-if="execution.completed_at && execution.started_at">
            <span class="info-label">耗时</span>
            <span class="info-value">{{ getDuration(execution) }}</span>
          </div>
        </div>
        
        <div class="execution-actions" @click.stop>
          <el-button 
            v-if="execution.status === 'running'" 
            type="warning" 
            size="small"
            @click="handleCancel(execution)"
          >
            取消
          </el-button>
          <el-button 
            type="primary" 
            size="small" 
            text
            @click="handleView(execution)"
          >
            查看详情
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
    
    <div v-if="total > pageSize" class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        small
        @current-change="handlePageChange"
      />
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, VideoPlay, ArrowRight } from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import { formatRelativeTime, formatDateTime, formatDuration } from '@/utils/time'

const props = defineProps({
  taskId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['new-execution'])

const router = useRouter()
const taskStore = useTaskStore()

const executions = ref([])
const total = ref(0)
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
let refreshInterval = null

onMounted(() => {
  fetchExecutions()
  // 自动刷新（如果有运行中的执行）
  refreshInterval = setInterval(() => {
    if (executions.value.some(e => e.status === 'running')) {
      fetchExecutions()
    }
  }, 5000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})

watch(() => props.taskId, () => {
  currentPage.value = 1
  fetchExecutions()
})

async function fetchExecutions() {
  loading.value = true
  try {
    const data = await taskStore.fetchExecutions(props.taskId, {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    })
    executions.value = data.items
    total.value = data.total
  } catch (error) {
    console.error('获取执行历史失败:', error)
  } finally {
    loading.value = false
  }
}

function handleRefresh() {
  fetchExecutions()
}

function handlePageChange(page) {
  currentPage.value = page
  fetchExecutions()
}

function handleView(execution) {
  router.push(`/task/${props.taskId}/execution/${execution.id}`)
}

function handleNewExecution() {
  emit('new-execution')
}

async function handleCancel(execution) {
  try {
    await ElMessageBox.confirm('确定要取消该执行吗？', '提示', {
      type: 'warning'
    })
    await taskStore.cancelExecution(props.taskId, execution.id)
    ElMessage.success('执行已取消')
    fetchExecutions()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消执行失败:', error)
    }
  }
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
  return formatRelativeTime(time)
}

function getDuration(execution) {
  return formatDuration(execution.started_at, execution.completed_at)
}

// 暴露刷新方法
defineExpose({
  refresh: fetchExecutions
})
</script>

<style scoped>
.execution-list-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.empty-state {
  padding: 40px 0;
}

.execution-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.execution-item {
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.execution-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(100, 180, 255, 0.3);
}

.execution-item.is-running {
  border-color: rgba(64, 158, 255, 0.4);
  background: rgba(64, 158, 255, 0.05);
}

.execution-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.execution-number {
  display: flex;
  align-items: center;
  gap: 8px;
}

.number-badge {
  font-size: 14px;
  font-weight: 600;
  color: #a0a0a0;
}

.execution-time {
  font-size: 12px;
  color: #707070;
}

.execution-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: 11px;
  color: #707070;
}

.info-value {
  font-size: 13px;
  color: #b0b0b0;
}

.execution-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>

