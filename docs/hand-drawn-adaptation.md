# 手绘库的选择性吸收

> 当前执行规则更新（2026-10-10）：用户已要求本项目“不要等我批准”。下文原集成/测试中关于分镜、构图与样片等待批准的描述仅保留历史背景；当前按[统一流程](production-workflow.md)完成内部质量复核后自主继续，不伪改过去的批准或测试事实。费用、私有外传、冻结稿与对外发布边界不因此放开。

研究日期：2026-10-10。状态：文档与候选规范；未安装、执行或验证上游生成流程，未生成图片、视频或调用模型。既有风格选择、冻结脚本、分镜、素材与配音保持原状。

## 作者、版本与许可

感谢 **yang0** 的 [handraw-style](https://github.com/yang0/handraw-style)；研究固定到 [4eb29e2fcea3d9595d2f67b363e30ffdea338027](https://github.com/yang0/handraw-style/tree/4eb29e2fcea3d9595d2f67b363e30ffdea338027)。根 LICENSE 自称 “MIT License (with Attribution Requirement)”，GitHub 元数据为 NOASSERTION；本项目按**带额外署名要求的 MIT 变体**记录，不标为标准 MIT。完整原文保存在 [yang0 许可](third-party/yang0-handraw-style-LICENSE.txt)。其附加条款要求受益或派生项目明确保留作者与仓库链接，可列在文档、仓库、产品描述或界面。此处及仓库首页保留明显署名；没有擅自给画面加署名水印，也没有采用上游每次回复都附画廊入口的规则。这是本次仓库文档适配的范围记录，并非对所有未来输出授权的法律保证；未来若分发其代码、图片、字体或其他资产，仍须逐项核对权利与附带要求。

感谢 **liulei / threerocks** 的 [hand-drawn-styles](https://github.com/threerocks/hand-drawn-styles)；研究固定到 [4132988b8596bfa36321c970a4472d4e3bb25d96](https://github.com/threerocks/hand-drawn-styles/tree/4132988b8596bfa36321c970a4472d4e3bb25d96)。根 LICENSE 为标准 MIT，Copyright (c) 2026 liulei；完整原文保存在 [threerocks 许可](third-party/threerocks-hand-drawn-styles-LICENSE.txt)。文档改编不等于其中示例图的独立权利核实。

## 仓库实查

- yang0：[根入口](https://github.com/yang0/handraw-style/blob/4eb29e2fcea3d9595d2f67b363e30ffdea338027/SKILL.md)路由到[实际 skill](https://github.com/yang0/handraw-style/blob/4eb29e2fcea3d9595d2f67b363e30ffdea338027/skills/handdraw-style-prompter/SKILL.md)，还有风格、配色、版式 JSON、图库和 Python 工具。README 宣称 327 种风格；实际数据使用 FA/FB 等分组 ID，不能把旧展示编号不经解析地复制为项目 style_id。数据与展示数量可能不同，本项目不承诺迁入完整菜单。其贡献在于分开决定内容、材料、色彩、布局，并要求理由关联具体主题，而非“高级手绘”空话。
- threerocks：[实际 skill](https://github.com/threerocks/hand-drawn-styles/blob/4132988b8596bfa36321c970a4472d4e3bb25d96/SKILL.md)、[协议](https://github.com/threerocks/hand-drawn-styles/blob/4132988b8596bfa36321c970a4472d4e3bb25d96/PROTOCOL.md)、[配方](https://github.com/threerocks/hand-drawn-styles/blob/4132988b8596bfa36321c970a4472d4e3bb25d96/STYLES.md)分离；当前是编号 1–20 加 3.1，仓库简短描述仍提到五种，不宜据此判断内容。3.1/19/20 带固定锚点和正式调用约束，其他多数输出提示词；不是动画引擎。
- 依赖检查限于读源码：yang0 的 prompt_style.py 使用 Python 标准库及库内 layout_library/resolve_reference 和资源文件；threerocks 的 render_prompt.py、hosted_images.py、validate_style_20_asset.py 使用标准库及相互导入，hosted_images 含网络下载与缓存。未审计全部依赖、未安装运行。后者固定资产在外部托管，生产流程还要求参考图输入与指定模型条件；这些均未迁入、未声称可用。
- 上游称“已验证”“高保真”或某模型可激活画风，仅是上游报告；本项目没有复测，不继承其分数、兼容性或质量保证。也不把其参考图/模板当作科学依据。

## 与现有规范的重合和增益

| 现有入口 | 选择性增益 | 不迁入 |
| --- | --- | --- |
| visual-design | 内容、材料、色板、布局、文字分开说明；风格参考与身份/证据参考分离；同主体及跨主体检查 | 自动生图、全库推荐、固定模型能力假设、冗长安装路由 |
| paper-2d | 纸纹尺度与材质连续性、边缘和填色分工、先去纹理看结构 | #13 立体纸雕的卷纸人物、凸鼻、民俗饰品和3D厚度，避免把纸雕错并为纸片二维 |
| natural-history-plate | 墨线优先保持形态、稀疏强调与塑形排线区分、透明局部色不掩证据 | #10 的禁止排线、#17 的巨大虹膜/手账纸框、艺术家签名、未知器官与颜色 |
| flat-vector | #18 的大轮廓阅读与动作弧线方法 | 蓝橙限色、人物体型、七成空白、纸纹、阴影人物模板；既有纯矢量定义不变 |
| scientific-drawing | 既有线型/剖切/标尺规则已经足够，本轮不另改 | 用随意墨线代替测量边界；把示意画成真实空间 |

不新增独立 hand-drawn style：这个大类没有比现有纸片、矢量、结构图、博物志更清楚的单一材料与验收边界。也不复制每个编号为 agent。若未来要独立水彩场景或真正纸雕，应先以具体镜头证明差异，再单独定义候选与批准范围。

## 本地入口与保留边界

[手绘语法](../.agents/skills/earthstory-visual-design/references/hand-drawn-grammar.md)是唯一新增方法参考，已有 visual-design / paper-2d / flat-vector / natural-history-plate 按需进入。不装上游 skill、不搬图库、字体、生成脚本、模型配置或固定参考图；本项目的中文文字在可校对排版层完成。上游声称不能摘句混配的生产规则没有被当作我们独立规范的调用协议；本项目不是其兼容封装，也不宣称复现原画风。

当前制作约束继续以 [production-style](production-style.md) 为准：16:9 满幅事件场景，原始完整男性主持人右下圆形角标（当前约250 px布局），无空侧栏/底栏；现成男性普通话，冻结稿不改。私人角色图和录音不发布为方法资产。分镜与构图关键帧同版双批准后才能制作视频。此次没有启动生产，也没有变更这些批准状态。

## 验证

[行为检查场景](tests/hand-drawn-adaptation.md)用于审阅边界；静态路径、技能 frontmatter 和范围检查可运行，但不能证明视觉质量。实际样图、跨主体图像回归、动画稳定性和音频验收本次全部 not-run。
