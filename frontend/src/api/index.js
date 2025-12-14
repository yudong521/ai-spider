import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 从 localStorage 获取系统密钥并附加到请求头
    const secretKey = localStorage.getItem('system_secret_key')
    if (secretKey) {
      config.headers['X-Secret-Key'] = secretKey
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    
    // 处理 204 No Content 或空响应
    if (!res) {
      return null
    }
    
    // code !== 0 表示业务错误
    if (res.code !== 0) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    return res.data
  },
  error => {
    console.error('响应错误:', error)
    
    // 处理 401 未授权错误
    if (error.response && error.response.status === 401) {
      // 清除无效的密钥
      localStorage.removeItem('system_secret_key')
      
      // 检查当前路径，避免在登录页面重复跳转
      if (window.location.pathname !== '/login') {
        ElMessage.error('访问未授权，请重新输入密钥')
        // 跳转到登录页面
        window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`
      }
      return Promise.reject(error)
    }
    
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request
