### Task 7: 前端认证（登录/注册 + 路由守卫）

**Files:**
- Create: `frontend/src/stores/auth.js`
- Create: `frontend/src/views/Login.vue`
- Modify: `frontend/src/router/index.js`
- （`frontend/src/api/http.js` 已在 Task 6 Step 6 创建，本任务直接使用）

**Interfaces:**
- Consumes: 后端 `POST /api/auth/login`、`POST /api/auth/register`、`GET /api/auth/me`；Task 4 的响应结构（Token/UserOut）；Task 6 的 `src/api/http.js`。
- Produces: `useAuthStore`（state: `token`/`user`；getters: `isAdmin`/`isEngineer`；actions: `login/register/fetchMe/logout`）；路由 `meta`：`{ public: true }` 免登录、`{ roles: [...] }` 限角色。

- [ ] **Step 1: 创建 src/stores/auth.js**

```js
import { defineStore } from 'pinia'
import http from '../api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null
  }),
  getters: {
    isAdmin: (s) => s.user?.role === 'admin',
    isEngineer: (s) => s.user && ['engineer', 'admin'].includes(s.user.role),
    isLoggedIn: (s) => !!s.token
  },
  actions: {
    setSession(r) {
      this.token = r.access_token
      this.user = r.user
      localStorage.setItem('token', r.access_token)
    },
    async login(username, password) {
      const r = await http.post('/auth/login', { username, password })
      this.setSession(r)
    },
    async register(username, password, phone) {
      const r = await http.post('/auth/register', { username, password, phone })
      this.setSession(r)
    },
    async fetchMe() {
      this.user = await http.get('/auth/me')
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
    }
  }
})
```

- [ ] **Step 2: 创建 src/views/Login.vue**

```vue
<template>
  <div class="login-wrap">
    <el-card class="login-card">
      <h2 style="text-align:center">注塑机上位机智能问答</h2>
      <el-tabs v-model="tab">
        <el-tab-pane label="登录" name="login">
          <el-form @submit.prevent="doLogin">
            <el-form-item><el-input v-model="form.username" placeholder="用户名" /></el-form-item>
            <el-form-item><el-input v-model="form.password" type="password" placeholder="密码" show-password /></el-form-item>
            <el-button type="primary" style="width:100%" :loading="loading" @click="doLogin">登 录</el-button>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form @submit.prevent="doRegister">
            <el-form-item><el-input v-model="form.username" placeholder="用户名" /></el-form-item>
            <el-form-item><el-input v-model="form.phone" placeholder="手机号" /></el-form-item>
            <el-form-item><el-input v-model="form.password" type="password" placeholder="密码（至少6位）" show-password /></el-form-item>
            <el-button type="primary" style="width:100%" :loading="loading" @click="doRegister">注 册</el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const tab = ref('login')
const form = ref({ username: '', password: '', phone: '' })
const loading = ref(false)
const auth = useAuthStore()
const router = useRouter()

async function doLogin() {
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    router.push('/')
  } finally {
    loading.value = false
  }
}

async function doRegister() {
  loading.value = true
  try {
    await auth.register(form.value.username, form.value.password, form.value.phone)
    ElMessage.success('注册成功')
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f5f7fa; }
.login-card { width: 380px; padding: 12px 8px; }
</style>
```

- [ ] **Step 3: 更新 src/router/index.js（含守卫）**

```js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', component: () => import('../views/Login.vue'), meta: { public: true } },
  { path: '/', component: () => import('../views/Home.vue') }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.public) return true
  if (!auth.token) return '/login'
  if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      return '/login'
    }
  }
  if (to.meta.roles && !to.meta.roles.includes(auth.user.role)) return '/'
  return true
})

export default router
```

- [ ] **Step 4: 手动验证登录流程**

Run: `cd backend && uvicorn app.main:app --reload --port 8000`（确保 backend/.env 存在且 `alembic upgrade head` 已执行）
Run: `cd frontend && npm run dev`

验证方式：以公网模式临时启动后端注册测试账号——
1. 停掉后端，执行 `$env:APP_MODE="public"; uvicorn app.main:app --port 8000`（PowerShell 环境变量方式，不改 .env 文件）
2. 浏览器打开 http://localhost:5173 → 注册一个账号（角色自动为 support）→ 自动登录进入首页
3. 停掉后端，恢复正常启动（full 模式）
Expected: 未登录访问 `/` 跳转 `/login`；注册后自动登录进入首页；刷新页面保持登录态；重启后端后 token 仍有效。

- [ ] **Step 5: Commit**

```bash
git add frontend/src
git commit -m "feat: 前端登录注册与路由守卫"
```

---
---


