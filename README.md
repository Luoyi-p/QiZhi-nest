# 栖知 Nest

一个在本机运行的个人学习工作台，用来整理资料、写笔记、跟进项目和记录学习进度。

收藏的教程可以关联到学习路线，路线拆成可以勾选的里程碑，笔记和学习记录留在同一个地方。数据保存在本地 SQLite 数据库中，无需注册账号。

## 功能

- **工作台**：查看当前路线、置顶内容、最近笔记和学习时长。
- **学习路线**：按主题设置里程碑，勾选完成情况，自动计算进度。
- **资料、笔记与项目**：支持标签、状态、置顶、路线关联，以及标题、正文和标签搜索。
- **学习时间线**：记录学习主题与分钟数，按日期回看内容和学习活动。
- **数据管理**：归档与恢复内容，导出 JSON 备份，合并导入已有数据。

首次启动会创建带有「示例」标记的数据。在「数据与设置」中关闭「示例内容」后，工作区和统计只显示自己的记录。

## 技术栈

| 部分 | 技术 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Vite、Lucide 图标 |
| 后端 | Python、FastAPI、Pydantic |
| 存储 | SQLite |
| 检查 | vue-tsc、pytest、GitHub Actions |

## 快速开始

准备 Node.js 22.18+ 和 Python 3.12+。以下命令从仓库根目录开始执行。

### 1. 安装依赖

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-lock.txt
cd frontend
npm ci
cd ..
```

macOS / Linux：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-lock.txt
cd frontend
npm ci
cd ..
```

### 2. 启动后端

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

macOS / Linux：

```bash
.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

### 3. 启动前端

另开一个终端，在仓库根目录执行：

```bash
cd frontend
npm run dev
```

访问 [http://127.0.0.1:5173](http://127.0.0.1:5173)。开发服务将 `/api` 请求转发到后端，接口文档位于 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)。

### 构建后运行

如果不需要前端热更新，可以先构建页面：

```bash
cd frontend
npm run build
cd ..
```

随后使用上面的命令启动后端，访问 [http://127.0.0.1:8000](http://127.0.0.1:8000)。后端在启动时检测 `frontend/dist` 并提供静态页面。首次构建后需要重启已运行的后端；修改前端后需要重新构建。

## 数据与备份

数据库默认位于仓库的 `data/nest.db`。如需更换位置，在启动后端前设置 `NEST_DB_PATH`，建议使用绝对路径：

```powershell
# Windows PowerShell
$env:NEST_DB_PATH = "D:\NestData\nest.db"
```

```bash
# macOS / Linux
export NEST_DB_PATH="$HOME/.local/share/nest/nest.db"
```

应用不自动读取 `.env` 文件。浏览器只保存「是否显示示例」的偏好，内容由后端写入数据库。

在「数据与设置」中导出 JSON，可以备份或迁移全部数据，包括示例与归档内容。导入文件最大为 10 MB，按各类记录的 ID 合并，已有 ID 保留本地版本。格式、重复 ID 或路线关联校验失败时，整份文件都不会导入。

数据库和 `nest-backup-*.json` 已加入忽略规则。个人备份仍建议保存在仓库外。

## 项目结构

```text
.
├── frontend/
│   └── src/
│       ├── components/     编辑器、弹窗、资料卡片、活跃图
│       ├── views/          各页面
│       ├── store.ts        共享数据与 API 请求
│       └── ui.ts           导航与弹窗状态
├── backend/
│   ├── app/                API、数据校验、数据库与示例数据
│   └── tests/              接口测试
├── docs/                   功能范围、界面约定与验证记录
├── .github/workflows/      构建与测试
└── data/                   本地数据库，不纳入版本控制
```

SQLite 的 `documents` 表按路线、内容、学习记录保存 JSON。前端读取工作区快照后完成搜索和统计，适合个人规模的数据；目前没有服务端分页或全文索引。

## 开发与检查

前端类型检查与构建：

```bash
cd frontend
npm run build
```

后端测试在仓库根目录执行：

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m pytest -q backend/tests
```

```bash
# macOS / Linux
.venv/bin/python -m pytest -q backend/tests
```

测试覆盖持久化、输入校验、归档恢复、备份往返、重复导入和非法导入原子性等行为。GitHub Actions 会在推送和 Pull Request 时运行前端构建与后端测试。

提交问题或改动前，请阅读 [贡献指南](CONTRIBUTING.md)。功能范围见 [SPEC](docs/SPEC.md)，检查记录见 [VERIFICATION](docs/VERIFICATION.md)。

## 使用范围

当前版本面向单人本地使用，按上述命令仅监听 `127.0.0.1`，没有登录鉴权，不适合直接开放到公网。笔记为纯文本，暂不支持 Markdown 渲染、附件上传和跨设备自动同步。

## 许可证

[MIT](LICENSE)
