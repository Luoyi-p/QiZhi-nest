# 开发约定

- Vue 使用 Composition API 和 TypeScript；页面负责展示，共享数据访问放在 `src/store.ts`，交互状态放在 `src/ui.ts`。
- Python API 输入由 Pydantic 校验；用户提供的数据库值使用参数化 SQL，写操作必须处于事务中。
- 输入链接只接受 http/https；笔记使用文本插值，不直接渲染用户 HTML。
- 每个用户可见写操作必须有失败反馈，成功后更新前端状态；提交期间避免重复请求。
- 新增页面须包含空状态，并保持键盘可操作与手机布局。
- 个人数据、备份、密钥不得进入版本库。使用 `.env.example` 演示配置，禁止提交 `.env`。
- 验证按行为进行：前端 `npm run build`；后端在 `backend` 执行 `python -m pytest -q`。
- 不引入没有当前需求的抽象层；本项目明确面向个人、小规模数据，不承诺大型团队或海量数据能力。
