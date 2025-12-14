# 智能爬虫 Agent - 前端

基于 Vue 3 + Element Plus 的智能爬虫 Agent 系统前端界面。

## 技术栈

- **Vue 3** - 核心框架
- **Vite** - 构建工具
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP 请求

## 功能特性

- 🎯 **任务管理** - 创建、执行、取消、删除爬虫任务
- 📊 **实时监控** - SSE 实时日志流，Token 消耗统计
- 🎨 **深色主题** - 精心设计的深色 UI，支持 Element Plus Dark 模式
- 📄 **结果预览** - Markdown 渲染，支持复制和导出
- ⚙️ **配置管理** - API Key 配置、模型选择

## 目录结构

```
src/
├── api/                 # API 调用层
│   ├── index.js         # axios 实例
│   ├── tasks.js         # 任务 API
│   ├── configs.js       # 配置 API
│   └── stats.js         # 统计 API
├── components/          # 组件
│   ├── TaskForm.vue     # 任务创建表单
│   ├── TaskList.vue     # 任务列表
│   ├── LogViewer.vue    # 实时日志查看器
│   ├── TokenStats.vue   # Token 统计面板
│   └── ResultPreview.vue # 结果预览
├── views/               # 页面
│   ├── Home.vue         # 首页
│   ├── TaskDetail.vue   # 任务详情
│   └── Settings.vue     # 设置页
├── stores/              # Pinia 状态管理
│   ├── task.js          # 任务状态
│   └── config.js        # 配置状态
├── router/              # 路由配置
├── styles/              # 全局样式
├── App.vue
└── main.js
```

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

默认运行在 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

## 配置说明

### Vite 代理配置

开发环境下，API 请求会自动代理到后端服务器：

```js
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

确保后端服务运行在 `http://localhost:8000`。

## 页面说明

### 首页 (/)

- 任务创建表单：输入任务名称、描述、入口 URL、选择模型
- 高级配置：最大爬取深度、页面数、Agent 温度等
- 任务列表：显示所有任务，支持状态筛选

### 任务详情 (/task/:id)

- Token 统计：输入/输出 Token 数量、费用估算
- 执行日志：SSE 实时推送，显示每一步执行过程
- 结果预览：Markdown 渲染，支持复制和导出

### 设置 (/settings)

- API Key 配置：阿里千问、智谱 AI
- 连接测试：验证 API Key 是否有效
- 默认配置：默认模型、爬取深度等

## 与后端 API 对接

| 前端方法 | 后端接口 | 说明 |
|---------|---------|------|
| `createTask()` | POST `/api/tasks` | 创建任务 |
| `getTasks()` | GET `/api/tasks` | 获取任务列表 |
| `getTask(id)` | GET `/api/tasks/{id}` | 获取任务详情 |
| `runTask(id)` | POST `/api/tasks/{id}/run` | 启动任务 |
| `cancelTask(id)` | POST `/api/tasks/{id}/cancel` | 取消任务 |
| `deleteTask(id)` | DELETE `/api/tasks/{id}` | 删除任务 |
| `streamLogs(id)` | GET `/api/tasks/{id}/logs/stream` | SSE 日志流 |
| `getTaskTokenStats(id)` | GET `/api/stats/tasks/{id}/token-stats` | Token 统计 |

