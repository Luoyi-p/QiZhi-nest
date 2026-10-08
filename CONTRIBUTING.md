# 贡献指南

## 提交问题

报告问题时，请附上操作步骤、预期结果、实际结果，以及操作系统、Node.js 和 Python 版本。界面问题可以附截图；日志和备份请先移除个人内容。

功能建议请说明具体使用场景。

## 提交改动

1. 按 [README](README.md) 启动项目，确认问题或需要调整的行为。
2. 每个 Pull Request 集中处理一件事；涉及行为变更时补充相应测试。
3. 运行前端构建和后端测试，在描述中写明变更内容与验证结果。界面变更请附前后截图。
4. 修改启动方式、数据格式或功能范围时，同步更新文档。

## 代码约定

- Vue 使用 Composition API 和 TypeScript。页面负责展示，数据访问放在 `frontend/src/store.ts`，导航和弹窗状态放在 `frontend/src/ui.ts`。
- Python API 使用 Pydantic 校验输入；SQL 使用参数绑定，写操作放在事务中。
- 内容链接只接受 http/https。笔记按纯文本显示，不直接渲染用户 HTML。
- 写操作应有失败反馈，成功后更新前端状态；提交期间避免重复请求。
- 页面保留加载、错误和空状态，检查手机布局与键盘操作。
- 注释解释约束或取舍，避免复述代码。暂时只出现一次的简单逻辑可以留在使用处。
- 不提交数据库、私人备份、虚拟环境或密钥。应用目前只读取系统环境变量，不自动加载 `.env` 文件。

## 检查命令

在 `frontend` 目录执行 `npm run build`，检查 TypeScript 并构建页面。

在仓库根目录执行后端测试：

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m pytest -q backend/tests
```

```bash
# macOS / Linux
.venv/bin/python -m pytest -q backend/tests
```

测试中的工作区使用临时数据库。GitHub Actions 也会运行前端构建与后端测试。
