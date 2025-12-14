<template>
  <el-card class="result-preview-card">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <span class="header-icon">📄</span>
          <span>执行结果</span>
        </div>
        <div class="header-actions" v-if="result">
          <el-button text size="small" @click="handleCopy">
            <el-icon><CopyDocument /></el-icon>
            复制
          </el-button>
          <el-button text size="small" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </div>
      </div>
    </template>
    
    <div class="result-content">
      <div v-if="status === 'pending'" class="status-message pending">
        <el-icon><Clock /></el-icon>
        <span>任务等待执行</span>
      </div>
      
      <div v-else-if="status === 'running'" class="status-message running">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>任务执行中，请稍候...</span>
      </div>
      
      <div v-else-if="status === 'failed'" class="status-message failed">
        <el-icon><CircleClose /></el-icon>
        <div class="error-info">
          <span>任务执行失败</span>
          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        </div>
      </div>
      
      <div v-else-if="status === 'cancelled'" class="status-message cancelled">
        <el-icon><WarningFilled /></el-icon>
        <span>任务已取消</span>
      </div>
      
      <div v-else-if="result" class="markdown-body" v-html="renderedResult"></div>
      
      <div v-else class="status-message empty">
        <el-icon><Document /></el-icon>
        <span>暂无结果</span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  CopyDocument, 
  Download, 
  Clock, 
  Loading, 
  CircleClose, 
  WarningFilled,
  Document 
} from '@element-plus/icons-vue'
import { marked } from 'marked'

const props = defineProps({
  result: {
    type: String,
    default: ''
  },
  status: {
    type: String,
    default: ''
  },
  errorMessage: {
    type: String,
    default: ''
  },
  taskName: {
    type: String,
    default: 'task'
  }
})

const renderedResult = computed(() => {
  if (!props.result) return ''
  return marked(props.result)
})

function handleCopy() {
  if (!props.result) return
  
  navigator.clipboard.writeText(props.result).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

function handleExport() {
  if (!props.result) return
  
  const blob = new Blob([props.result], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${props.taskName}-result.md`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('导出成功')
}
</script>

<style scoped>
.result-preview-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #e0e0e0;
}

.header-icon {
  font-size: 20px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.result-content {
  min-height: 200px;
}

.status-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 20px;
  color: #808080;
  font-size: 15px;
}

.status-message.pending {
  color: #909399;
}

.status-message.running {
  color: #409eff;
}

.status-message.failed {
  color: #f56c6c;
  flex-direction: column;
}

.status-message.cancelled {
  color: #e6a23c;
}

.error-info {
  text-align: center;
}

.error-message {
  margin-top: 8px;
  font-size: 13px;
  color: #909090;
  max-width: 400px;
}

/* Markdown 样式 */
.markdown-body {
  color: #c9d1d9;
  line-height: 1.8;
  font-size: 14px;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  color: #e0e0e0;
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
}

.markdown-body :deep(h1) {
  font-size: 24px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.markdown-body :deep(h2) {
  font-size: 20px;
}

.markdown-body :deep(h3) {
  font-size: 16px;
}

.markdown-body :deep(p) {
  margin-bottom: 16px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 24px;
  margin-bottom: 16px;
}

.markdown-body :deep(li) {
  margin-bottom: 8px;
}

.markdown-body :deep(code) {
  background: rgba(110, 118, 129, 0.4);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
}

.markdown-body :deep(pre) {
  background: rgba(0, 0, 0, 0.4);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 16px;
}

.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
}

.markdown-body :deep(blockquote) {
  border-left: 4px solid #409eff;
  padding-left: 16px;
  margin: 16px 0;
  color: #a0a0a0;
}

.markdown-body :deep(a) {
  color: #58a6ff;
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.markdown-body :deep(th) {
  background: rgba(255, 255, 255, 0.05);
  font-weight: 600;
}

.markdown-body :deep(hr) {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin: 24px 0;
}
</style>

