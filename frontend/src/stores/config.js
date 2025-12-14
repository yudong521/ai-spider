import { defineStore } from 'pinia'
import { ref } from 'vue'
import { 
  getConfigs as apiGetConfigs, 
  updateConfig as apiUpdateConfig,
  testApiKey as apiTestApiKey,
  getModels as apiGetModels
} from '@/api/configs'

export const useConfigStore = defineStore('config', () => {
  // 状态
  const configs = ref([])
  const models = ref([])
  const loading = ref(false)
  
  // 方法
  async function fetchConfigs() {
    loading.value = true
    try {
      configs.value = await apiGetConfigs()
    } finally {
      loading.value = false
    }
  }
  
  async function updateConfig(key, value) {
    const updated = await apiUpdateConfig(key, value)
    // 更新本地状态
    const index = configs.value.findIndex(c => c.key === key)
    if (index !== -1) {
      configs.value[index] = updated
    }
    return updated
  }
  
  async function testApiKey(provider) {
    const result = await apiTestApiKey(provider)
    return result.valid
  }
  
  async function fetchModels() {
    models.value = await apiGetModels()
    return models.value
  }
  
  function getConfigValue(key) {
    const config = configs.value.find(c => c.key === key)
    return config?.value || ''
  }
  
  return {
    // 状态
    configs,
    models,
    loading,
    // 方法
    fetchConfigs,
    updateConfig,
    testApiKey,
    fetchModels,
    getConfigValue
  }
})

