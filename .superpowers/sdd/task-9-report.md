# Task 9 报告：用户管理页（管理员）

- **状态**: DONE_WITH_CONCERNS
- **分支**: `feature/m1-foundation`
- **Commit**: `29782f9` — `feat: 用户管理页面`

## 执行步骤

### Step 1: 创建 `frontend/src/views/admin/Users.vue`
- 按简报代码**逐字**创建（模板 + `<script setup>` + scoped style，UTF-8）。
- 内容要点：用户表格（ID/用户名/手机号/角色/分组/状态/操作）、新建用户对话框、编辑角色/分组、禁用/启用切换；调用 `http.get('/users')`、`http.post('/users?role=...')`、`http.patch('/users/{id}')`；`onMounted(load)` 加载列表。

### Step 2: 更新路由
- `frontend/src/router/index.js` 第 16 行：`admin/users` 从 `() => import('../views/Placeholder.vue')` 改为 `() => import('../views/admin/Users.vue')`，`meta: { roles: ['admin'] }` 保持不变。

### Step 3: 静态编译验证（替代手动验证，见 Concerns）
由于沙箱禁止 esbuild spawn，`npm run dev`/`build` 无法执行，改用静态编译验证：

| 检查项 | 结果 |
|---|---|
| `node --check frontend/src/router/index.js` | OK（ESM 语法，package.json `"type": "module"`） |
| `@vue/compiler-sfc` `parse(Users.vue)` | OK，无解析错误 |
| `@vue/compiler-sfc` `compileScript(<script setup>)` | OK（编译产物再经 `node --check` 通过） |
| `@vue/compiler-sfc` `compileTemplate(<template>)` | OK，无模板编译错误 |
| import `../../api/http` 解析 | 命中 `frontend/src/api/http.js`（存在且为默认导出） |
| 路由 `../views/admin/Users.vue` 解析 | 目标文件存在 |
| 编码 | 两文件均为 UTF-8 无 BOM；git 提示 LF→CRLF 为仓库 autocrlf 常规警告 |

### Step 4: 提交
```
git add frontend/src/views/admin frontend/src/router/index.js
git commit -m "feat: 用户管理页面"
```
结果：`29782f9`，2 files changed, 107 insertions(+), 1 deletion(-)。仅包含简报指定的两个路径；`.superpowers/sdd/*` 下既有未跟踪文件未纳入提交。

## 验证结果
全部静态检查通过（详见上表）。功能层面的"表格展示 / 新建 / 禁用 / 启用 / 改角色 / 改分组"因无法启动前后端未做端到端验证。

## 问题 / 疑虑
1. **手动验证被静态验证替代**：沙箱限制导致 `npm run dev`/`build`（esbuild spawn）失败，浏览器端到端验证未执行；代码与后端接口（Task 5 的 `/api/users` 系列）的契约一致性未实测。
2. **`el-dialog` 使用 `v-model="dialog"`**：element-plus ≥ 2.x 支持 `v-model`（`modelValue`），项目依赖 `element-plus ^2.9.1`，兼容，无问题。
3. **新建用户只传 username/password，角色走 query**：与简报代码一致；`group_name` 在新建时未提交（后端默认或需后续补丁），这是简报既定行为，非本次改动引入。
4. **前端无单元测试**：项目未见测试框架配置，验证依赖静态编译 + 未来集成回归。
5. **git LF/CRLF 警告**：仓库 `core.autocrlf` 行为，不影响内容正确性。
