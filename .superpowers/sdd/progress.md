# 进度台账

## M1 项目骨架与认证

Task 1: complete (commits e2abe83..ad2cf25, review clean)
Task 2: complete (commits 56b9d19..e07c30a, review clean)
Task 3: complete (commits 614fa58..732755b, review clean)
Task 4: complete (commits 732755b..52577c0, review clean)
Task 5: complete (commits 52577c0..e0cf1af, review clean)
Task 6: complete (commits d18fec8..2c70013, review clean)
Task 7: complete (commits af1a574..563d710, review clean after fix)
Task 8: complete (commits 987e534..6020211, review clean)
Task 9: complete (commits 5da2b69..29782f9, review clean)

## M1 里程碑：完成
- final review 完成，3 项必改已修复（commit 286562b，SECRET_KEY 校验/public 挂载隔离/group_name 补全）
- 后端 15 passed；前端静态编译通过，运行时待普通终端补验
- 里程碑总结：docs/superpowers/progress/2026-08-22-m1-总结.md




## Minor findings（triage 结果见里程碑总结 docs/superpowers/progress/2026-08-22-m1-总结.md）
- conftest.py 的 except Exception: pass 吞异常（Task 2，可延后）
- main.py CORS allow_origins=["*"] + allow_credentials=True（开发宽松，M5 收紧）
- pydantic class Config 弃用警告（后续统一迁移 ConfigDict）
- alembic.ini 残留占位 sqlalchemy.url（Task 3，可延后）
- deps.py int(payload["sub"]) 未纳入 try，建议防御性处理（Task 4，可延后）
- login 复用 UserCreate 含注册级校验，建议独立 LoginRequest schema（Task 4，可延后）
- users.py 创建用户查重非原子（TOCTOU），建议 catch IntegrityError（Task 5，可延后）
- [环境] 沙箱禁止 esbuild spawn，前端 dev/build 需在普通终端补跑验收（Task 6）
- Login.vue 无前端表单校验，依赖后端报错（Task 7，设计取舍）
- ~~Home.vue 死代码~~（已在 M1 收尾清理）
- ~~group_name 静默丢弃~~（已在 final fix 286562b 修复）









