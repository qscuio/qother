---
name: earthstory-production
description: 编排地球往事从已核实连续旁白到分镜、构图复核、逐镜渲染和声画验收的交接与门槛；用于跨阶段制作或管线规划，不替代写作、视觉设计和具体风格技能，也不自动授权生成或发布。
---
# 地球往事：制作编排

先读本次任务范围、已有授权与质量证据和[统一制作流程](../../../docs/production-workflow.md)。该文件是阶段顺序、输入输出、工具分工、复核失效和交付状态的唯一共用流程；当前人物布局/声音配置仍由[制作配置](../../../docs/production-style.md)管理。本项目按用户“不要等我批准”的指令，在质量关卡通过后自主继续；不可伪记为 user-approved。权限边界见统一流程。不复制第二份流程，不把旧样片参数或单镜试验写成全系列默认。

从已有产物判断当前关卡，交付本次获授权的最小下一步。记录所用版本、缺失证据、允许继续的范围；只有方法更新时只改文档，不改冻结正文、素材、生产状态或安装渲染工具。

## 三项不可互相替代的放行条件

制作对应剧本的封面、完整段落或整片时，先读[身份、覆盖与逐段质量台账](references/identity-coverage-gates.md)：
1. 锁定正文标题与哈希；封面、视频标题卡/品牌行不得自行换成另一个章节名。标题完整不等于封面或视频已修好。
2. 每段及其主张关联实际旁白cue、shot_id与要解释的概念/机制；逐字旁白覆盖和视觉解释覆盖分别审查，不以段数、字幕或码流完整替代画面内容。
3. 合成完整章前，所选范围内各段内容、实际画面和相邻连续性须有同版本内部审查证据。fail/not-run/blocked/缺失证据都不自动放行；已授权的有缺陷预览只能标注其未完成范围，不得称为完成质量。

运行台账机械验证并读取语义/视觉审查报告；机器只核对标题、哈希、ID与引用一致性，不判断画质。当前序章以已有P10作为制作质量对照，不把其材质或镜数规定为全系列模板。按既有delegated-proceed内部复核后继续，不新设逐项用户批准。历史预览的技术结果保留，质量否决另记sidecar。

按任务加载：
- 新写/实质改稿：earthstory-scriptwriting；局部语言修订：earthstory-deslop。
- 理解目标、构图、字体/标注、风格关键帧：earthstory-visual-design 和本镜选定的 style skill。
- 镜内变化、摄影、剪辑和声音规划：earthstory-cinematography。
- 固定主持人身份、动作候选、挑帧和独立透明 PNG：earthstory-character-assets。
- 剪切/变速源素材、对齐声音事件或排查连续帧问题时，读[剪辑来源与连续复核](references/edit-audio-temporal-review.md)；可选网页后端只按[隔离试验](../../../docs/frame-renderer-pilot.md)评估，不替换当前渲染器。
- 程序化制作时读[渲染接口约定](references/render-contract.md)；准备验收时读 cinematography 的[确定性与 QA](../earthstory-cinematography/references/determinism-and-qa.md)。

Skill 提供方法；执行者按单次任务承担职责，同一人可加载多个 skill。这里不创建每画风常驻 agent，不自动部署、发布、安装依赖或调用收费服务。

交接必须区分已实现、实测通过、待执行和阻塞；给产物版本、证据、下一步。真实图像才证明构图，连续播放才验证动态。方法/字段通过不能换成成片通过。行为复核使用[任务案例](tests/behavioral-tests.md)。


