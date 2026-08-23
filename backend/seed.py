"""种子数据脚本：创建注塑机领域示例知识（幂等，可直接发布并向量化）。
用法：cd backend && .venv/Scripts/python.exe seed.py（开发）或 docker compose exec backend python seed.py（部署）
"""
from sqlalchemy import select

from app.db import SessionLocal
from app.models.knowledge import KnowledgeItem
from app.models.user import User
from app.core.security import hash_password
from app.services.indexing import reindex_knowledge

SEED_ITEMS = [
    {
        "title": "模保功能原理",
        "kind": "article",
        "category": "运动控制",
        "machines": "A5/A6",
        "aliases": ["模保是什么", "模具保护", "模保原理", "低压模保"],
        "body": "## 模保（模具保护）原理\n\n模保是在合模过程中，通过低压低速的方式检测模具内是否有异物或产品未取出，防止压坏模具。\n\n### 工作原理\n1. 合模到模保起始位置后，转为低压低速继续合模\n2. 在模保区间内，若实际压力超过设定压力（或实际位置未到达设定位置），判定为模保异常\n3. 异常时立即停止合模并报警，保护模具\n\n### 关键参数\n- 模保压力：通常远低于正常合模压力\n- 模保位置/行程：模保生效的区间\n- 模保时间：模保区间的允许时间",
    },
    {
        "title": "顶出动作原理",
        "kind": "article",
        "category": "运动控制",
        "machines": "A5/A6",
        "aliases": ["顶出是什么", "顶针", "脱模", "顶出原理"],
        "body": "## 顶出动作原理\n\n顶出机构在开模后把成型制品从模具型腔中顶出，便于取件。\n\n### 工作流程\n1. 开模到位后，顶出油缸（或伺服电机）驱动顶针前进\n2. 顶针推动制品脱离型腔\n3. 顶出到位后，顶针退回（顶退）\n\n### 关键参数\n- 顶出次数：多次顶出可设置\n- 顶出速度/压力\n- 顶出位置（顶出行程）\n- 顶退速度",
    },
    {
        "title": "射胶（注射）原理",
        "kind": "article",
        "category": "运动控制",
        "machines": "A5/A6",
        "aliases": ["射胶是什么", "注射原理", "射胶速度", "塑化"],
        "body": "## 射胶（注射）原理\n\n射胶是把熔融塑料高速注入模具型腔的过程，分注射与保压两个阶段。\n\n### 注射阶段\n- 螺杆（或柱塞）以设定速度前进，将熔料注入型腔\n- 多段射胶速度控制：充填不同阶段用不同速度\n\n### 保压阶段\n- 型腔充满后转为保压，补偿冷却收缩\n- 保压压力与保压时间影响制品密度与尺寸\n\n### 关键参数\n- 射胶速度（多段）\n- 射胶压力（多段）\n- 保压压力与保压时间\n- 射胶终点位置（切换保压）",
    },
    {
        "title": "料筒温度控制",
        "kind": "article",
        "category": "温度控制",
        "machines": "A5/A6",
        "aliases": ["料筒温度", "温度设定", "加热", "温控"],
        "body": "## 料筒温度控制\n\n料筒分多段加热，使塑料逐渐熔融。温度过高会降解材料，过低则塑化不良。\n\n### 分段说明\n- 料筒通常分 3-5 段，从进料段到喷嘴段温度递增\n- 喷嘴段温度略低于前段（防流涎）\n\n### 注意事项\n- 开机先升温到设定值并保温，再启动螺杆\n- 换料时需按材料特性调整温度\n- 温度异常（超温/低温）会报警并停止动作",
    },
    {
        "title": "模保报警 E012 处理",
        "kind": "case",
        "category": "故障处理",
        "machines": "A5/A6",
        "aliases": ["E012 报警", "模保报警", "模具保护报警", "E012 怎么处理"],
        "body": "## 模保报警 E012 处理\n\n### 故障现象\n合模过程中触发模保报警，机器停止合模。\n\n### 排查步骤\n1. 检查模具内是否有异物、产品是否未取净\n2. 检查模保压力/位置/时间参数是否设置合理（压力是否过低、区间是否过长）\n3. 检查模具顶针是否复位、抽芯是否到位\n4. 检查模保相关的行程开关/传感器是否正常\n\n### 解决方案\n- 清理异物或未取出产品\n- 重新校准模保参数\n- 更换故障传感器\n\n### 注意事项\n模保报警是保护模具的安全机制，**不可盲目加大模保压力或关闭模保**，否则可能压坏模具。",
    },
    {
        "title": "合模压力不足报警处理",
        "kind": "case",
        "category": "故障处理",
        "machines": "A5/A6",
        "aliases": ["合模压力不足", "锁模压力不够", "合模压力报警"],
        "body": "## 合模压力不足报警处理\n\n### 故障现象\n合模到位后压力达不到设定值，报警。\n\n### 排查步骤\n1. 检查液压系统压力是否正常\n2. 检查合模油缸是否内泄\n3. 检查模具是否过厚导致行程异常\n4. 检查压力传感器/比例阀是否正常\n\n### 解决方案\n- 调整系统压力\n- 检修油缸密封\n- 校准传感器\n\n### 注意事项\n合模压力不足会导致制品飞边，甚至模具胀开，需及时处理。",
    },
    {
        "title": "中子（抽芯）控制",
        "kind": "article",
        "category": "运动控制",
        "machines": "A5/A6",
        "aliases": ["中子是什么", "抽芯", "中子控制", "侧抽芯"],
        "body": "## 中子（抽芯）控制\n\n中子用于成型带侧孔/侧凹的产品，在开模前把侧型芯抽出。\n\n### 工作流程\n1. 合模后、射胶前，中子芯插入到位\n2. 射胶保压冷却完成\n3. 开模前，中子芯抽出\n\n### 关键参数\n- 中子动作位置/时间点\n- 中子进/出速度与压力\n- 中子到位检测\n\n### 注意事项\n中子动作时序必须与开合模联锁，否则会损坏模具。",
    },
    {
        "title": "开合模动作时序",
        "kind": "article",
        "category": "运动控制",
        "machines": "A5/A6",
        "aliases": ["开合模时序", "合模流程", "开模流程", "动作顺序"],
        "body": "## 开合模动作时序\n\n### 合模流程\n1. 快速合模（高速）\n2. 低压模保区间（模保）\n3. 高压锁模（锁紧）\n\n### 开模流程\n1. 慢速开模（先泄压）\n2. 快速开模\n3. 慢速开模到位（缓冲）\n\n### 注意事项\n- 开模前必须先完成中子抽出、顶退\n- 合模前必须顶针复位、中子到位\n- 各动作有位置/压力到位检测与联锁",
    },
    {
        "title": "HMI 手动模式操作",
        "kind": "article",
        "category": "HMI 操作",
        "machines": "A5/A6",
        "aliases": ["手动模式", "HMI 操作", "手动合模", "手动操作"],
        "body": "## HMI 手动模式操作\n\n### 进入手动模式\n1. 在 HMI 主页切换到手动模式\n2. 确认安全门关闭、急停复位\n\n### 手动动作\n- 手动合模/开模（点动或长按）\n- 手动顶出/顶退\n- 手动射胶/塑化\n- 手动中子进/出\n\n### 注意事项\n- 手动模式用于调试与检修，正常生产用自动模式\n- 手动动作前确认模具区域安全\n- 各动作有互锁（如合模时不能顶出）",
    },
    {
        "title": "料筒清洗（换料）步骤",
        "kind": "article",
        "category": "维护保养",
        "machines": "A5/A6",
        "aliases": ["料筒清洗", "换料", "清洗料筒", "换色"],
        "body": "## 料筒清洗（换料）步骤\n\n### 步骤\n1. 将料筒温度调到新材料所需温度（或清洗料推荐温度）\n2. 排空旧料（反复塑化、注射直到无旧料）\n3. 投入清洗料（如 PP/清洗专用料）反复冲洗\n4. 确认旧料排净后投入新材料\n5. 用新材料冲洗至颜色/性质稳定\n\n### 注意事项\n- 换料温差大时要逐步升温，避免材料降解\n- 深色换浅色需更充分清洗\n- 清洗时注意安全，防止烫伤",
    },
    {
        "title": "常见报警代码表",
        "kind": "code",
        "category": "故障处理",
        "machines": "A5/A6",
        "aliases": ["报警代码", "报警表", "故障代码", "报警大全"],
        "body": "## 常见报警代码表\n\n| 代码 | 含义 | 常见处理 |\n|---|---|---|\n| E012 | 模保报警 | 清理异物/校准模保参数 |\n| E020 | 料筒超温 | 检查加热圈/热电偶 |\n| E021 | 料筒低温 | 等待升温/检查加热 |\n| E030 | 液压压力异常 | 检查油泵/压力传感器 |\n| E040 | 安全门未关 | 关闭安全门/检查门开关 |\n| E050 | 顶出未到位 | 检查顶出传感器 |\n| E060 | 中子未到位 | 检查中子行程开关 |\n\n> 具体报警含义与处理请以机型说明书为准。",
    },
    {
        "title": "保压切换原理",
        "kind": "article",
        "category": "运动控制",
        "machines": "A5/A6",
        "aliases": ["保压切换", "保压", "注射保压", "VP 切换"],
        "body": "## 保压切换原理\n\n注射阶段结束后切换到保压阶段，简称 VP 切换（速度控制→压力控制）。\n\n### 切换方式\n- 位置切换：螺杆到达设定位置时切换（最常用）\n- 压力切换：达到设定压力时切换\n- 时间切换：达到设定时间时切换\n\n### 保压作用\n- 补偿制品冷却收缩\n- 控制制品尺寸与密度\n- 保压时间过长会过充、过短会缩水\n\n### 关键参数\n- 切换位置\n- 保压压力与保压时间（多段）",
    },
    {
        "title": "模具温度机设置",
        "kind": "article",
        "category": "温度控制",
        "machines": "A5/A6",
        "aliases": ["模温机", "模具温度", "模温设定", "水温机"],
        "body": "## 模具温度机设置\n\n模温机用于控制模具温度，影响制品外观与成型周期。\n\n### 设置要点\n- 按材料特性设定模温（如 PP 约 40-60℃，PC 约 80-120℃）\n- 动模/定模可分别设不同温度\n- 开机先预热模具到设定温度再生产\n\n### 注意事项\n- 模温过高会导致制品变形、周期变长\n- 模温过低会导致充填不良、熔接线明显\n- 定期检查模温机水位与管路",
    },
]

def seed():
    db = SessionLocal()
    # 确保有 engineer 账号
    eng = db.scalar(select(User).where(User.username == "engineer"))
    if eng is None:
        eng = User(username="engineer", role="engineer", hashed_password=hash_password("engineer123"))
        db.add(eng)
        db.commit()
        db.refresh(eng)
    created = 0
    for it in SEED_ITEMS:
        exists = db.scalar(select(KnowledgeItem).where(KnowledgeItem.title == it["title"]))
        if exists:
            continue
        k = KnowledgeItem(
            title=it["title"],
            kind=it["kind"],
            body=it["body"],
            aliases=it["aliases"],
            category=it["category"],
            machines=it["machines"],
            tags=[],
            status="published",
            publish_to_public=True,
            author_id=eng.id,
        )
        db.add(k)
        db.flush()
        reindex_knowledge(k, db)
        db.commit()
        created += 1
    db.close()
    print(f"种子数据完成：新增 {created} 条，共 {len(SEED_ITEMS)} 条。demo 账号：engineer/engineer123")


if __name__ == "__main__":
    seed()
