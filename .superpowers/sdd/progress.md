# 进度台账

## M1 项目骨架与认证

Task 1: complete (commits e2abe83..ad2cf25, review clean)
Task 2: complete (commits 56b9d19..e07c30a, review clean)




## Minor findings（留待最终 whole-branch review 处理）
- conftest.py 的 except Exception: pass 吞异常（Task 2，源自计划原文）
- main.py CORS allow_origins=["*"] + allow_credentials=True（开发宽松，M5 收紧）
- pydantic class Config 弃用警告（后续统一迁移 ConfigDict）

