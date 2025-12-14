<template>
  <div class="home-page">
    <header class="page-header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-icon">🕷️</span>
          <h1>智能爬虫 Agent</h1>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
          <router-link to="/settings">
            <el-button text size="large">
              <el-icon><Setting /></el-icon>
              设置
            </el-button>
          </router-link>
        </div>
      </div>
    </header>
    
    <main class="page-main">
      <div class="main-content">
        <!-- 任务统计卡片 -->
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon">📋</div>
            <div class="stat-info">
              <div class="stat-value">{{ total }}</div>
              <div class="stat-label">任务总数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-info">
              <div class="stat-value completed">{{ completedCount }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-info">
              <div class="stat-value running">{{ runningCount }}</div>
              <div class="stat-label">执行中</div>
            </div>
          </div>
        </div>
        
        <!-- 任务列表 -->
        <div class="task-section">
          <div class="section-header">
            <h2>
              <el-icon><List /></el-icon>
              任务列表
            </h2>
            <el-button text @click="handleRefresh" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
          
          <div v-if="tasks.length === 0" class="empty-state">
            <el-empty description="暂无任务">
              <el-button type="primary" @click="showCreateDialog = true">
                <el-icon><Plus /></el-icon>
                创建第一个任务
              </el-button>
            </el-empty>
          </div>
          
          <div v-else class="task-grid">
            <div 
              v-for="task in tasks" 
              :key="task.id" 
              class="task-card"
              @click="handleViewTask(task)"
            >
              <div class="card-header">
                <div class="task-status">
                  <span class="status-dot" :class="getStatusClass(task.status)"></span>
                  <el-tag :type="getStatusType(task.status)" size="small" effect="dark">
                    {{ getStatusText(task.status) }}
                  </el-tag>
                  <el-tooltip v-if="task.schedule_enabled" content="已启用定时执行" placement="top">
                    <el-tag size="small" type="success" class="schedule-tag">
                      <el-icon><AlarmClock /></el-icon>
                      定时
                    </el-tag>
                  </el-tooltip>
                </div>
                <el-dropdown trigger="click" @click.stop @command="handleCommand($event, task)">
                  <el-button text size="small" @click.stop>
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit">
                        <el-icon><Edit /></el-icon>
                        编辑任务
                      </el-dropdown-item>
                      <el-dropdown-item command="run" :disabled="task.status === 'running'">
                        <el-icon><VideoPlay /></el-icon>
                        立即执行
                      </el-dropdown-item>
                      <el-dropdown-item command="delete" divided>
                        <el-icon><Delete /></el-icon>
                        删除任务
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
              
              <div class="card-body">
                <h3 class="task-name">{{ task.name }}</h3>
                <p class="task-description">{{ task.description }}</p>
              </div>
              
              <div class="card-footer">
                <div class="task-meta">
                  <el-tag size="small" type="info">{{ task.model }}</el-tag>
                  <span class="execution-count">
                    <el-icon><Timer /></el-icon>
                    {{ task.execution_count }} 次执行
                  </span>
                </div>
                <span class="task-time">{{ formatTime(task.created_at) }}</span>
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
        </div>
      </div>
    </main>
    
    <footer class="page-footer">
      <p>基于 LLM 的智能爬虫系统 · 自然语言驱动 · 全程可观测</p>
    </footer>
    
    <!-- 新建/编辑任务弹窗 -->
    <TaskDialog 
      v-model="showCreateDialog" 
      :task="editingTask"
      @success="handleTaskSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Setting, 
  List, 
  Plus, 
  Refresh, 
  MoreFilled, 
  Edit, 
  VideoPlay, 
  Delete,
  Timer,
  AlarmClock
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import { formatRelativeTime } from '@/utils/time'
import TaskDialog from '@/components/TaskDialog.vue'

const router = useRouter()
const taskStore = useTaskStore()

const showCreateDialog = ref(false)
const editingTask = ref(null)
const currentPage = ref(1)
const pageSize = ref(12)
let refreshInterval = null

const tasks = computed(() => taskStore.tasks)
const total = computed(() => taskStore.total)
const loading = computed(() => taskStore.loading)

const completedCount = computed(() => 
  tasks.value.filter(t => t.status === 'completed').length
)
const runningCount = computed(() => 
  tasks.value.filter(t => t.status === 'running').length
)

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

function handleViewTask(task) {
  router.push(`/task/${task.id}`)
}

async function handleCommand(command, task) {
  switch (command) {
    case 'edit':
      editingTask.value = task
      showCreateDialog.value = true
      break
    case 'run':
      await handleRunTask(task)
      break
    case 'delete':
      await handleDeleteTask(task)
      break
  }
}

async function handleRunTask(task) {
  try {
    const execution = await taskStore.createExecution(task.id)
    ElMessage.success('任务已启动')
    router.push(`/task/${task.id}/execution/${execution.id}`)
  } catch (error) {
    console.error('启动任务失败:', error)
  }
}

async function handleDeleteTask(task) {
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

function handleTaskSuccess() {
  editingTask.value = null
  fetchTasks()
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
.home-page {
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

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 36px;
}

.logo h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #64b5f6, #42a5f5, #1e88e5);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-main {
  flex: 1;
  padding: 32px 24px;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  transition: all 0.2s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.12);
}

.stat-icon {
  font-size: 32px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #e0e0e0;
}

.stat-value.completed {
  color: #67c23a;
}

.stat-value.running {
  color: #409eff;
}

.stat-label {
  font-size: 13px;
  color: #808080;
}

/* 任务区域 */
.task-section {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #e0e0e0;
}

.empty-state {
  padding: 60px 0;
}

/* 任务卡片网格 */
.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.task-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.task-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(100, 180, 255, 0.3);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.task-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-pending { background: #909399; }
.status-running { background: #409eff; animation: pulse 1.5s infinite; }
.status-completed { background: #67c23a; }
.status-failed { background: #f56c6c; }
.status-cancelled { background: #e6a23c; }

.schedule-tag {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.card-body {
  margin-bottom: 16px;
}

.task-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #e0e0e0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-description {
  margin: 0;
  font-size: 13px;
  color: #909090;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.execution-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #707070;
}

.task-time {
  font-size: 12px;
  color: #606060;
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

.page-footer {
  padding: 24px;
  text-align: center;
  color: #505050;
  font-size: 13px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .task-grid {
    grid-template-columns: 1fr;
  }
}
</style>
