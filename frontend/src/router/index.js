import { createRouter, createWebHistory } from 'vue-router'
import { getAuthStatus, verifySecretKey } from '@/api/configs'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/task/:id',
    name: 'TaskDetail',
    component: () => import('@/views/TaskDetail.vue'),
    meta: { title: '任务详情' }
  },
  {
    path: '/task/:taskId/execution/:executionId',
    name: 'ExecutionDetail',
    component: () => import('@/views/ExecutionDetail.vue'),
    meta: { title: '执行详情' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: '设置' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 认证状态缓存
let authStatusCache = null
let cacheTime = 0
const CACHE_DURATION = 5000 // 5秒缓存

async function checkAuthRequired() {
  const now = Date.now()
  if (authStatusCache !== null && (now - cacheTime) < CACHE_DURATION) {
    return authStatusCache
  }
  
  try {
    const status = await getAuthStatus()
    authStatusCache = status.required
    cacheTime = now
    return authStatusCache
  } catch (error) {
    console.error('检查认证状态失败:', error)
    return false
  }
}

async function validateStoredKey() {
  const storedKey = localStorage.getItem('system_secret_key')
  if (!storedKey) return false
  
  try {
    const result = await verifySecretKey(storedKey)
    return result.valid
  } catch (error) {
    console.error('验证存储密钥失败:', error)
    return false
  }
}

// 路由守卫 - 认证检查和页面标题更新
router.beforeEach(async (to, from, next) => {
  // 更新页面标题
  document.title = `${to.meta.title || '页面'} - 智能爬虫 Agent`
  
  // 公开页面直接放行
  if (to.meta.public) {
    next()
    return
  }
  
  // 检查是否需要认证
  const authRequired = await checkAuthRequired()
  
  if (!authRequired) {
    // 不需要认证，直接放行
    next()
    return
  }
  
  // 需要认证，检查本地存储的密钥
  const isValid = await validateStoredKey()
  
  if (isValid) {
    next()
  } else {
    // 清除无效密钥
    localStorage.removeItem('system_secret_key')
    // 重定向到登录页
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  }
})

// 清除认证缓存的函数（供外部调用）
export function clearAuthCache() {
  authStatusCache = null
  cacheTime = 0
}

export default router
