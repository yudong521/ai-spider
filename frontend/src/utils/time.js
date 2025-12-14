/**
 * 时间处理工具函数
 * 后端返回的时间是 UTC 时间但没有带时区标识，需要手动处理
 */

/**
 * 解析后端返回的时间字符串为 Date 对象
 * @param {string|Date} time - 时间字符串或 Date 对象
 * @returns {Date|null} - Date 对象
 */
export function parseTime(time) {
  if (!time) return null
  if (time instanceof Date) return time
  
  // 如果时间字符串不包含时区信息，添加 Z 表示 UTC
  if (typeof time === 'string' && !time.endsWith('Z') && !time.includes('+') && !time.includes('-', 10)) {
    time = time + 'Z'
  }
  return new Date(time)
}

/**
 * 格式化时间为相对时间（如：刚刚、5分钟前、2小时前）
 * @param {string|Date} time - 时间
 * @returns {string} - 相对时间字符串
 */
export function formatRelativeTime(time) {
  if (!time) return ''
  const date = parseTime(time)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  
  return date.toLocaleDateString('zh-CN')
}

/**
 * 格式化时间为完整的日期时间字符串
 * @param {string|Date} time - 时间
 * @returns {string} - 格式化后的时间字符串
 */
export function formatDateTime(time) {
  if (!time) return '-'
  return parseTime(time).toLocaleString('zh-CN')
}

/**
 * 计算两个时间之间的持续时间
 * @param {string|Date} startTime - 开始时间
 * @param {string|Date} endTime - 结束时间
 * @returns {string} - 持续时间字符串
 */
export function formatDuration(startTime, endTime) {
  if (!startTime || !endTime) return '-'
  const start = parseTime(startTime)
  const end = parseTime(endTime)
  const diff = end - start
  
  if (diff < 1000) return '< 1秒'
  if (diff < 60000) return `${Math.floor(diff / 1000)} 秒`
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分 ${Math.floor((diff % 60000) / 1000)} 秒`
  return `${Math.floor(diff / 3600000)} 小时 ${Math.floor((diff % 3600000) / 60000)} 分`
}

