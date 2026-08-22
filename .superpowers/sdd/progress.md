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




## Minor findings（留待最终 whole-branch review 处理）
- conftest.py 的 except Exception: pass 吞异常（Task 2，源自计划原文）
- main.py CORS allow_origins=["*"] + allow_credentials=True（开发宽松，M5 收紧）
- pydantic class Config 弃用警告（后续统一迁移 ConfigDict）
- alembic.ini 残留占位 sqlalchemy.url（Task 3）
- deps.py int(payload["sub"]) 未纳入 try，建议防御性处理（Task 4）
- login 复用 UserCreate 含注册级校验，建议独立 LoginRequest schema（Task 4）
- users.py 创建用户查重非原子（TOCTOU），建议 catch IntegrityError（Task 5）
- [环境] 沙箱禁止 esbuild spawn，前端 dev/build 需在普通终端补跑验收（Task 6）
- Login.vue 无前端表单校验，依赖后端报错（Task 7，设计取舍）
- Home.vue 死代码，待 M1 收尾清理（Task 8）







