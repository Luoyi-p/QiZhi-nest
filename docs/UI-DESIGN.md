# Nest UI · 2026-09-15—2026-09-20

## 本次范围

使用用户指定的 [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) 重构 Vue 前端。保留工作台、学习路线、资料、笔记、项目、时间线、设置共七个页面及现有数据行为；不改 API / SQLite，不添加网络字体、组件框架、云服务或远程发布。

## 设计检索与取舍

实际读取其 `SKILL.md`、`references/quick-reference.md`、`references/pro-rules.md`，使用仓库版本 `15de38fb70bc80ae9276fa7703b48ae861a672e6` 的 Python 检索脚本。

可复现命令（`<skill>` 为该仓库 `.claude/skills/ui-ux-pro-max` 的绝对路径）：

```text
python <skill>/scripts/search.py "personal knowledge workspace minimal" --design-system -p Nest --density 6 -f markdown
python <skill>/scripts/search.py "productivity dashboard minimal" --design-system -p Nest --density 6 -f markdown
python <skill>/scripts/search.py "forms keyboard components" --stack vue
```

第一次检索的 Minimalism & Swiss Style、黑白灰 + 蓝色强调符合长期使用的个人知识工作台。生成器的布局建议却偏营销页；收窄查询后仍是产品展示布局，因此**没有照搬或持久化不适用的营销布局**。页面结构采用既有工作台的信息优先级，属于人工适配，不声称来自命中的 dashboard 模板。

Vue 检索匹配 3.5.x：保留已有 Composition API、TypeScript、原生表单和数字 v-model。当前表单不复杂，不为本轮外观工作增加验证库。

## 采用的视觉规则

- 黑白灰为基础，蓝色用于主要动作、当前导航与进度；路线分类继续保留文字和图标，颜色不是唯一标识。
- 主文字 `#18181B`，背景 `#FAFAFA`，卡片 `#FFFFFF`，强调 `#2563EB`，次级文字 `#626774`。
- 以浅灰侧栏区分导航，以深蓝随手记区块承载次要入口。统计使用分隔线形成一组，不给每个数字附加装饰卡片。
- 系统字体优先 Segoe UI / PingFang SC / Microsoft YaHei；不采用检索生成的 Google Fonts 网络导入。
- 4/8px 间距节奏、统一圆角和边界；所有页面复用同一套 CSS，删除旧的多层样式覆盖。
- 375 / 768 / 1024 / 1440px 检查；小屏导航抽屉、卡片单列、表单输入 16px，长标题和标签允许换行。
- Lucide 图标沿用；控件有焦点和状态反馈，保留错误/加载/空状态；支持 reduced-motion。
- 增加跳转正文链接、路由切换焦点、手机导航焦点循环与返回。表单使用原生 dialog 焦点管理，底部操作区留出滚动焦点空间。

## 验证

- `npm run build`：TypeScript 检查与 Vite 构建。
- 后端 `pytest`：17 项通过；存在上游 anyio 别名弃用提示，不影响通过。
- 浏览器对七页 × 四种宽度进行 DOM 布局检查，无横向溢出；检查桌面/手机画面。
- 验证搜索打开资料、状态筛选空状态、路线表单必填校验、Escape 关闭与返回触发按钮；不创建或改写个人记录。
- 仅实现当前浅色主题；不声称已实现或测试深色主题。

## 最终回归与审查（2026-09-20）

- 重启本地预览后再次完成生产构建。
- 375px 下验证导航的 Shift+Tab / Tab 首尾循环、Escape 返回打开按钮、关闭时解除背景禁用和滚动锁；选择资料库后焦点进入正文。
- 手机资料编辑弹窗的字段、滚动区域和底部保存/取消按钮可用，表单输入字号为 16px；校验与取消测试没有写入个人记录。
- 减少动画通过 CSS 媒体规则提供；没有进行系统级动画设置切换或屏幕阅读器专项测试。

### Standards

独立审查报告：未发现可操作的规范或可维护性问题，文档规则硬性违规 0 项，启发式问题 0 项。

### Spec

独立需求审查因额度限制没有完成，不能称为独立审查通过。主代理对照 `docs/SPEC.md`、用户本轮 UI 请求和代码差异人工复核：API、数据库和数据访问层不变，七页入口与现有编辑/筛选/导入导出功能保留，未发现待处理的需求回归。浏览器没有重演导入导出写操作，相关数据逻辑由现有后端测试覆盖。
