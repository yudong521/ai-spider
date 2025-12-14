import request from './index'

/**
 * 获取任务最新执行的 Token 统计
 */
export function getTaskTokenStats(taskId) {
  return request({
    url: `/stats/tasks/${taskId}/token-stats`,
    method: 'get'
  })
}

/**
 * 获取指定执行记录的 Token 统计
 */
export function getExecutionTokenStats(executionId) {
  return request({
    url: `/stats/executions/${executionId}/token-stats`,
    method: 'get'
  })
}

/**
 * 获取总体统计
 */
export function getOverviewStats() {
  return request({
    url: '/stats/overview',
    method: 'get'
  })
}
