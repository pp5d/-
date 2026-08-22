# Task 7 报告：前端认证（登录/注册 + 路由守卫）

- **状态**：DONE_WITH_CONCERNS
- **Commit**：`2ade4f95a9775b279e023b24708f289b19f73dfe`（message: `feat: 前端登录注册与路由守卫`，分支 `feature/m1-foundation`）
- **改动文件**：新增 `frontend/src/stores/auth.js`、`frontend/src/views/Login.vue`；修改 `frontend/src/router/index.js`（3 files changed, +120 / -3）

---

## 一、执行步骤

按简报 Step 1 → Step 5 逐字照做（代码与简报完全一致）：

### Step 1：创建 `frontend/src/stores/auth.js`
- Pinia `useAuthStore`：state `token`（初始化自 `localStorage`）/`user`；getters `isAdmin`/`isEngineer`/`isLoggedIn`；actions `setSession/login/register/fetchMe/logout`。
- 复用 Task 6 的 `src/api/http.js`（未重复创建）；`http` 拦截器已返回 `res.data`（即后端响应体），故 `login` 中 `r.access_token`、`r.user` 直接对应 Task 4 的 Token/UserOut 结构。

### Step 2：创建 `frontend/src/views/Login.vue`
- 登录/注册双 Tab（`el-tabs`），`el-form @submit.prevent` + 按钮 `@click`，`loading` 防重复提交，成功后 `ElMessage.success` 并 `router.push('/')`。

### Step 3：更新 `frontend/src/router/index.js`
- 新增 `/login` 路由（`meta: { public: true }`，懒加载 `Login.vue`）；`/` 指向 `Home.vue`。
- `beforeEach` 守卫：public 路由放行 → 无 token 跳 `/login` → 有 token 无 user 时 `fetchMe()`（失败跳 `/login`）→ `meta.roles` 角色校验（不匹配跳 `/`）。

### Step 4：静态编译验证（替代浏览器手动验证）
沙箱禁止 esbuild 子进程 spawn，`npm run dev`/`npm run build` 无法执行，故采用下述静态验证（结果见下节）。

### Step 5：Commit
`git add frontend/src && git commit -m "feat: 前端登录注册与路由守卫"`，仅提交 `frontend/src` 下 3 个文件（`.superpowers/sdd` 下文件保持未跟踪）。

---

## 二、静态验证方法与结果

验证环境：Node v24.16.0（`frontend/node_modules` 为 Task 6 已装依赖，未执行 npm install）。

1. **ESM 语法检查**：用 `node:vm` 的 `SourceTextModule` 对 `frontend/src` 下全部 `.js`（main.js / api/http.js / router/index.js / stores/app.js / stores/auth.js）做 ESM 语法解析 → 全部通过。
2. **SFC 编译检查**：用 `@vue/compiler-sfc` 的 `parse` + `compileTemplate` + `compileScript` 对全部 `.vue`（App.vue / Home.vue / Login.vue）做真实编译 → Login.vue 的 template 与 `<script setup>` 均编译通过，无 template/script 错误。
3. **import 解析检查**：对每个文件的所有静态/动态 import（含 router 的懒加载 `import('../views/Login.vue')`）做解析——相对路径按 Vite 规则（补 `.js`/`.vue`/`/index.js` 等）校验真实文件存在；裸模块用 `require.resolve` + Node ESM `import.meta.resolve` 校验可解析 → 全部通过（如 `pinia`、`vue-router`、`element-plus`、`../stores/auth`、`../views/Login.vue`）。
4. **模块加载冒烟测试**：用临时 Vite 式 resolve loader 在 Node 中实际 `import` 了 `stores/auth.js` → 导出 `useAuthStore` 且为函数、storeId `auth`，模块顶层无运行时错误。

**结果：全部检查 PASS（ALL CHECKS PASSED）。** 验证用临时脚本已删除，未入库。

---

## 三、Commit

- Hash：`2ade4f95a9775b279e023b24708f289b19f73dfe`
- Message：`feat: 前端登录注册与路由守卫`

---

## 四、问题 / 疑虑（concerns）

1. **运行时验证待普通终端补跑（简报已注明，不归本任务）**：沙箱禁止 esbuild spawn，`npm run dev`/`npm run build` 失败，简报 Step 4 的浏览器登录流程（未登录访问 `/` 跳 `/login`、注册后自动登录、刷新保持登录态、重启后端 token 仍有效）**未执行**。需在普通终端按简报 Step 4 步骤验证（后端 `alembic upgrade head` + `APP_MODE=public` 注册 → full 模式复验）。
2. **Node 直连限制（非缺陷）**：`router/index.js` 在纯 Node 中 import 会因 `createWebHistory` 需要浏览器 `window` 而抛 `ReferenceError: window is not defined`——已确认失败点仅为浏览器专属 API，模块本身语法/解析/拼写无误，浏览器/Vite 环境正常。
3. **Node ESM 不解析无扩展名相对导入**：`'../api/http'`、`'./router'` 等省略 `.js` 的写法在纯 Node ESM 下无法解析，但 Vite 完全支持；且全代码库（含 Task 5/6 已有文件）均为该风格，非本次引入的问题。
4. **联调前提**：认证流程依赖后端 `POST /api/auth/login`、`POST /api/auth/register`、`GET /api/auth/me` 及 Task 4 响应结构（`access_token`/`user`，字段名需与后端一致）。静态层面已按此结构编写，建议后端联调时确认字段名（尤其 `user.role` 与守卫 `roles` 的取值 `admin`/`engineer`/`support`）。
5. **git 换行警告**：提交时 git 提示 LF→CRLF（Windows `core.autocrlf` 正常行为），不影响内容与编码（文件为 UTF-8）。

---

## Fix 修复记录

**背景**：Task 7 代码审查发现两个 Important 健壮性缺陷，本小节记录修复。

### 修改的文件

1. `frontend/src/api/http.js`
2. `frontend/src/router/index.js`

### 修改内容

**修复 1（`frontend/src/api/http.js`）— 登录/注册失败时无用户反馈（尤其 401 密码错误）**

原 401 分支只清 token + 硬跳转，用户停留在 `/login` 页时不会跳转，导致输错密码后界面毫无反应。改为：若当前在 `/login` 页则用 `ElMessage.error` 弹出错误提示（优先显示后端 `detail`，否则默认文案"用户名或密码错误"），不跳转；否则清 token 并 `location.href = '/login'` 跳转。

```js
if (status === 401) {
  localStorage.removeItem('token')
  if (location.pathname.startsWith('/login')) {
    ElMessage.error(typeof detail === 'string' ? detail : '用户名或密码错误')
  } else {
    location.href = '/login'
  }
}
```

> 说明：外层作用域（第 16 行）已声明 `const detail = err.response?.data?.detail` 且 401 分支直接复用该变量，故未在分支内重复声明（行为与审查建议完全一致，同时避免 `no-shadow` lint 告警）。

**修复 2（`frontend/src/router/index.js`）— 路由守卫 fetchMe 失败时仅跳登录、不清残留 token**

原 catch 里直接 `return '/login'`，失效 token 残留在内存（pinia state）与 `localStorage`，下次导航会反复携带重试。改为失败时先 `auth.logout()`（清 `token`/`user`/`localStorage`）再跳转。

```js
if (!auth.user) {
  try {
    await auth.fetchMe()
  } catch {
    auth.logout()
    return '/login'
  }
}
```

`stores/auth.js` 的 `logout()` 已确认存在（`token=''`、`user=null`、`localStorage.removeItem('token')`），无需改动。

### 验证命令与结果

- `node --check frontend/src/api/http.js` → **PASS**（无输出，exit 0）
- `node --check frontend/src/router/index.js` → **PASS**（无输出，exit 0）
- import 未受影响：两文件顶部的 `import axios/element-plus`、`import vue-router/../stores/auth` 均未改动，且 `auth.logout()` 在 store 中真实存在。
- 本次仅修改上述 2 个文件（`git status` 确认），其余逻辑未动。

### Commit

- Hash：`563d710219a642f787383e0d282158b8dcfa76d1`
- Message：`fix: 登录失败反馈与守卫清理失效 token`
- 变更统计：2 files changed, 6 insertions(+), 1 deletion(-)
