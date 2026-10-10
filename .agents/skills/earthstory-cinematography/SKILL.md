---
name: earthstory-cinematography
description: Design and review motivated shots, virtual camera movement and editing for 地球往事 documentary storyboards and short demos. Use for shot selection, framing, lens intent, camera paths, spatial continuity, pacing and scientifically honest visual transitions; not for rewriting narration or selecting a new default visual style.
---

# 地球往事：镜头与剪辑

把观众的注意力带到正在发生的关系上。这里整理可迁移的成熟电影技法，不是“所有最佳运镜”、导演风格生成器或必须逐项使用的花样清单。固定镜头可以是最好的决定。

## 进入任务

先读授权范围、冻结脚本、相关 source_id、实际相邻镜头及当前选定风格；查仓库 `AGENTS.md`（若存在），再读 `docs/style-system.md`、`docs/production-style.md`、`docs/storyboard-template.md`。最新明确指令可指定本次 demo 风格，但不自动重写系列默认风格。只优化 skill 时不动作品；只做短 demo 时不重排全片。

## 从意义选镜头

1. 写一句观众本镜结束后应看懂的新关系，以及旁白尚未说出/已经说出的信息。区别主体变化、摄影变化、剪辑跳时；运动本身不是新信息。逐镜写出可指认的新增关系、状态变化或机制，以及“删去本镜会损失什么信息”；纹理漂移、粒子漂亮和相机推拉都不能单独计作解释。少量建立环境/气氛镜可例外，但须说明它建立的方位、观看预期或必要停顿及前后解释镜的衔接；开头不能全由零信息气氛镜构成。
2. 先考虑静态构图是否足够，再用[决策树与构图](references/selection.md)选景别、视点、焦段意图和运动。只读[动作库](references/movement-catalog.md)中相关项；写出起点、揭示、终点，不能只写“电影感、缓慢推进、震撼”。
3. 涉及邻接镜头时读[连续性与节奏](references/editing.md)。先保证空间、时间和因果可理解，再考虑打破惯例。打破惯例要记录目的与重新定向方法。
4. 科学场景必读[科学视觉边界](references/scientific-visuals.md)。艺术复原/示意标识不免除事实责任；不得用宇宙中心火球、错年代星空或伪造尺度替代解释。
5. 按[输入输出契约](references/shot-contract.md)提交逐镜 sidecar；保留现有 storyboard 的字符串 `camera`、`action` 和 ID。没有授权不改 schema、资产锁、脚本、音轨或旧 board。示例见 [宇宙开头](examples/cosmic-opening-camera-plan.json)，它不是 production storyboard，也不是计时承诺。

## 旁白主张到镜头的覆盖

完整段落/章节使用[身份与覆盖台账](../earthstory-production/references/identity-coverage-gates.md)连接paragraph_id、原文主张、旁白cue与shot_id，并写明画面实际解释什么。按理解需要决定一镜或多镜，允许合理跨段镜头；不强制每句拆镜。反查每项限定、机制与结果是否在实际画面中得到表达；文本读完不等于观众已看懂。已有片段重定时、烧录字幕或换音轨时，显式标出旧cue例外并重审对应主张与切点。

## 复核与交付

- 先过静音可读性：观众能辨认主体、变化和空间关系吗？再连旁白检查信息出现、字幕阅读和停顿。避免画面提前泄露尚未解释的结果。
- 检查首/中/末帧及切点前后运动、焦点、遮挡、主观轴线、时间标注；有真实视频才声称完成动态 QA。截图、JSON 和“播放无报错”不能证明成片合格。
- 比较最低复杂度方案与拟选方案：运动或转场没有增加理解/必要情绪就删。无需固定镜数、固定秒数、每镜不同运镜或全片同一缓动。
- 交付 why、参数、前后状态、科学风险及检查状态；未知参数标 provisional，不能编造镜头物理尺寸、已存在素材或已测旁白时长。
- 新 skill 的行为回归见[测试场景](tests/behavioral-tests.md)。来源与实际读取范围见[研究记录](references/sources.md)。要学习具体导演/影片的可检验方法时读[案例索引](references/film-cases.md)，不用人名替代设计。

## 制作规划补充

跨阶段交接统一读[制作流程](../../../docs/production-workflow.md)，不在摄影技能内另设整片生产顺序；具体渲染候选由 earthstory-production 衔接。

需要把冻结稿组织成可审阅的声画方案时，读[制作 treatment 与声音规划](references/treatment-and-sound.md)：比较尚未锁定的声画路径，复用已有逐镜契约，不另起脚本或强制音乐节拍。涉及程序化画面复现与交付检查时，读[确定性与 QA 证据](references/determinism-and-qa.md)。两份参考只补方法，不安装工具、不授权视频制作。

