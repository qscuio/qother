# 设计研究与采用边界

研究日期：2026-10-09。这里只链接、归纳方法并写本项目原创工作规则，不安装外部仓库、复制 skill 正文、字体、截图或实现代码。公开可读不自动意味着可重新分发。下列 main 链接可能更新；复核来源时记录读取日期与实际范围，不将搜索摘要当完整阅读。

## 已读的官方来源

### Anthropic frontend-design

- [官方正文](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)
- [该 skill 的 LICENSE.txt](https://github.com/anthropics/skills/blob/main/skills/frontend-design/LICENSE.txt)：已完整读取，Apache-2.0。
- 阅读范围：全文；主题驱动的设计、字体/结构选择、设计计划与自查段落重点对照。
- 本项目迁移：让视觉选择由题材产生，设计前明确方向，检查所有结构是否承担信息。不是移植其网页 hero、CSS 建议或某组默认配色。
- 不复制正文。如果以后要分发其改写版本或代码，应另行满足许可证副本、变更及相关归属通知要求；本记录不代替这些义务。

### OpenAI Frontend App Builder

- [官方正文](https://github.com/openai/plugins/blob/main/plugins/build-web-apps/skills/frontend-app-builder/SKILL.md)
- [所属插件 README](https://github.com/openai/plugins/blob/main/plugins/build-web-apps/README.md)
- 阅读范围：两份全文，重点概念设计、实现忠实度和截图核对。
- 本项目迁移：把认可的视觉目标与实际输出逐项比较，区分功能可运行和视觉通过。
- 不迁移：强制 Image Gen、React/Vite、网站整页设计、按钮/导航、10/10口号或UI特定禁项。纪录片可用现有3D渲染器低成本做设计静帧。
- 许可：本次尝试仓库 LICENSE、LICENSE.md、插件及 skill 的 LICENSE.txt 未取得有效许可证正文；未确认该文件重分发许可。因此仅链接并独立概述，不 vendoring、不安装、不复制代码或资产。
- [旧 OpenAI skills README](https://github.com/openai/skills/blob/main/README.md)已完整读取；当前提示迁往 plugins，并要求逐 skill 看许可证。不能用旧仓库的假定许可覆盖新插件。

### IBM Carbon Motion（v10 归档文档）

- [官方 Motion overview](https://v10.carbondesignsystem.com/guidelines/motion/overview/)
- 阅读范围：正文 Style、Easing、Duration、Motion design strategy、Evaluation checklist、Adaptive interface motion design；未运行示例组件或包。
- 本项目迁移：运动承担理解/引导功能，相关运动协同，显著运动留给关键变化。
- 不迁移：UI毫秒时长、交互反馈曲线或弹跳限制作为自然过程的物理规律。所读为归档版，不称最新规范。
- 许可：网页显示 IBM 版权与条款链接；未核实媒体/代码重用许可，不复制图、动画、代码。

### W3C 可读性参考

- [Understanding SC 1.4.3 Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- 阅读范围：In Brief、Success Criterion、Intent、抗锯齿及背景图说明；不是WCAG全标准阅读或合规评估。
- 本项目迁移：用亮度对比而非色相差别检查文字，留意细字体和变化背景。4.5:1/大字3:1只作为实用检查，不能宣称成片因此获得认证。
- 许可：未取得许可页面正文；只引用链接和简短事实概述，不复制规范正文或图示。

## 本项目证据与原创规则

已通过 GitHub 读取 qscuio/qother 基准 81df47a91b6c2c05fa5fbc7bc0f2d3e72e104c23 的两个 skill 入口、docs/style-system.md 和 docs/production-style.md；与现有镜头 sidecar 交接，不改旧脚本或分镜。

这次反馈涉及宇宙段落中的纸感适配、无解释作用的黄色云纹理、蓝底卡片网格及平面空间。归纳的是内容与形式脱节、信息缺失、空间和层次不足；不是蓝色/黄色/二维在所有题材都错误。灰黑底、低饱和和真3D也不自动合格。

最多两款低成本静帧、八项门槛、同镜三帧及行为测试是本项目原创的生产控制方法，不声称外部来源规定了这些数量。技术渲染成功不能替代审美或科学验收；能力状态需每次实际检查，不在本 skill 锁定某机器/引擎永久可用。

未采用：Material 3 motion 页面本次仅返回需 JavaScript 的提示；不把未读正文列为已吸收方法。未完整研读其他社区UI skills，不做排名或“最佳技能”断言。
