<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <!-- Logo 区域 -->
        <div class="logo-section">
          <div class="logo-icon">
            <img src="/spider.svg" alt="Logo" />
          </div>
          <h1 class="logo-title">智能爬虫 Agent</h1>
          <p class="logo-subtitle">请输入系统访问密钥</p>
        </div>
        
        <!-- 表单区域 -->
        <div class="form-section">
          <el-form 
            ref="formRef"
            :model="form" 
            :rules="rules"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="secretKey">
              <el-input
                v-model="form.secretKey"
                :type="showKey ? 'text' : 'password'"
                placeholder="请输入访问密钥"
                size="large"
                clearable
                @keyup.enter="handleLogin"
              >
                <template #prefix>
                  <el-icon><Key /></el-icon>
                </template>
                <template #suffix>
                  <el-icon 
                    class="toggle-visibility" 
                    @click="showKey = !showKey"
                  >
                    <View v-if="!showKey" />
                    <Hide v-else />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                size="large" 
                :loading="loading"
                class="login-btn"
                @click="handleLogin"
              >
                <el-icon v-if="!loading"><Unlock /></el-icon>
                {{ loading ? '验证中...' : '进入系统' }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 提示信息 -->
        <div class="tips-section">
          <el-icon><InfoFilled /></el-icon>
          <span>密钥由系统管理员在设置页面配置</span>
        </div>
      </div>
      
      <!-- 装饰元素 -->
      <div class="decoration">
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
        <div class="circle circle-3"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Key, View, Hide, Unlock, InfoFilled } from '@element-plus/icons-vue'
import { verifySecretKey, getAuthStatus } from '@/api/configs'

const router = useRouter()
const route = useRoute()
const formRef = ref(null)
const loading = ref(false)
const showKey = ref(false)

const form = reactive({
  secretKey: ''
})

const rules = {
  secretKey: [
    { required: true, message: '请输入访问密钥', trigger: 'blur' }
  ]
}

onMounted(async () => {
  // 检查是否需要认证
  try {
    const status = await getAuthStatus()
    if (!status.required) {
      // 不需要认证，直接跳转
      const redirect = route.query.redirect || '/'
      router.replace(redirect)
    }
  } catch (error) {
    console.error('检查认证状态失败:', error)
  }
})

async function handleLogin() {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  
  loading.value = true
  
  try {
    const result = await verifySecretKey(form.secretKey)
    
    if (result.valid) {
      // 存储密钥到 localStorage
      localStorage.setItem('system_secret_key', form.secretKey)
      ElMessage.success('验证成功')
      
      // 跳转到目标页面
      const redirect = route.query.redirect || '/'
      router.replace(redirect)
    } else {
      ElMessage.error('密钥无效，请重新输入')
    }
  } catch (error) {
    ElMessage.error('验证失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
  position: relative;
  overflow: hidden;
}

.login-container {
  position: relative;
  z-index: 1;
}

.login-card {
  width: 400px;
  padding: 48px 40px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  backdrop-filter: blur(20px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.logo-section {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.logo-icon img {
  width: 48px;
  height: 48px;
  filter: brightness(0) invert(1);
}

.logo-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px;
  letter-spacing: 1px;
}

.logo-subtitle {
  font-size: 14px;
  color: #808080;
  margin: 0;
}

.form-section {
  margin-bottom: 24px;
}

.form-section :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 4px 16px;
}

.form-section :deep(.el-input__wrapper:hover) {
  border-color: rgba(255, 255, 255, 0.2);
}

.form-section :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
}

.form-section :deep(.el-input__inner) {
  color: #fff;
  font-size: 15px;
}

.form-section :deep(.el-input__inner::placeholder) {
  color: #606060;
}

.form-section :deep(.el-input__prefix),
.form-section :deep(.el-input__suffix) {
  color: #606060;
}

.toggle-visibility {
  cursor: pointer;
  transition: color 0.2s;
}

.toggle-visibility:hover {
  color: #667eea;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

.login-btn:active {
  transform: translateY(0);
}

.tips-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
  color: #606060;
}

.tips-section .el-icon {
  font-size: 14px;
}

/* 装饰元素 */
.decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.circle-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  right: -100px;
  animation: float 8s ease-in-out infinite;
}

.circle-2 {
  width: 300px;
  height: 300px;
  bottom: -50px;
  left: -50px;
  animation: float 10s ease-in-out infinite reverse;
}

.circle-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  left: 10%;
  animation: float 12s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-30px) scale(1.05);
  }
}

/* 响应式 */
@media (max-width: 480px) {
  .login-card {
    width: 90%;
    max-width: 360px;
    padding: 32px 24px;
  }
  
  .logo-icon {
    width: 64px;
    height: 64px;
  }
  
  .logo-icon img {
    width: 36px;
    height: 36px;
  }
  
  .logo-title {
    font-size: 22px;
  }
}
</style>

