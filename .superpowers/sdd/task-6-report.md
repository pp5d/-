# Task 6 报告：前端骨架（Vite + Vue3 + Element Plus）

- 状态：**DONE_WITH_CONCERNS**
- 执行者：实现子代理（M1 Task 6）
- 分支：`feature/m1-foundation`
- Commit：`2c70013a17704c231b4c199648d467080d5e8099`（`feat: 前端骨架`）

## 执行步骤

按简报 Step 1 → Step 10 顺序执行：

1. **Step 1–8 文件创建**（全部逐字按简报原文，UTF-8）：
   - `frontend/package.json`
   - `frontend/vite.config.js`（port 5173，proxy `/api → http://localhost:8000`）
   - `frontend/index.html`
   - `frontend/src/main.js`（Element Plus 全量引入 + zh-cn locale + 图标全局注册）
   - `frontend/src/App.vue`（`<router-view />`）
   - `frontend/src/api/http.js`（axios 实例，baseURL `/api`，Bearer token 注入，401 清 token 跳 `/login`，错误 ElMessage）
   - `frontend/src/stores/app.js`（`mode` 默认 `''`，未改为 'full'，getters `isPublic`/`isFull`，action `fetchHealth()`）
   - `frontend/src/router/index.js` + 占位页 `frontend/src/views/Home.vue`（el-result "AIQA 骨架已就绪"）

2. **Step 9 依赖安装**：见下节。

3. **Step 9 编译验证**：见下节（沙箱限制，改用等价静态验证）。

4. **Step 10 提交**：`git add frontend/` → `git commit -m "feat: 前端骨架"`，共 10 个文件（含 `package-lock.json`），不含 `node_modules/`、`dist/`、临时文件。

## npm install 结果

- 首次 `npm install`（默认缓存 `C:\Users\41691\AppData\Local\npm-cache`）：**EPERM 失败**——沙箱（workspace-write 模式）拒绝向工作区外路径写入缓存（`_cacache\tmp\***`）。
- 重试一次：同样 EPERM（确认非瞬时故障，属沙箱对工作区外文件访问的固定限制）。
- 改用工作区内缓存 `npm install --cache ./frontend/.npm-cache`：下载/缓存阶段通过，但在执行依赖生命周期脚本（`esbuild@0.21.5 postinstall`、`vue-demi@0.14.10 postinstall`）时 `spawn EPERM`（-4048）——沙箱禁止 Node 以管道 stdio（named pipe）spawn 子进程，而 npm 运行 postinstall 恰好捕获子进程输出。
- 最终：`npm install --ignore-scripts --no-audit --no-fund --cache ./.npm-cache` **成功，90 个包**。
  - 两个被跳过的 postinstall 在本项目场景均为无害：`vue-demi` 的 postinstall 是 Vue2/3 切换 no-op（已装 Vue3，lib 文件在位）；`esbuild` 的二进制由可选依赖 `@esbuild/win32-x64/esbuild.exe` 提供（已验证存在）。
  - 安装结束后已删除工作区缓存目录 `frontend/.npm-cache`，未入库。

## 编译验证结果

- **`npm run build` 失败（环境限制，非项目缺陷）**：vite 强制用 esbuild 打包配置文件（`bundleConfigFile` 硬编码 `esbuild.build()`），esbuild 以管道 stdio spawn 原生二进制被沙箱以 EPERM 拒绝（与 postinstall 同一沙箱边界）。`npm run dev` 走同一 esbuild 路径，同样无法在本沙箱内运行。
- **等价静态编译验证（全部通过）**，使用 `@vue/compiler-sfc`（纯 JS，无需原生子进程）：
  1. 全部 4 个 JS 模块（main.js / router / api/http.js / stores/app.js）经 `vm.SourceTextModule` module 解析 → **语法 OK**；
  2. 2 个 SFC（App.vue / Home.vue）经 `@vue/compiler-sfc` 解析 + 模板编译 → **编译 OK**（两文件均为纯模板 SFC，无 script 块，符合简报原文）；
  3. 全部 import 说明符解析 → **OK**（含 `element-plus/es/locale/lang/zh-cn`，经 exports 映射 + 扩展名探测确认 vite 可解析；`element-plus/dist/index.css` 存在）。
- **建议**：在无沙箱限制的终端执行一次 `npm run build` 做最终确认（预期通过；若需，可先补跑两个 postinstall，或保持 --ignore-scripts 不变——esbuild 二进制已由平台包提供）。

## Commit

```
2c70013a17704c231b4c199648d467080d5e8099 feat: 前端骨架
```

## 问题 / 疑虑（Concerns）

1. **vite dev/build 无法在本沙箱内直接验证**：esbuild 子进程（管道 stdio spawn）被沙箱 EPERM 拦截，属环境边界而非代码问题；已用静态等价验证覆盖语法、SFC 编译、依赖解析，建议主代理/用户在普通终端跑一次 `npm run build`（或 `npm run dev` + 浏览器打开 http://localhost:5173 看 "AIQA 骨架已就绪"）。
2. **依赖以 `--ignore-scripts` 安装**：本项目所需 esbuild 二进制由 `@esbuild/win32-x64` 可选依赖提供（已确认在 node_modules），跳过两个 no-op/验证型 postinstall 不影响功能；`package-lock.json` 已提交，后续在普通环境 `npm ci`/`npm install` 会正常执行脚本。
3. **element-plus 实际解析版本 2.14.5**（`^2.9.1` 语义化升级），高于简报标注的 2.9.1；为同一大版本内的向后兼容升级，main.js 的 `element-plus/es/locale/lang/zh-cn` 导入已验证可解析，无兼容性担忧。
4. LF→CRLF git 警告为仓库 autocrlf 配置的正常提示，无影响。
