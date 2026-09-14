# 栖知 Nest

**技术学习入口 × 个人数字工作台。**

把散落的教程、笔记、项目和学习记录，串成自己的知识路径。为单人使用设计，Vue 3 + TypeScript 前端、Python FastAPI 后端、SQLite 本地持久化。

## 能做什么

- **工作台**：下一步学习、置顶入口、最近思考、学习统计与 105 天活跃图。
- **学习路线**：自己定义小目标，逐步勾选里程碑，自动计算完成进度。
- **个人数字资料库**：收藏网页、写纯文本笔记、记录实践项目；支持标签、状态、置顶、正文搜索和关联路线。
- **成长时间线**：记录每次学习的主题与投入分钟数，回看自己的数字积累。
- **数据掌控**：内容归档/恢复、JSON 全量导出、合并导入；同 ID 保留本地记录。

首次启动附带明确标记的示例内容。前往「数据与设置」关闭「示例内容」，即可只显示自己的内容；统计同步排除示例。

## 本地运行

需要 Node.js 22.18+（本项目验证环境为 22.21）、Python 3.12+。

### 1. 安装依赖

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-lock.txt
cd frontend
npm ci
cd ..
```

macOS / Linux 使用 `.venv/bin/python` 替换 `.\.venv\Scripts\python.exe`。

### 2. 启动 Python 服务

在项目根目录打开终端：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

### 3. 启动 Vue 开发服务

另开终端：

```powershell
cd frontend
npm run dev
```

打开 [http://127.0.0.1:5173](http://127.0.0.1:5173)。Vue 开发服务通过 `/api` 将请求代理到 Python。接口文档位于 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)。

### 只启动一个服务

先构建前端：

```powershell
cd frontend
npm run build
cd ..
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

打开 [http://127.0.0.1:8000](http://127.0.0.1:8000)。Python 会在启动时检测并提供 `frontend/dist` 中的页面。修改前端后需重新构建；首次构建后需重启后端。页面使用 hash 导航，刷新子页面不会丢失路由。

## 数据与备份

- 数据库默认保存到 `data/nest.db`，与启动命令所在目录无关；可用 `NEST_DB_PATH` 环境变量指定其他路径。
- 本项目不读取 `.env` 文件；如需改路径，请直接配置环境变量。
- 开发和正式页面使用同一套本地数据。浏览器只保存「是否显示示例」偏好。
- 学习统计和活跃图按浏览器所在时区计算。「最近 7 天」包含今天及前 6 个自然日。
- 从「数据与设置」导出 JSON 备份，包含全部内容、示例与归档项；可以迁移到另一台电脑。
- 导入上限 10 MB，按 ID 合并。已有 ID 不覆盖；文件格式、重复 ID 或关联校验失败时，不导入任何内容。
- 备份可能包含个人内容，请保存在仓库之外。`.gitignore` 忽略本项目数据目录及 `nest-backup-*.json`。

## 项目结构

```text
nest/
├── frontend/
│   ├── src/components/    弹窗、编辑器、资料卡片、活跃图
│   ├── src/views/         工作台、路线、资料库、时间线、数据管理
│   ├── src/store.ts       共享数据及 API 访问
│   └── src/ui.ts          导航及弹窗状态
├── backend/
│   ├── app/models.py      输入与备份校验
│   ├── app/db.py          SQLite 事务与文档存储
│   ├── app/main.py        HTTP API、导入导出、静态页面
│   ├── app/seed.py        首次启动示例
│   └── tests/             API 行为测试
├── docs/SPEC.md           第一版范围
├── .github/workflows/     GitHub 自动构建与测试
└── data/                  私人数据库，不提交
```

这里有意选择小规模文档存储：SQLite `documents` 表保存经过 Pydantic 校验的路线、内容、学习记录 JSON；一次快照供前端搜索和聚合。适用于个人数据量，不假装提供全文搜索引擎或服务端分页。

## 验证

```powershell
cd frontend
npm run build
cd ../backend
..\.venv\Scripts\python.exe -m pytest -q
```

测试覆盖跨重启持久化、关联与校验、归档恢复、备份往返、重复导入、非法导入原子性、示例初始化与跨来源写入保护。

## 上传 GitHub

此目录可以单独作为仓库发布。先在 GitHub 创建空仓库，再在本目录执行（将地址替换为你的仓库）：

```bash
git remote add origin https://github.com/YOUR_NAME/nest.git
git push -u origin main
```

代码默认使用 MIT License。上传前检查 `git status`，不要把数据库、私人备份或 `.env` 加入 Git。GitHub Actions 会自动检查 Vue 构建与 Python API 测试。

## 当前边界

这是单人本地版本，服务默认只监听 `127.0.0.1`，没有登录鉴权。当前支持 http/https 链接与纯文本笔记，不包含附件上传、Markdown 渲染、AI 生成、自动爬取或跨设备同步。若以后要开放到公网，应先加入身份验证与部署配置。

实现依据：[Vue 官方入门文档](https://vuejs.org/guide/quick-start.html)、[FastAPI 官方入门文档](https://fastapi.tiangolo.com/tutorial/first-steps/)。
