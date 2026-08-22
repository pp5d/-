### Task 6: 前端骨架（Vite + Vue3 + Element Plus）

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/api/http.js`
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/stores/app.js`

**Interfaces:**
- Consumes: 后端 `GET /api/health`（返回 mode）。
- Produces: 前端开发服务器 `http://localhost:5173`，Vite 代理 `/api → http://localhost:8000`；`src/api/http.js` 默认导出 axios 实例（自动带 Bearer token，401 时清 token 跳登录，错误弹 ElMessage）；`src/stores/app.js` 的 `useAppStore`（state: `mode` 默认 `""`，action: `fetchHealth()`）；路由表 `src/router/index.js`。

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "aiqa-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@element-plus/icons-vue": "^2.3.1",
    "axios": "^1.7.9",
    "element-plus": "^2.9.1",
    "markdown-it": "^14.1.0",
    "pinia": "^2.3.0",
    "vue": "^3.5.13",
    "vue-router": "^4.5.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.1",
    "vite": "^5.4.11"
  }
}
```

- [ ] **Step 2: 创建 vite.config.js**

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: { '/api': 'http://localhost:8000' }
  }
})
```

- [ ] **Step 3: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>注塑机智能问答</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 4: 创建 src/main.js**

```js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import * as Icons from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
for (const [name, comp] of Object.entries(Icons)) app.component(name, comp)
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })
app.mount('#app')
```

- [ ] **Step 5: 创建 src/App.vue**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 6: 创建 src/api/http.js（axios 实例，含认证拦截）**

```js
import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({ baseURL: '/api', timeout: 30000 })

http.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const status = err.response?.status
    const detail = err.response?.data?.detail
    if (status === 401) {
      localStorage.removeItem('token')
      if (!location.pathname.startsWith('/login')) location.href = '/login'
    } else {
      ElMessage.error(typeof detail === 'string' ? detail : '网络错误，请稍后重试')
    }
    return Promise.reject(err)
  }
)

export default http
```

- [ ] **Step 7: 创建 src/stores/app.js（mode 默认空串，避免守卫失效）**

```js
import { defineStore } from 'pinia'
import http from '../api/http'

export const useAppStore = defineStore('app', {
  state: () => ({ mode: '' }),
  getters: {
    isPublic: (s) => s.mode === 'public',
    isFull: (s) => s.mode === 'full'
  },
  actions: {
    async fetchHealth() {
      const r = await http.get('/health')
      this.mode = r.mode
    }
  }
})
```

- [ ] **Step 8: 创建 src/router/index.js（暂含占位路由，Task 7 补守卫）**

```js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('../views/Home.vue') }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
```

创建占位页 `frontend/src/views/Home.vue`：

```vue
<template>
  <el-result icon="success" title="AIQA 骨架已就绪" sub-title="M1 项目骨架运行正常" />
</template>
```

- [ ] **Step 9: 安装依赖并验证**

Run: `cd frontend && npm install`
Run: `npm run dev`
浏览器打开 http://localhost:5173，Expected: 显示"AIQA 骨架已就绪"。

- [ ] **Step 10: Commit**

```bash
git add frontend/
git commit -m "feat: 前端骨架"
```

---
---


