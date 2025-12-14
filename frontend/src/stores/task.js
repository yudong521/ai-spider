import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  createTask as apiCreateTask, 
  getTasks as apiGetTasks, 
  getTask as apiGetTask,
  updateTask as apiUpdateTask,
  deleteTask as apiDeleteTask,
  getExecutions as apiGetExecutions,
  getExecution as apiGetExecution,
  createExecution as apiCreateExecution,
  cancelExecution as apiCancelExecution,
  getTaskLogs as apiGetTaskLogs,
  getExecutionLogs as apiGetExecutionLogs
} from '@/api/tasks'

export const useTaskStore = defineStore('task', () => {
  // 状态
  const tasks = ref([])
  const total = ref(0)
  const currentTask = ref(null)
  const currentExecution = ref(null)
  const currentLogs = ref([])
  const loading = ref(false)
  
  // 计算属性
  const runningTasks = computed(() => 
    tasks.value.filter(t => t.status === 'running')
  )
  
  const completedTasks = computed(() => 
    tasks.value.filter(t => t.status === 'completed')
  )
  
  // ============ 任务相关方法 ============
  
  async function fetchTasks(params = { skip: 0, limit: 20 }) {
    loading.value = true
    try {
      const data = await apiGetTasks(params)
      tasks.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }
  
  async function fetchTask(taskId) {
    loading.value = true
    try {
      currentTask.value = await apiGetTask(taskId)
      return currentTask.value
    } finally {
      loading.value = false
    }
  }
  
  async function createTask(data) {
    const task = await apiCreateTask(data)
    // 刷新列表
    await fetchTasks()
    return task
  }
  
  async function updateTask(taskId, data) {
    const task = await apiUpdateTask(taskId, data)
    // 更新本地状态
    const index = tasks.value.findIndex(t => t.id === taskId)
    if (index !== -1) {
      tasks.value[index] = task
    }
    if (currentTask.value?.id === taskId) {
      currentTask.value = task
    }
    return task
  }
  
  async function deleteTask(taskId) {
    await apiDeleteTask(taskId)
    // 从列表中移除
    tasks.value = tasks.value.filter(t => t.id !== taskId)
    total.value -= 1
    if (currentTask.value?.id === taskId) {
      currentTask.value = null
    }
  }
  
  // ============ 执行记录相关方法 ============
  
  async function fetchExecutions(taskId, params = { skip: 0, limit: 20 }) {
    const data = await apiGetExecutions(taskId, params)
    return data
  }
  
  async function fetchExecution(taskId, executionId) {
    currentExecution.value = await apiGetExecution(taskId, executionId)
    return currentExecution.value
  }
  
  async function createExecution(taskId) {
    const execution = await apiCreateExecution(taskId)
    
    // 更新任务状态
    const index = tasks.value.findIndex(t => t.id === taskId)
    if (index !== -1) {
      tasks.value[index].status = 'running'
      tasks.value[index].execution_count += 1
      tasks.value[index].last_execution_id = execution.id
    }
    if (currentTask.value?.id === taskId) {
      currentTask.value.status = 'running'
      currentTask.value.execution_count += 1
      currentTask.value.last_execution_id = execution.id
    }
    
    return execution
  }
  
  async function cancelExecution(taskId, executionId) {
    const execution = await apiCancelExecution(taskId, executionId)
    
    // 更新任务状态
    const index = tasks.value.findIndex(t => t.id === taskId)
    if (index !== -1) {
      tasks.value[index].status = 'cancelled'
    }
    if (currentTask.value?.id === taskId) {
      currentTask.value.status = 'cancelled'
    }
    if (currentExecution.value?.id === executionId) {
      currentExecution.value = execution
    }
    
    return execution
  }
  
  // ============ 日志相关方法 ============
  
  async function fetchTaskLogs(taskId) {
    const data = await apiGetTaskLogs(taskId)
    currentLogs.value = data.items
    return data.items
  }
  
  async function fetchExecutionLogs(taskId, executionId) {
    const data = await apiGetExecutionLogs(taskId, executionId)
    currentLogs.value = data.items
    return data.items
  }
  
  function addLog(log) {
    // 用于 SSE 实时添加日志
    const exists = currentLogs.value.find(l => l.step === log.step)
    if (!exists) {
      currentLogs.value.push(log)
    }
  }
  
  function clearCurrentTask() {
    currentTask.value = null
    currentExecution.value = null
    currentLogs.value = []
  }
  
  return {
    // 状态
    tasks,
    total,
    currentTask,
    currentExecution,
    currentLogs,
    loading,
    // 计算属性
    runningTasks,
    completedTasks,
    // 任务方法
    fetchTasks,
    fetchTask,
    createTask,
    updateTask,
    deleteTask,
    // 执行记录方法
    fetchExecutions,
    fetchExecution,
    createExecution,
    cancelExecution,
    // 日志方法
    fetchTaskLogs,
    fetchExecutionLogs,
    addLog,
    clearCurrentTask
  }
})
