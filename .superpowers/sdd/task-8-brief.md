### Task 8: 主布局（按模式渲染菜单）

**Files:**
- Create: `frontend/src/layouts/MainLayout.vue`
- Modify: `frontend/src/router/index.js`（Home 等页面挂到布局下）
- Create: `frontend/src/views/Dashboard.vue`

**Interfaces:**
- Consumes: Task 6 的 `useAppStore`（mode/isPublic/isFull）；Task 7 的 `useAuthStore`（user/isAdmin/isEngineer/logout）。
- Produces: 布局组件 `MainLayout.vue`（侧边菜单 + 顶栏用户区）；`/` 路由渲染 `Dashboard.vue`（欢迎页，显示当前模式与角色）。后续页面以子路由形式挂入布局。

- [ ] **Step 1: 创建 src/layouts/MainLayout.vue**

```vue
<template>
  <el-container style="min-height:100vh">
    <el-aside width="210px" class="aside">
      <div class="logo">注塑机智能问答</div>
      <el-menu :default-active="$route.path" router background-color="#001529" text-color="#a6adb4" active-text-color="#ffffff">
        <el-menu-item index="/"><el-icon><HomeFilled /></el-icon><span>首页</span></el-menu-item>
        <template v-if="app.isPublic">
          <el-menu-item index="/chat"><el-icon><ChatDotRound /></el-icon><span>智能问答</span></el-menu-item>
          <el-menu-item index="/knowledge"><el-icon><Reading /></el-icon><span>知识库</span></el-menu-item>
          <el-menu-item index="/tickets"><el-icon><Tickets /></el-icon><span>我的工单</span></el-menu-item>
        </template>
        <template v-else>
          <el-menu-item index="/chat"><el-icon><ChatDotRound /></el-icon><span>智能问答</span></el-menu-item>
          <el-menu-item index="/knowledge"><el-icon><Reading /></el-icon><span>知识库</span></el-menu-item>
          <el-menu-item index="/manage"><el-icon><Notebook /></el-icon><span>知识管理</span></el-menu-item>
          <el-menu-item index="/review"><el-icon><Checked /></el-icon><span>审核中心</span></el-menu-item>
          <el-menu-item index="/tickets"><el-icon><Tickets /></el-icon><span>工单处理</span></el-menu-item>
          <el-menu-item v-if="auth.isAdmin" index="/admin/users"><el-icon><User /></el-icon><span>用户管理</span></el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>{{ app.isPublic ? '公网门户（售后/试机）' : '内网系统（工程师）' }}</span>
        <el-dropdown @command="onCommand">
          <span class="user">{{ auth.user?.username }}（{{ auth.user?.role }}）<el-icon><ArrowDown /></el-icon></span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useAuthStore } from '../stores/auth'

const app = useAppStore()
const auth = useAuthStore()
const router = useRouter()

onMounted(() => { if (!app.mode) app.fetchHealth() })

function onCommand(cmd) {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.aside { background: #001529; }
.logo { color: #fff; font-size: 16px; font-weight: 600; text-align: center; padding: 18px 0; }
.header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e4e7ed; }
.user { cursor: pointer; display: flex; align-items: center; gap: 4px; }
</style>
```

- [ ] **Step 2: 创建 src/views/Dashboard.vue**

```vue
<template>
  <el-card>
    <h2>欢迎，{{ auth.user?.username }}</h2>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="系统模式">{{ app.isPublic ? '公网门户' : '内网系统' }}</el-descriptions-item>
      <el-descriptions-item label="角色">{{ auth.user?.role }}</el-descriptions-item>
      <el-descriptions-item label="说明">
        {{ app.isPublic ? '售后/试机人员入口：智能问答、知识库、我的工单。' : '工程师入口：知识管理、审核、工单处理。' }}
      </el-descriptions-item>
    </el-descriptions>
  </el-card>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import { useAuthStore } from '../stores/auth'

const app = useAppStore()
const auth = useAuthStore()
</script>
```

- [ ] **Step 3: 更新 src/router/index.js（布局嵌套 + 占位子页）**

```js
const routes = [
  { path: '/login', component: () => import('../views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('../views/Dashboard.vue') },
      { path: 'chat', component: () => import('../views/Placeholder.vue') },
      { path: 'knowledge', component: () => import('../views/Placeholder.vue') },
      { path: 'tickets', component: () => import('../views/Placeholder.vue') },
      { path: 'manage', component: () => import('../views/Placeholder.vue'), meta: { roles: ['engineer', 'admin'] } },
      { path: 'review', component: () => import('../views/Placeholder.vue'), meta: { roles: ['engineer', 'admin'] } },
      { path: 'admin/users', component: () => import('../views/Placeholder.vue'), meta: { roles: ['admin'] } }
    ]
  }
]
```

创建 `src/views/Placeholder.vue`：

```vue
<template>
  <el-empty description="该页面将在后续里程碑实现" />
</template>
```

- [ ] **Step 4: 手动验证布局**

Run: `cd frontend && npm run dev`
Expected: 登录后进入首页，左侧菜单按模式渲染；engineer 看不到"用户管理"；未登录访问 /chat 跳登录。

- [ ] **Step 5: Commit**

```bash
git add frontend/src
git commit -m "feat: 主布局与按模式菜单"
```

---
---


