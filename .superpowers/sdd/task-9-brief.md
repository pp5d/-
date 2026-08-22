### Task 9: 用户管理页（管理员）

**Files:**
- Create: `frontend/src/views/admin/Users.vue`
- Modify: `frontend/src/router/index.js`（`admin/users` 指向 Users.vue）

**Interfaces:**
- Consumes: 后端 `GET /api/users`、`POST /api/users?role=...`、`PATCH /api/users/{id}`（Task 5）；`useAuthStore.isAdmin`。
- Produces: 管理员页面：用户表格、新建用户对话框、禁用/启用、改角色、改分组。

- [ ] **Step 1: 创建 src/views/admin/Users.vue**

```vue
<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openCreate">新建用户</el-button>
    </div>
    <el-table :data="users" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="phone" label="手机号" />
      <el-table-column prop="role" label="角色" width="110" />
      <el-table-column prop="group_name" label="分组" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="230">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" :type="row.is_active ? 'danger' : 'success'" @click="toggleActive(row)">
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" :title="editing ? '编辑用户' : '新建用户'" width="420px">
      <el-form label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" :disabled="!!editing" />
        </el-form-item>
        <el-form-item v-if="!editing" label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option label="工程师" value="engineer" />
            <el-option label="售后/试机" value="support" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="分组">
          <el-input v-model="form.group_name" placeholder="如：售后二部" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const users = ref([])
const dialog = ref(false)
const editing = ref(null)
const form = ref({ username: '', password: '', role: 'support', group_name: '' })

async function load() {
  users.value = await http.get('/users')
}

function openCreate() {
  editing.value = null
  form.value = { username: '', password: '', role: 'support', group_name: '' }
  dialog.value = true
}

function openEdit(row) {
  editing.value = row
  form.value = { username: row.username, password: '', role: row.role, group_name: row.group_name }
  dialog.value = true
}

async function save() {
  if (editing.value) {
    const body = { role: form.value.role, group_name: form.value.group_name }
    await http.patch(`/users/${editing.value.id}`, body)
  } else {
    await http.post(`/users?role=${form.value.role}`, {
      username: form.value.username,
      password: form.value.password
    })
  }
  ElMessage.success('已保存')
  dialog.value = false
  load()
}

async function toggleActive(row) {
  await http.patch(`/users/${row.id}`, { is_active: !row.is_active })
  ElMessage.success(row.is_active ? '已禁用' : '已启用')
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; }
</style>
```

- [ ] **Step 2: 更新路由指向真实页面**

在 `src/router/index.js` 中把 `{ path: 'admin/users', component: () => import('../views/Placeholder.vue'), meta: { roles: ['admin'] } }` 改为：

```js
{ path: 'admin/users', component: () => import('../views/admin/Users.vue'), meta: { roles: ['admin'] } }
```

- [ ] **Step 3: 手动验证**

Run: `cd frontend && npm run dev`
用 admin 账号登录（后端 `APP_MODE=full` 时通过 API 创建：`POST /api/users?role=admin`，可用 PowerShell `Invoke-RestMethod` 先登录再创建）。
Expected: 用户表格展示、新建/禁用/启用/改角色全部生效。

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/admin frontend/src/router/index.js
git commit -m "feat: 用户管理页面"
```

---
---


