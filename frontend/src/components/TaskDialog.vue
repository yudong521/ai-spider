<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑任务' : '新建任务'"
    width="680px"
    :close-on-click-modal="false"
    @close="handleClose"
    class="task-dialog"
  >
    <el-form 
      ref="formRef" 
      :model="form" 
      :rules="rules" 
      label-position="top"
      class="task-form"
    >
      <el-form-item label="任务名称" prop="name">
        <el-input 
          v-model="form.name" 
          placeholder="例如：GitHub热门AI项目"
          clearable
        />
      </el-form-item>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="主Agent模型" prop="model">
            <el-select v-model="form.model" placeholder="选择模型" style="width: 100%">
              <el-option 
                v-for="model in models" 
                :key="model.key" 
                :label="model.name" 
                :value="model.key"
              >
                <div class="model-option">
                  <span>{{ model.name }}</span>
                  <el-tag size="small" type="info">{{ model.provider }}</el-tag>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="提取Agent模型" prop="extract_model">
            <el-select v-model="form.extract_model" placeholder="选择模型" style="width: 100%">
              <el-option 
                v-for="model in models" 
                :key="model.key" 
                :label="model.name" 
                :value="model.key"
              >
                <div class="model-option">
                  <span>{{ model.name }}</span>
                  <el-tag size="small" type="info">{{ model.provider }}</el-tag>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="任务描述" prop="description">
        <el-input 
          v-model="form.description" 
          type="textarea" 
          :rows="3"
          placeholder="详细描述你想要爬取的信息，例如：获取GitHub上今日热门的AI Agent相关项目，包含名称、Star数、简介、README详情"
        />
      </el-form-item>
      
      <el-form-item label="入口 URL" prop="entry_urls">
        <el-input 
          v-model="form.entry_urls" 
          type="textarea" 
          :rows="2"
          placeholder="输入爬取入口URL，多个URL请换行分隔"
        />
      </el-form-item>
      
      <el-collapse v-model="showAdvanced" class="advanced-config">
        <el-collapse-item name="advanced">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span style="margin-left: 8px">高级配置</span>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="最大爬取页面数">
                <el-input-number v-model="form.config.max_pages" :min="1" :max="100" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="超时时间(秒)">
                <el-input-number v-model="form.config.timeout" :min="60" :max="1800" :step="60" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="主Agent温度">
                <el-slider v-model="form.config.main_temperature" :min="0" :max="1" :step="0.1" show-input />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="提取Agent温度">
                <el-slider v-model="form.config.extract_temperature" :min="0" :max="1" :step="0.1" show-input />
              </el-form-item>
            </el-col>
          </el-row>
        </el-collapse-item>
        
        <!-- 定时执行配置 -->
        <el-collapse-item name="schedule">
          <template #title>
            <el-icon><Timer /></el-icon>
            <span style="margin-left: 8px">定时执行</span>
          </template>
          
          <el-form-item>
            <el-switch 
              v-model="form.schedule_enabled" 
              active-text="启用定时执行"
              inactive-text="手动执行"
            />
          </el-form-item>
          
          <template v-if="form.schedule_enabled">
            <el-form-item label="执行方式">
              <el-radio-group v-model="form.schedule_type">
                <el-radio value="interval">间隔执行</el-radio>
                <el-radio value="cron">定时执行</el-radio>
                <el-radio value="once">单次执行</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <!-- 间隔执行配置 -->
            <el-form-item v-if="form.schedule_type === 'interval'" label="执行间隔">
              <el-input-number 
                v-model="form.schedule_config.interval_minutes" 
                :min="1" 
                :max="1440"
                :step="5"
              />
              <span style="margin-left: 8px; color: #909399">分钟</span>
            </el-form-item>
            
            <!-- 定时执行配置 (cron) -->
            <template v-if="form.schedule_type === 'cron'">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="执行时间">
                    <el-time-select
                      v-model="cronTime"
                      start="00:00"
                      step="00:30"
                      end="23:30"
                      placeholder="选择时间"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="执行日期">
                    <el-select 
                      v-model="form.schedule_config.cron_day_of_week" 
                      placeholder="选择日期"
                      style="width: 100%"
                    >
                      <el-option label="每天" value="*" />
                      <el-option label="工作日 (周一至周五)" value="mon,tue,wed,thu,fri" />
                      <el-option label="周末 (周六、周日)" value="sat,sun" />
                      <el-option label="周一" value="mon" />
                      <el-option label="周二" value="tue" />
                      <el-option label="周三" value="wed" />
                      <el-option label="周四" value="thu" />
                      <el-option label="周五" value="fri" />
                      <el-option label="周六" value="sat" />
                      <el-option label="周日" value="sun" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </template>
            
            <!-- 单次执行配置 -->
            <el-form-item v-if="form.schedule_type === 'once'" label="执行时间">
              <el-date-picker
                v-model="form.schedule_config.once_at"
                type="datetime"
                placeholder="选择日期时间"
                :disabled-date="disabledDate"
                style="width: 100%"
              />
            </el-form-item>
          </template>
        </el-collapse-item>
      </el-collapse>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '保存' : '创建任务' }}
        </el-button>
        <el-button 
          v-if="!isEdit" 
          type="success" 
          @click="handleSubmitAndRun" 
          :loading="submitting"
        >
          <el-icon><VideoPlay /></el-icon>
          创建并执行
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Setting, VideoPlay, Timer } from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import { useConfigStore } from '@/stores/config'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  task: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const router = useRouter()
const taskStore = useTaskStore()
const configStore = useConfigStore()

const formRef = ref()
const showAdvanced = ref([])
const submitting = ref(false)
const models = ref([])

const visible = ref(false)
const isEdit = ref(false)

const defaultConfig = {
  max_pages: 20,
  main_temperature: 0.5,
  extract_temperature: 0.0,
  timeout: 600
}

const defaultScheduleConfig = {
  interval_minutes: 60,
  cron_hour: 9,
  cron_minute: 0,
  cron_day_of_week: '*',
  once_at: null
}

const form = reactive({
  name: '',
  description: '',
  entry_urls: '',
  model: 'qwen3-max',
  extract_model: 'qwen3-max',
  config: { ...defaultConfig },
  schedule_enabled: false,
  schedule_type: 'interval',
  schedule_config: { ...defaultScheduleConfig }
})

// cron 时间的计算属性
const cronTime = computed({
  get() {
    const hour = String(form.schedule_config.cron_hour || 0).padStart(2, '0')
    const minute = String(form.schedule_config.cron_minute || 0).padStart(2, '0')
    return `${hour}:${minute}`
  },
  set(val) {
    if (val) {
      const [hour, minute] = val.split(':')
      form.schedule_config.cron_hour = parseInt(hour)
      form.schedule_config.cron_minute = parseInt(minute)
    }
  }
})

// 禁用过去的日期
function disabledDate(time) {
  return time.getTime() < Date.now()
}

const rules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入任务描述', trigger: 'blur' }
  ],
  entry_urls: [
    { required: true, message: '请输入入口URL', trigger: 'blur' }
  ],
  model: [
    { required: true, message: '请选择主Agent模型', trigger: 'change' }
  ],
  extract_model: [
    { required: true, message: '请选择提取Agent模型', trigger: 'change' }
  ]
}

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    initForm()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

onMounted(async () => {
  models.value = await configStore.fetchModels()
})

function initForm() {
  if (props.task) {
    isEdit.value = true
    form.name = props.task.name
    form.description = props.task.description
    form.entry_urls = props.task.entry_urls?.join('\n') || ''
    form.model = props.task.model
    form.extract_model = props.task.extract_model || props.task.model
    form.config = props.task.config ? { ...props.task.config } : { ...defaultConfig }
    
    // 定时配置
    form.schedule_enabled = props.task.schedule_enabled || false
    form.schedule_type = props.task.schedule_type || 'interval'
    form.schedule_config = props.task.schedule_config 
      ? { ...defaultScheduleConfig, ...props.task.schedule_config }
      : { ...defaultScheduleConfig }
  } else {
    isEdit.value = false
    resetForm()
  }
}

function resetForm() {
  form.name = ''
  form.description = ''
  form.entry_urls = ''
  form.model = 'qwen3-max'
  form.extract_model = 'qwen3-max'
  form.config = { ...defaultConfig }
  form.schedule_enabled = false
  form.schedule_type = 'interval'
  form.schedule_config = { ...defaultScheduleConfig }
  formRef.value?.resetFields()
}

function handleClose() {
  visible.value = false
  resetForm()
}

function buildTaskData() {
  const entry_urls = form.entry_urls
    .split('\n')
    .map(url => url.trim())
    .filter(url => url.length > 0)
  
  const taskData = {
    name: form.name,
    description: form.description,
    entry_urls,
    model: form.model,
    extract_model: form.extract_model,
    config: form.config,
    schedule_enabled: form.schedule_enabled,
    schedule_type: form.schedule_enabled ? form.schedule_type : null,
    schedule_config: form.schedule_enabled ? form.schedule_config : null
  }
  
  return taskData
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    const taskData = buildTaskData()
    
    if (isEdit.value) {
      await taskStore.updateTask(props.task.id, taskData)
      ElMessage.success('任务更新成功')
    } else {
      await taskStore.createTask(taskData)
      const msg = form.schedule_enabled ? '任务创建成功，已启用定时执行' : '任务创建成功'
      ElMessage.success(msg)
    }
    
    emit('success')
    handleClose()
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    submitting.value = false
  }
}

async function handleSubmitAndRun() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    const taskData = buildTaskData()
    
    // 创建任务
    const task = await taskStore.createTask(taskData)
    
    // 创建执行记录
    const execution = await taskStore.createExecution(task.id)
    
    ElMessage.success('任务创建成功，正在执行...')
    
    emit('success')
    handleClose()
    
    // 跳转到执行详情页
    router.push(`/task/${task.id}/execution/${execution.id}`)
  } catch (error) {
    console.error('创建任务失败:', error)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.task-dialog :deep(.el-dialog) {
  background: #1a1a2e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}

.task-dialog :deep(.el-dialog__header) {
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.task-dialog :deep(.el-dialog__title) {
  color: #e0e0e0;
  font-size: 18px;
  font-weight: 600;
}

.task-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.task-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.task-form {
  padding: 0;
}

.model-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.advanced-config {
  margin-top: 16px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.advanced-config :deep(.el-collapse-item__header) {
  background: transparent;
  color: #a0a0a0;
  border: none;
  padding: 12px 16px;
}

.advanced-config :deep(.el-collapse-item__content) {
  padding: 16px;
  background: rgba(0, 0, 0, 0.2);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

