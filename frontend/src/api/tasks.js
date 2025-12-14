import request from './index'

/**
 * 创建任务
 */
export function createTask(data) {
  return request({
    url: '/tasks',
    method: 'post',
    data
  })
}

/**
 * 获取任务列表
 */
export function getTasks(params = {}) {
  return request({
    url: '/tasks',
    method: 'get',
    params
  })
}

/**
 * 获取任务详情
 */
export function getTask(taskId) {
  return request({
    url: `/tasks/${taskId}`,
    method: 'get'
  })
}

/**
 * 更新任务
 */
export function updateTask(taskId, data) {
  return request({
    url: `/tasks/${taskId}`,
    method: 'put',
    data
  })
}

/**
 * 删除任务
 */
export function deleteTask(taskId) {
  return request({
    url: `/tasks/${taskId}`,
    method: 'delete'
  })
}

// ============ 执行记录相关 ============

/**
 * 获取任务的执行记录列表
 */
export function getExecutions(taskId, params = {}) {
  return request({
    url: `/tasks/${taskId}/executions`,
    method: 'get',
    params
  })
}

/**
 * 获取执行记录详情
 */
export function getExecution(taskId, executionId) {
  return request({
    url: `/tasks/${taskId}/executions/${executionId}`,
    method: 'get'
  })
}

/**
 * 创建新的执行记录并启动执行
 */
export function createExecution(taskId) {
  return request({
    url: `/tasks/${taskId}/executions`,
    method: 'post'
  })
}

/**
 * 取消执行
 */
export function cancelExecution(taskId, executionId) {
  return request({
    url: `/tasks/${taskId}/executions/${executionId}/cancel`,
    method: 'post'
  })
}

// ============ 日志相关 ============

/**
 * 获取任务最新执行的日志
 */
export function getTaskLogs(taskId) {
  return request({
    url: `/tasks/${taskId}/logs`,
    method: 'get'
  })
}

/**
 * 获取指定执行记录的日志
 */
export function getExecutionLogs(taskId, executionId) {
  return request({
    url: `/tasks/${taskId}/executions/${executionId}/logs`,
    method: 'get'
  })
}

/**
 * 创建执行记录的 SSE 日志流连接
 * @param {string} taskId 任务ID
 * @param {string} executionId 执行记录ID
 * @param {object} handlers 事件处理器 { onStep, onComplete, onTimeout, onError }
 * @returns {EventSource} SSE 连接实例
 */
export function createExecutionLogStream(taskId, executionId, handlers = {}) {
  // EventSource 不支持自定义请求头，需要通过 URL query 参数传递密钥
  const secretKey = localStorage.getItem('system_secret_key')
  const url = `/api/tasks/${taskId}/executions/${executionId}/logs/stream${secretKey ? `?key=${encodeURIComponent(secretKey)}` : ''}`
  const eventSource = new EventSource(url)
  
  eventSource.addEventListener('step', (event) => {
    const data = JSON.parse(event.data)
    handlers.onStep?.(data)
  })
  
  eventSource.addEventListener('complete', (event) => {
    const data = JSON.parse(event.data)
    handlers.onComplete?.(data)
    eventSource.close()
  })
  
  eventSource.addEventListener('timeout', (event) => {
    const data = JSON.parse(event.data)
    handlers.onTimeout?.(data)
    eventSource.close()
  })
  
  eventSource.onerror = (error) => {
    handlers.onError?.(error)
    eventSource.close()
  }
  
  return eventSource
}

/**
 * 创建 SSE 日志流连接（旧版，基于task）
 * @deprecated 使用 createExecutionLogStream 代替
 */
export function createLogStream(taskId, handlers = {}) {
  // EventSource 不支持自定义请求头，需要通过 URL query 参数传递密钥
  const secretKey = localStorage.getItem('system_secret_key')
  const url = `/api/tasks/${taskId}/logs/stream${secretKey ? `?key=${encodeURIComponent(secretKey)}` : ''}`
  const eventSource = new EventSource(url)
  
  eventSource.addEventListener('step', (event) => {
    const data = JSON.parse(event.data)
    handlers.onStep?.(data)
  })
  
  eventSource.addEventListener('complete', (event) => {
    const data = JSON.parse(event.data)
    handlers.onComplete?.(data)
    eventSource.close()
  })
  
  eventSource.addEventListener('timeout', (event) => {
    const data = JSON.parse(event.data)
    handlers.onTimeout?.(data)
    eventSource.close()
  })
  
  eventSource.onerror = (error) => {
    handlers.onError?.(error)
    eventSource.close()
  }
  
  return eventSource
}
