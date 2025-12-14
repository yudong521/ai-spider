import request from './index'

/**
 * 获取认证状态（是否需要密钥）
 */
export function getAuthStatus() {
  return request({
    url: '/configs/auth/status',
    method: 'get'
  })
}

/**
 * 验证系统密钥
 */
export function verifySecretKey(key) {
  return request({
    url: '/configs/auth/verify',
    method: 'post',
    data: { key }
  })
}

/**
 * 获取所有配置
 */
export function getConfigs() {
  return request({
    url: '/configs',
    method: 'get'
  })
}

/**
 * 获取配置项
 */
export function getConfig(key) {
  return request({
    url: `/configs/${key}`,
    method: 'get'
  })
}

/**
 * 更新配置项
 */
export function updateConfig(key, value) {
  return request({
    url: `/configs/${key}`,
    method: 'put',
    data: { value }
  })
}

/**
 * 测试 API Key
 */
export function testApiKey(provider) {
  return request({
    url: `/configs/api-key/${provider}/test`,
    method: 'get'
  })
}

/**
 * 获取可用模型列表
 */
export function getModels() {
  return request({
    url: '/configs/models/list',
    method: 'get'
  })
}

