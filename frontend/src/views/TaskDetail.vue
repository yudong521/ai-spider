<template>
  <div class="task-detail-page">
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <el-button text @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <div class="task-info" v-if="task">
            <h1>{{ task.name }}</h1>
            <el-tag :type="getStatusType(task.status)" effect="dark">
              {{ getStatusText(task.status) }}
            </el-tag>
          </div>
        </div>
        <div class="header-actions" v-if="task">
          <el-button @click="handleEdit">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button 
            type="primary"
            @click="handleNewExecution"
            :disabled="task.status === 'running'"
          >
            <el-icon><VideoPlay /></el-icon>
            新建执行
          </el-button>
        </div>
      </div>
    </header>
    
    <main class="page-main" v-if="task">
      <div class="main-content">
        <div class="detail-layout">
          <!-- 左侧：任务信息 -->
          <div class="task-info-section">
            <el-card class="info-card">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">📝</span>
                  <span>任务信息</span>
                </div>
              </template>
              
              <div class="info-content">
                <div class="info-item">
                  <label>任务ID</label>
                  <span class="value monospace">{{ task.id }}</span>
                </div>
                
                <div class="info-item">
                  <label>主Agent模型</label>
                  <el-tag size="small">{{ task.model }}</el-tag>
                </div>
                
                <div class="info-item">
                  <label>提取Agent模型</label>
                  <el-tag size="small" type="info">{{ task.extract_model || task.model }}</el-tag>
                </div>
                
                <div class="info-item">
                  <label>创建时间</label>
                  <span class="value">{{ formatTime(task.created_at) }}</span>
                </div>
                
                <div class="info-item">
                  <label>执行次数</label>
                  <span class="value highlight">{{ task.execution_count }} 次</span>
                </div>
                
                <el-divider />
                
                <div class="info-item full">
                  <label>任务描述</label>
                  <p class="description">{{ task.description }}</p>
                </div>
                
                <div class="info-item full">
                  <label>入口 URL</label>
                  <ul class="url-list">
                    <li v-for="url in task.entry_urls" :key="url">
                      <a :href="url" target="_blank">{{ url }}</a>
                    </li>
                  </ul>
                </div>
                
                <el-collapse v-if="task.config" class="config-collapse">
                  <el-collapse-item name="config">
                    <template #title>
                      <el-icon><Setting /></el-icon>
                      <span style="margin-left: 8px">高级配置</span>
                    </template>
                    <div class="config-grid">
                      <div class="config-item">
                        <span class="label">最大页面数</span>
                        <span class="value">{{ task.config.max_pages }}</span>
                      </div>
                      <div class="config-item">
                        <span class="label">超时时间</span>
                        <span class="value">{{ task.config.timeout }}秒</span>
                      </div>
                      <div class="config-item">
                        <span class="label">主Agent温度</span>
                        <span class="value">{{ task.config.main_temperature }}</span>
                      </div>
                    </div>
                  </el-collapse-item>
                </el-collapse>
                
                <!-- 定时执行信息 -->
                <div class="schedule-section" v-if="task.schedule_enabled">
                  <el-divider />
                  <div class="schedule-header">
                    <el-icon><Timer /></el-icon>
                    <span>定时执行</span>
                    <el-tag size="small" type="success">已启用</el-tag>
                  </div>
                  <div class="schedule-info">
                    <div class="schedule-item">
                      <span class="label">执行方式</span>
                      <span class="value">{{ getScheduleTypeText(task.schedule_type) }}</span>
                    </div>
                    <div class="schedule-item">
                      <span class="label">执行计划</span>
                      <span class="value">{{ getScheduleDescription(task) }}</span>
                    </div>
                    <div class="schedule-item" v-if="task.next_run_at">
                      <span class="label">下次执行</span>
                      <span class="value highlight">{{ formatTime(task.next_run_at) }}</span>
                    </div>
                    <div class="schedule-item" v-if="task.last_scheduled_at">
                      <span class="label">上次定时执行</span>
                      <span class="value">{{ formatTime(task.last_scheduled_at) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 右侧：执行历史 -->
          <div class="execution-history-section">
            <ExecutionList 
              ref="executionListRef"
              :task-id="task.id" 
              @new-execution="handleNewExecution"
            />
          </div>
        </div>
      </div>
    </main>
    
    <div v-else class="loading-page">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
    
    <!-- 编辑任务弹窗 -->
    <TaskDialog 
      v-model="showEditDialog" 
      :task="task"
      @success="handleEditSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, 
  VideoPlay,
  Edit,
  Loading,
  Setting,
  Timer
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import { formatDateTime } from '@/utils/time'
import ExecutionList from '@/components/ExecutionList.vue'
import TaskDialog from '@/components/TaskDialog.vue'

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()

const task = ref(null)
const showEditDialog = ref(false)
const executionListRef = ref(null)
let refreshInterval = null

onMounted(async () => {
  const taskId = route.params.id
  task.value = await taskStore.fetchTask(taskId)
  
  // 如果任务正在执行，定期刷新状态
  if (task.value?.status === 'running') {
    startRefresh()
  }
})

onUnmounted(() => {
  stopRefresh()
})

function startRefresh() {
  refreshInterval = setInterval(async () => {
    const taskId = route.params.id
    task.value = await taskStore.fetchTask(taskId)
    
    if (task.value?.status !== 'running') {
      stopRefresh()
    }
  }, 5000)
}

function stopRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

function goBack() {
  router.push('/')
}

function handleEdit() {
  showEditDialog.value = true
}

async function handleEditSuccess() {
  // 刷新任务信息
  const taskId = route.params.id
  task.value = await taskStore.fetchTask(taskId)
}

async function handleNewExecution() {
  try {
    const execution = await taskStore.createExecution(task.value.id)
    ElMessage.success('执行已启动')
    
    // 刷新执行历史
    executionListRef.value?.refresh()
    
    // 更新任务状态
    task.value = await taskStore.fetchTask(task.value.id)
    startRefresh()
    
    // 跳转到执行详情页
    router.push(`/task/${task.value.id}/execution/${execution.id}`)
  } catch (error) {
    console.error('创建执行失败:', error)
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
  return formatDateTime(time)
}

function getScheduleTypeText(type) {
  const map = {
    interval: '间隔执行',
    cron: '定时执行',
    once: '单次执行'
  }
  return map[type] || type
}

function getScheduleDescription(task) {
  if (!task.schedule_config) return '-'
  
  const config = task.schedule_config
  
  if (task.schedule_type === 'interval') {
    return `每 ${config.interval_minutes} 分钟执行一次`
  }
  
  if (task.schedule_type === 'cron') {
    const hour = String(config.cron_hour || 0).padStart(2, '0')
    const minute = String(config.cron_minute || 0).padStart(2, '0')
    const dayText = getDayOfWeekText(config.cron_day_of_week)
    return `${dayText} ${hour}:${minute} 执行`
  }
  
  if (task.schedule_type === 'once') {
    return config.once_at ? `${formatDateTime(config.once_at)} 执行一次` : '-'
  }
  
  return '-'
}

function getDayOfWeekText(dayOfWeek) {
  if (!dayOfWeek || dayOfWeek === '*') return '每天'
  
  const dayMap = {
    'mon': '周一',
    'tue': '周二',
    'wed': '周三',
    'thu': '周四',
    'fri': '周五',
    'sat': '周六',
    'sun': '周日'
  }
  
  if (dayOfWeek === 'mon,tue,wed,thu,fri') return '工作日'
  if (dayOfWeek === 'sat,sun') return '周末'
  
  const days = dayOfWeek.split(',').map(d => dayMap[d.trim()] || d).join('、')
  return days
}
</script>

<style scoped>
.task-detail-page {
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

.task-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-info h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #e0e0e0;
}

.header-actions {
  display: flex;
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

.detail-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 24px;
}

/* 任务信息卡片 */
.info-card {
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

.info-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-item.full {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.info-item label {
  font-size: 13px;
  color: #808080;
}

.info-item .value {
  font-size: 14px;
  color: #c0c0c0;
}

.info-item .value.monospace {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 12px;
}

.info-item .value.highlight {
  color: #409eff;
  font-weight: 600;
}

.description {
  margin: 0;
  font-size: 14px;
  color: #b0b0b0;
  line-height: 1.6;
}

.url-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.url-list li {
  margin-bottom: 6px;
}

.url-list a {
  color: #58a6ff;
  text-decoration: none;
  font-size: 13px;
  word-break: break-all;
}

.url-list a:hover {
  text-decoration: underline;
}

.config-collapse {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.config-collapse :deep(.el-collapse-item__header) {
  background: transparent;
  color: #a0a0a0;
  border: none;
  padding: 12px 16px;
}

.config-collapse :deep(.el-collapse-item__content) {
  padding: 16px;
  background: rgba(0, 0, 0, 0.2);
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.config-item .label {
  font-size: 11px;
  color: #707070;
}

.config-item .value {
  font-size: 14px;
  color: #c0c0c0;
}

/* 定时执行信息 */
.schedule-section {
  margin-top: 8px;
}

.schedule-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #a0a0a0;
  margin-bottom: 12px;
}

.schedule-header .el-icon {
  color: #67c23a;
}

.schedule-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  background: rgba(103, 194, 58, 0.08);
  border: 1px solid rgba(103, 194, 58, 0.2);
  border-radius: 8px;
}

.schedule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.schedule-item .label {
  font-size: 12px;
  color: #808080;
}

.schedule-item .value {
  font-size: 13px;
  color: #c0c0c0;
}

.schedule-item .value.highlight {
  color: #67c23a;
  font-weight: 600;
}

/* 执行历史区域 */
.execution-history-section {
  min-height: 400px;
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
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
