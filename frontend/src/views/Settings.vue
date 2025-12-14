<template>
  <div class="settings-page">
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <el-button text @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <h1>系统设置</h1>
        </div>
      </div>
    </header>
    
    <main class="page-main">
      <div class="main-content">
        <div class="section-title">
          <span class="section-icon">🔑</span>
          <span>API 密钥配置</span>
        </div>
        
        <div class="api-cards-grid">
          <!-- 阿里千问 API Key 配置 -->
          <el-card class="api-card dashscope-card">
            <div class="api-card-header">
              <div class="provider-logo dashscope-logo">
                <span class="logo-text">阿里千问</span>
              </div>
              <el-tag type="info" size="small" effect="plain">DashScope</el-tag>
            </div>
            
            <div class="api-card-body">
              <div class="model-list">
                <span class="model-label">支持模型</span>
                <div class="model-tags">
                  <el-tag size="small" effect="plain">qwen3-max</el-tag>
                  <el-tag size="small" effect="plain">qwen-turbo</el-tag>
                </div>
              </div>
              
              <div class="api-input-group">
                <label class="input-label">API Key</label>
                <el-input 
                  v-model="apiKeys.dashscope_api_key" 
                  :type="showKeys.dashscope ? 'text' : 'password'"
                  placeholder="请输入阿里千问 API Key"
                  clearable
                  size="large"
                >
                  <template #suffix>
                    <el-icon 
                      class="input-icon" 
                      @click="showKeys.dashscope = !showKeys.dashscope"
                    >
                      <View v-if="!showKeys.dashscope" />
                      <Hide v-else />
                    </el-icon>
                  </template>
                </el-input>
              </div>
            </div>
            
            <div class="api-card-footer">
              <el-button 
                type="primary" 
                :loading="saving.dashscope"
                @click="handleSaveKey('dashscope_api_key')"
                class="save-btn"
              >
                <el-icon><Check /></el-icon>
                保存配置
              </el-button>
            </div>
          </el-card>
          
          <!-- 智谱 AI API Key 配置 -->
          <el-card class="api-card zhipu-card">
            <div class="api-card-header">
              <div class="provider-logo zhipu-logo">
                <span class="logo-text">智谱 AI</span>
              </div>
              <el-tag type="info" size="small" effect="plain">ZhipuAI</el-tag>
            </div>
            
            <div class="api-card-body">
              <div class="model-list">
                <span class="model-label">支持模型</span>
                <div class="model-tags">
                  <el-tag size="small" effect="plain">glm-4.6</el-tag>
                  <el-tag size="small" effect="plain">glm-4-flash</el-tag>
                </div>
              </div>
              
              <div class="api-input-group">
                <label class="input-label">API Key</label>
                <el-input 
                  v-model="apiKeys.zhipu_api_key" 
                  :type="showKeys.zhipu ? 'text' : 'password'"
                  placeholder="请输入智谱 API Key"
                  clearable
                  size="large"
                >
                  <template #suffix>
                    <el-icon 
                      class="input-icon" 
                      @click="showKeys.zhipu = !showKeys.zhipu"
                    >
                      <View v-if="!showKeys.zhipu" />
                      <Hide v-else />
                    </el-icon>
                  </template>
                </el-input>
              </div>
            </div>
            
            <div class="api-card-footer">
              <el-button 
                type="primary" 
                :loading="saving.zhipu"
                @click="handleSaveKey('zhipu_api_key')"
                class="save-btn"
              >
                <el-icon><Check /></el-icon>
                保存配置
              </el-button>
            </div>
          </el-card>
        </div>
        
        <!-- 系统安全配置 -->
        <div class="section-title" style="margin-top: 16px;">
          <span class="section-icon">🔐</span>
          <span>系统安全配置</span>
        </div>
        
        <el-card class="api-card security-card">
          <div class="api-card-header">
            <div class="provider-logo security-logo">
              <span class="logo-text">访问密钥</span>
            </div>
            <el-tag 
              :type="systemSecretKey ? 'success' : 'info'" 
              size="small" 
              effect="plain"
            >
              {{ systemSecretKey ? '已启用' : '未启用' }}
            </el-tag>
          </div>
          
          <div class="api-card-body">
            <div class="security-description">
              <p>设置系统访问密钥后，用户需要输入正确的密钥才能访问系统。</p>
              <p class="warning-text">⚠️ 修改密钥后需要重新登录系统。</p>
            </div>
            
            <div class="api-input-group">
              <label class="input-label">系统密钥</label>
              <el-input 
                v-model="apiKeys.system_secret_key" 
                :type="showKeys.system ? 'text' : 'password'"
                placeholder="留空表示不启用访问控制"
                clearable
                size="large"
              >
                <template #suffix>
                  <el-icon 
                    class="input-icon" 
                    @click="showKeys.system = !showKeys.system"
                  >
                    <View v-if="!showKeys.system" />
                    <Hide v-else />
                  </el-icon>
                </template>
              </el-input>
            </div>
          </div>
          
          <div class="api-card-footer">
            <el-button 
              type="primary" 
              :loading="saving.system"
              @click="handleSaveSystemKey"
              class="save-btn"
            >
              <el-icon><Check /></el-icon>
              保存配置
            </el-button>
          </div>
        </el-card>
        
        <!-- 系统信息 -->
        <el-card class="settings-card system-info-card">
          <template #header>
            <div class="card-header">
              <span class="header-icon">ℹ️</span>
              <span>系统信息</span>
            </div>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="版本">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="后端状态">
              <el-tag :type="backendStatus ? 'success' : 'danger'" size="small">
                {{ backendStatus ? '在线' : '离线' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="技术栈">Vue 3 + FastAPI + LangChain</el-descriptions-item>
            <el-descriptions-item label="数据库">SQLite</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, View, Hide, Check } from '@element-plus/icons-vue'
import { useConfigStore } from '@/stores/config'
import { clearAuthCache } from '@/router/index'
import request from '@/api/index'

const router = useRouter()
const configStore = useConfigStore()

const backendStatus = ref(false)

const apiKeys = reactive({
  dashscope_api_key: '',
  zhipu_api_key: '',
  system_secret_key: ''
})

const showKeys = reactive({
  dashscope: false,
  zhipu: false,
  system: false
})

const saving = reactive({
  dashscope: false,
  zhipu: false,
  system: false
})

// 计算系统密钥是否已设置
const systemSecretKey = computed(() => !!apiKeys.system_secret_key)

onMounted(async () => {
  // 检查后端状态
  try {
    await request.get('/health', { baseURL: '' })
    backendStatus.value = true
  } catch {
    backendStatus.value = false
  }
  
  // 加载配置
  await configStore.fetchConfigs()
  
  // 填充表单
  apiKeys.dashscope_api_key = configStore.getConfigValue('dashscope_api_key')
  apiKeys.zhipu_api_key = configStore.getConfigValue('zhipu_api_key')
  apiKeys.system_secret_key = configStore.getConfigValue('system_secret_key')
})

function goBack() {
  router.push('/')
}

async function handleSaveKey(key) {
  const provider = key.includes('dashscope') ? 'dashscope' : 'zhipu'
  saving[provider] = true
  
  try {
    await configStore.updateConfig(key, apiKeys[key])
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving[provider] = false
  }
}

async function handleSaveSystemKey() {
  const newKey = apiKeys.system_secret_key
  const oldKey = configStore.getConfigValue('system_secret_key')
  
  // 如果密钥有变化，提示用户
  if (newKey !== oldKey) {
    try {
      await ElMessageBox.confirm(
        newKey 
          ? '修改系统密钥后，您需要使用新密钥重新登录。确定要修改吗？'
          : '清空系统密钥后，任何人都可以访问系统。确定要清空吗？',
        '安全提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      // 用户取消操作
      return
    }
  }
  
  saving.system = true
  
  try {
    await configStore.updateConfig('system_secret_key', newKey)
    ElMessage.success('保存成功')
    
    // 清除认证缓存
    clearAuthCache()
    
    // 如果修改了密钥，更新本地存储并重新登录
    if (newKey !== oldKey) {
      if (newKey) {
        // 更新本地存储的密钥
        localStorage.setItem('system_secret_key', newKey)
      } else {
        // 清空密钥
        localStorage.removeItem('system_secret_key')
      }
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.system = false
  }
}
</script>

<style scoped>
.settings-page {
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
  max-width: 1000px;
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

.header-left h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #e0e0e0;
}

.page-main {
  flex: 1;
  padding: 32px 24px;
}

.main-content {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
  color: #e0e0e0;
  margin-bottom: 8px;
}

.section-icon {
  font-size: 24px;
}

.api-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

@media (max-width: 768px) {
  .api-cards-grid {
    grid-template-columns: 1fr;
  }
}

.api-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.api-card:hover {
  border-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.api-card :deep(.el-card__body) {
  padding: 0;
}

.api-card-header {
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.dashscope-card .api-card-header {
  background: linear-gradient(135deg, rgba(255, 106, 0, 0.1) 0%, rgba(255, 165, 0, 0.05) 100%);
}

.zhipu-card .api-card-header {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1) 0%, rgba(100, 200, 255, 0.05) 100%);
}

.provider-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.dashscope-logo .logo-text {
  background: linear-gradient(135deg, #ff6a00, #ffa500);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.zhipu-logo .logo-text {
  background: linear-gradient(135deg, #409eff, #64c8ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.api-card-body {
  padding: 20px 24px;
}

.model-list {
  margin-bottom: 20px;
}

.model-label {
  display: block;
  font-size: 12px;
  color: #808080;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.model-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.model-tags .el-tag {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: #a0a0a0;
}

.api-input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  font-size: 13px;
  font-weight: 500;
  color: #b0b0b0;
}

.api-input-group :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.api-input-group :deep(.el-input__wrapper:hover) {
  border-color: rgba(255, 255, 255, 0.15);
}

.api-input-group :deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
}

.input-icon {
  cursor: pointer;
  color: #808080;
  transition: color 0.2s;
}

.input-icon:hover {
  color: #409eff;
}

.api-card-footer {
  padding: 16px 24px 20px;
  display: flex;
  justify-content: flex-end;
}

.save-btn {
  padding: 10px 24px;
  border-radius: 10px;
  font-weight: 500;
}

.dashscope-card .save-btn {
  background: linear-gradient(135deg, #ff6a00, #ff8c00);
  border: none;
}

.dashscope-card .save-btn:hover {
  background: linear-gradient(135deg, #ff7a10, #ff9c10);
}

.zhipu-card .save-btn {
  background: linear-gradient(135deg, #409eff, #5ab0ff);
  border: none;
}

.zhipu-card .save-btn:hover {
  background: linear-gradient(135deg, #50aeff, #6ac0ff);
}

.security-card .api-card-header {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.1) 0%, rgba(144, 238, 144, 0.05) 100%);
}

.security-logo .logo-text {
  background: linear-gradient(135deg, #67c23a, #95d475);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.security-card .save-btn {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  border: none;
}

.security-card .save-btn:hover {
  background: linear-gradient(135deg, #77d24a, #95de71);
}

.security-description {
  margin-bottom: 20px;
}

.security-description p {
  margin: 0 0 8px;
  font-size: 13px;
  color: #909090;
  line-height: 1.6;
}

.security-description .warning-text {
  color: #e6a23c;
  font-size: 12px;
}

.settings-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
}

.system-info-card {
  margin-top: 8px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #e0e0e0;
}

.header-icon {
  font-size: 22px;
}
</style>

