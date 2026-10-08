import json
from datetime import datetime, timedelta, timezone

from .db import Database


def seed_demo(db: Database):
    with db.connect() as conn:
        if conn.execute("SELECT 1 FROM metadata WHERE key='initialized'").fetchone():
            return
        # Initialization marker and all demonstration records commit together.
        now = datetime.now(timezone.utc)
        stamp = now.isoformat()
        tracks = [
            {"id": "demo-vue", "title": "Vue 3 深入与工程实践", "description": "从响应式原理，到一个真正属于自己的应用。", "color": "green", "milestones": [{"title": t, "done": i < 3} for i, t in enumerate(["Composition API 与组件设计", "响应式系统与依赖追踪", "TypeScript 类型建模", "封装一个可复用的 Composable", "路由与状态管理", "测试与发布"])]},
            {"id": "demo-python", "title": "Python 后端小步走", "description": "用 FastAPI 把想法变成可以调用的服务。", "color": "blue", "milestones": [{"title": t, "done": i < 1} for i, t in enumerate(["Python 类型与数据结构", "FastAPI 接口与参数校验", "SQLite 持久化", "接口测试", "部署个人服务"])]},
            {"id": "demo-system", "title": "构建我的数字花园", "description": "给碎片信息一个入口，让知识逐渐长出连接。", "color": "orange", "milestones": [{"title": t, "done": i < 2} for i, t in enumerate(["整理资料分类", "设计统一信息入口", "建立每周回顾", "完成第一个实践作品"])]},
        ]
        entries = [
            ("resource", "Vue.js 官方文档", "常读常新的学习入口。下一次重点看组合式函数与响应式进阶。", "https://cn.vuejs.org/guide/introduction.html", ["Vue", "官方文档"], "demo-vue", True, "active"),
            ("resource", "FastAPI 官方教程", "跟着教程做一个小接口，再把它连接到自己的 Vue 页面。", "https://fastapi.tiangolo.com/zh/tutorial/", ["Python", "API"], "demo-python", True, "inbox"),
            ("note", "理解响应式：从一个最小例子开始", "今天的思考\n\n响应式的关键不是数据变化本身，而是记录谁依赖了它。\n\n我的验证方法\n1. 用一个计数器观察 computed 何时重新计算。\n2. 用 watchEffect 看依赖如何被收集。\n3. 把这两个例子整理成可运行的小实验。\n\n下一步：封装一个管理异步请求状态的 Composable。", "", ["Vue", "学习笔记"], "demo-vue", True, "active"),
            ("project", "栖知 · 我的个人数字工作台", "把学习路线、笔记和收藏连在一起。\n\n第一阶段：跑通收藏 → 关联路线 → 记录学习的完整流程。\n第二阶段：根据自己的使用习惯迭代。", "", ["Vue", "Python", "个人项目"], "demo-system", True, "active"),
            ("resource", "MDN Web Docs", "查阅浏览器 API、JavaScript 和 CSS 的参考入口。", "https://developer.mozilla.org/zh-CN/", ["Web", "参考手册"], None, False, "inbox"),
            ("note", "每周回顾：让输入留下痕迹", "这周学到了什么？\n哪一条收藏已经变成了可运行的代码？\n下周只选一个最想弄懂的问题。", "", ["每周回顾", "个人成长"], "demo-system", False, "inbox"),
            ("project", "一个轻量的 API 练习场", "练习请求校验、错误处理和数据持久化。先实现一个可靠的小接口。", "", ["Python", "实验"], "demo-python", False, "inbox"),
        ]
        records = [("tracks", {**t, "created_at": stamp, "archived": False, "demo": True}) for t in tracks]
        for i, (kind, title, content, url, tags, track_id, starred, status) in enumerate(entries):
            records.append(("entries", {"id": f"demo-entry-{i}", "kind": kind, "title": title, "content": content, "url": url, "tags": tags, "track_id": track_id, "starred": starred, "status": status, "archived": False, "demo": True, "created_at": (now - timedelta(days=i)).isoformat(), "updated_at": (now - timedelta(hours=i * 7)).isoformat()}))
        for i in range(90):
            if i % 7 not in (1, 4) and i % 11 != 0:
                records.append(("sessions", {"id": f"demo-session-{i}", "title": ["阅读文档并整理笔记", "完成一个小实验", "复习并推进学习路线"][i % 3], "minutes": [25, 45, 60, 30][i % 4], "track_id": tracks[i % 3]["id"], "created_at": (now - timedelta(days=i)).isoformat(), "demo": True}))
        for collection, payload in records:
            conn.execute("INSERT OR IGNORE INTO documents VALUES (?, ?, ?)", (collection, payload["id"], json.dumps(payload, ensure_ascii=False)))
        conn.execute("INSERT INTO metadata VALUES ('initialized', '1')")
