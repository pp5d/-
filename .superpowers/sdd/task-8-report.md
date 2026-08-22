# Task 8 Report: 主布局（按模式渲染菜单）

- **状态**: DONE_WITH_CONCERNS（详见"问题/疑虑"）
- **分支**: `feature/m1-foundation`
- **Commit**: `6020211cd8790d9b8cb704ed243ef8a71127b0d2`（message: `feat: 主布局与按模式菜单`）

## 执行步骤

1. **Step 1** — 创建 `frontend/src/layouts/MainLayout.vue`（逐字照抄简报代码：侧边菜单按 `app.isPublic` 渲染公网/内网两套菜单项；内网模式按 `auth.isAdmin` 显示"用户管理"；顶栏含模式文案、用户下拉（用户名+角色）与退出登录；`onMounted` 中 `if (!app.mode) app.fetchHealth()` 保持 Task 6 约定，未改动）。
2. **Step 2** — 创建 `frontend/src/views/Dashboard.vue`（逐字照抄简报代码：欢迎语 + 系统模式/角色/说明的 `el-descriptions`）。
3. **Step 3** — 更新 `frontend/src/router/index.js`：
   - `/login` 路由保留（`meta: { public: true }`）；
   - `/` 改为 `MainLayout.vue` 懒加载 + 子路由：`''` → `Dashboard.vue`；`chat`/`knowledge`/`tickets` → `Placeholder.vue`；`manage`/`review` → `Placeholder.vue`（`meta.roles: ['engineer','admin']`）；`admin/users` → `Placeholder.vue`（`meta.roles: ['admin']`）；
   - 原有 `beforeEach` 守卫（public/登录/roles 校验）保持不变，与 `meta.roles` 配套生效。
   - 创建 `frontend/src/views/Placeholder.vue`（`el-empty` 占位页）。
   - 原 `frontend/src/views/Home.vue` 不再被路由引用；简报未要求删除，故保留（后续里程碑可复用或清理）。
4. **Step 4** — 浏览器手动验证无法执行（沙箱禁止 esbuild spawn，`npm run dev`/`build` 会 EPERM 失败），改用**静态编译验证**，结果全部通过（详见下节）。
5. **Step 5** — 按简报命令提交：`git add frontend/src && git commit -m "feat: 主布局与按模式菜单"`。

## 静态验证结果

| 检查项 | 结果 |
| --- | --- |
| `node --check src/router/index.js`（ESM 语法，Node v24.16.0） | ✅ 通过 |
| `@vue/compiler-sfc` parse + compileTemplate + compileScript（6 个 .vue：App/MainLayout/Dashboard/Home/Login/Placeholder） | ✅ 全部通过，0 错误 |
| 相对 import 路径解析（18 处，含 router 中 6 处懒加载 `Placeholder.vue`、`MainLayout.vue`、`Dashboard.vue`、stores、main.js） | ✅ 全部可解析 |
| 组件可用性 | ✅ Element Plus 与全部图标（HomeFilled/ChatDotRound/Reading/Tickets/Notebook/Checked/User/ArrowDown）已由 main.js 全局注册，模板无需额外 import |
| stores 接口 | ✅ app（mode 初始 `''`/isPublic/isFull/fetchHealth）与 auth（user/isAdmin/isEngineer/logout）与简报要求一致 |

> 说明：静态验证脚本为临时文件（`frontend/static-check.mjs`），验证完成后已删除，未进入提交。

## 逻辑核对（替代手动验证）

- 登录后进入 `/` → MainLayout + Dashboard，`onMounted` 拉取 `/health` 设置 mode，菜单按 mode 渲染：`public` 显示公网 4 项，其余（`full`/未获取到）显示内网 6 项；engineer 不显示"用户管理"（`v-if="auth.isAdmin"`）。
- 未登录访问 `/chat` 等 → 守卫 `!auth.token` 重定向 `/login`；engineer 访问 `/admin/users`、非 admin 访问 `/manage`/`/review` → 守卫按 `meta.roles` 重定向 `/`。
- `onMounted(() => { if (!app.mode) app.fetchHealth() })` 依赖 mode 初始为空串，Task 6 已保证，未改动。

## 问题/疑虑

1. **DONE_WITH_CONCERNS 原因**：简报 Step 4 的浏览器手动验证（登录后菜单按模式渲染、engineer 看不到用户管理、未登录跳登录）受沙箱限制无法实际执行，仅以上述静态编译 + 代码逻辑核对替代。建议在可运行环境执行一次真实浏览器验证。
2. `frontend/src/views/Home.vue` 已不被任何路由引用，成为死代码；简报未要求删除，故保留，需协调者决定是否在后续任务清理。
3. git 提交时出现 LF→CRLF 换行警告（仅换行符规范化提示，不影响内容）；仓库当前 `.gitattributes`/core.autocrlf 配置未统一，若在意可在后续统一。
4. `.superpowers/sdd/` 下存在多个未跟踪的 brief/report/diff 文件（含本任务 task-8-brief.md），按简报命令仅提交 `frontend/src`，这些文件留给协调者统一管理。
