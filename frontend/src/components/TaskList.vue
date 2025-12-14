<template>
  <el-card class="task-list-card">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <span class="header-icon">📋</span>
          <span>任务列表</span>
          <el-tag type="info" size="small">{{ total }} 个任务</el-tag>
        </div>
        <div class="header-right">
          <el-button text @click="handleRefresh" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </template>
    
    <div v-if="tasks.length === 0" class="empty-state">
      <el-empty description="暂无任务，创建一个试试吧" />
    </div>
    
    <div v-else class="task-items">
      <div 
        v-for="task in tasks" 
        :key="task.id" 
        class="task-item"
        @click="handleView(task)"
      >
        <div class="task-status">
          <span class="status-dot" :class="getStatusClass(task.status)"></span>
        </div>
        
        <div class="task-content">
          <div class="task-name">{{ task.name }}</div>
          <div class="task-meta">
            <el-tag size="small" type="info">{{ task.model }}</el-tag>
            <span class="task-time">{{ formatTime(task.created_at) }}</span>
          </div>
        </div>
        
        <div class="task-status-text">
          <el-tag :type="getStatusType(task.status)" effect="dark">
            {{ getStatusText(task.status) }}
          </el-tag>
        </div>
        
        <div class="task-actions" @click.stop>
          <el-button 
            v-if="task.status === 'pending'" 
            type="primary" 
            size="small"
            @click="handleRun(task)"
          >
            执行
          </el-button>
          <el-button 
            v-if="task.status === 'running'" 
            type="warning" 
            size="small"
            @click="handleCancel(task)"
          >
            取消
          </el-button>
          <el-button 
            v-if="task.status === 'failed'" 
            type="primary" 
            size="small"
            @click="handleRun(task)"
          >
            重试
          </el-button>
          <el-button 
            v-if="task.status === 'completed' || task.status === 'cancelled'" 
            type="success" 
            size="small"
            @click="handleRerun(task)"
          >
            重新执行
          </el-button>
          <el-button 
            type="danger" 
            size="small" 
            text
            @click="handleDelete(task)"
          >
            <el-icon><Delete /></el-icon>
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
        @current-change="handlePageChange"
      />
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Delete } from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import { formatRelativeTime } from '@/utils/time'

const router = useRouter()
const taskStore = useTaskStore()

const currentPage = ref(1)
const pageSize = ref(10)
let refreshInterval = null

const tasks = computed(() => taskStore.tasks)
const total = computed(() => taskStore.total)
const loading = computed(() => taskStore.loading)

onMounted(() => {
  fetchTasks()
  // 自动刷新
  refreshInterval = setInterval(() => {
    if (tasks.value.some(t => t.status === 'running')) {
      fetchTasks()
    }
  }, 5000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})

async function fetchTasks() {
  await taskStore.fetchTasks({
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value
  })
}

function handleRefresh() {
  fetchTasks()
}

function handlePageChange(page) {
  currentPage.value = page
  fetchTasks()
}

function handleView(task) {
  router.push(`/task/${task.id}`)
}

async function handleRun(task) {
  try {
    await taskStore.runTask(task.id)
    ElMessage.success('任务已启动')
    router.push(`/task/${task.id}`)
  } catch (error) {
    console.error('启动任务失败:', error)
  }
}

async function handleCancel(task) {
  try {
    await ElMessageBox.confirm('确定要取消该任务吗？', '提示', {
      type: 'warning'
    })
    await taskStore.cancelTask(task.id)
    ElMessage.success('任务已取消')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消任务失败:', error)
    }
  }
}

async function handleDelete(task) {
  try {
    await ElMessageBox.confirm('确定要删除该任务吗？此操作不可恢复', '警告', {
      type: 'warning'
    })
    await taskStore.deleteTask(task.id)
    ElMessage.success('任务已删除')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除任务失败:', error)
    }
  }
}

async function handleRerun(task) {
  try {
    await ElMessageBox.confirm('确定要重新执行该任务吗？将清除之前的执行结果', '提示', {
      type: 'info'
    })
    await taskStore.rerunTask(task.id)
    ElMessage.success('任务已重新启动')
    router.push(`/task/${task.id}`)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重新执行任务失败:', error)
    }
  }
}

function getStatusClass(status) {
  const map = {
    pending: 'status-pending',
    running: 'status-running',
    completed: 'status-completed',
    failed: 'status-failed',
    cancelled: 'status-cancelled'
  }
  return map[status] || ''
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
</script>

<style scoped>
.task-list-card {
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
  font-size: 18px;
  font-weight: 600;
  color: #e0e0e0;
}

.header-icon {
  font-size: 24px;
}

.empty-state {
  padding: 40px 0;
}

.task-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.task-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(100, 180, 255, 0.3);
  transform: translateX(4px);
}

.task-status {
  flex-shrink: 0;
}

.status-dot {
  display: block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-pending {
  background: #909399;
}

.status-running {
  background: #409eff;
  animation: pulse 1.5s infinite;
}

.status-completed {
  background: #67c23a;
}

.status-failed {
  background: #f56c6c;
}

.status-cancelled {
  background: #e6a23c;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.task-content {
  flex: 1;
  min-width: 0;
}

.task-name {
  font-size: 15px;
  font-weight: 500;
  color: #e0e0e0;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #808080;
}

.task-status-text {
  flex-shrink: 0;
}

.task-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>

