---
name: earthstory-visual-design
description: Design and critique 地球往事 documentary styleframes, visual hierarchy, Chinese typography, scientific annotations, color and 3D spatial readability before animation. Use for visual redesign and styleframe approval gates; not for building dashboard UI, rewriting narration or imposing a series-wide art style.
---

# 地球往事：视觉设计

让画面本身交代对象、关系和变化。迁移 frontend/UI design 的设计推理与画面复核能力，不把纪录片包装成网页、卡片仪表盘或科技面板。真三维是空间表达的能力，不能替代构图和信息设计。

## 输入与边界

先读本次明确需求、选定风格、冻结脚本版本、来源限定、相邻镜头和已有验收图。查仓库 AGENTS.md（若有）及 docs/style-system.md、docs/production-style.md。旧文档中的暂定纸感/向导基线不能覆盖当前具体任务的明确指令；本镜试验也不自动改写系列默认。只做 skill 时不改脚本、board、资产锁或成片。

接收 $earthstory-scriptwriting 的段落功能、前后知识与事实边界；和 $earthstory-cinematography 共用 shot_id、camera/action 语义及首中末状态。本 skill 决定画面组织和可读性；镜头路径、剪辑与跨镜连续性仍由 cinematography 负责。科学问题回到原来源，冻结稿适配问题只报告、不擅改。

## 先设计，再动起来

1. 写一个视觉简报：观众应看懂的关系；证据对象；最容易误读的地方；实际观看尺寸；当前可用渲染方式。先选视觉语法（实体空间、剖面、地图、定量图解等），再选择颜色、字体和纹理。无需每镜都用真3D；当前任务要求真3D时不得用平面缩放替代。
2. 为这一镜确定主体/说明/环境层级、主要留白、文字角色、色彩含义及空间证据。用[设计与审查门槛](references/styleframe-review.md)约束具体决策。每项装饰回答“删去会失去哪条信息或必要观看感受”；仅为显得复杂而存在的边框、光晕、编号或网格应删。
3. 最多提出两种低成本静帧方案；方向明确就只做一款。先真实渲染关键帧并目视检查，不以文字方案、工具名称或模型自评分充当视觉证据。若没法渲染，只交标明未验证的方案和阻断，不伪称静帧通过。
4. 修复最高影响缺陷再继续：科学误读、无信息增量、主体不清、文字不可读、空间伪造或遮挡错误均阻止进入动画。记录“缺陷→图中位置/证据→修复→复查结果”，不用总分抵销阻断。用户要求先看/等待批准时停在静帧，不自行继续。
5. 选定静帧后制作同镜起/中/末三个状态帧，复核身份、比例、光照、标注锚点和空间关系；将相机变化与物理变化分开。三帧内部检查通过不等于用户批准，也不等于运动、音画同步或整片已通过；进入视频制作还须通过下面的质量关卡。用户仅要求一张图时只交一张，并标明三帧检查尚未执行。

## 对应剧本与实际解释

为封面/标题卡读取冻结正文的准确标题，不从工作目录“第一章”等临时名称推断章节身份。标题、封面主视觉权利与缩略可读性分别复核。现有章完整制作需使用[身份与覆盖台账](../earthstory-production/references/identity-coverage-gates.md)，为主张记录实际解释画面和同版本视觉证据；旁白/字幕齐全不能填充visual pass。

先与本次已有质量基准比较可读主体、材质、空间关系与过程表达；当前序章使用P10作质量对照，不要求其他物质画成相同粒子盘。选取任务中真正不同的视觉类型做代表性验证，再扩展相应范围；不规定通用小镜头数量或固定色板。有缺陷或未检查段落不得借技术QA通过进入完成质量合成。

## 分镜与构图质量关卡

本项目用户已要求“不要等我批准”。按[统一制作流程](../../../docs/production-workflow.md)完成同版分镜与构图内部复核后，在既有任务范围内自主继续制作；审阅包可交用户查看，但不逐镜等点头。若用户之后对具体任务明确要求先看/暂停，则遵守更新的范围指令。

审阅包保留包版本、稳定 shot_id、逐镜 keyframe_id/图像版本、旁白或音轨版本、时间区间、相机/对象动作，确保实际画面对应分镜。分镜检查、真实关键帧检查分别记录 pass/fail/not-run 与证据，技术可运行不能代替质量。缺实际图像或有阻断缺陷则先修复，不因免等待而跳过关卡。

继续权限记 delegated-proceed；只有用户真实审阅并认可具体版本才记 user-approved。锁定通过内部检查的版本，成片逐镜比较。构图/运镜/时长变化只重审受影响部分，内部通过后继续，不重新等用户；冻结旁白、身份基准与外部分享/费用等边界保持。纯实现修复仍需复查。单图或技能维护不额外启动整集。

## 交付

保留轻量 sidecar：shot_id、脚本版本/来源、理解目标、视觉语法、色彩与文字角色、物体/相机变化、静帧路径、缺陷与检查状态、下一步允许范围。真实检查写 passed/failed；缺少图像或动态素材写 not-run。不要新增生产 schema 或将试验参数写成永久审美规则。

首次建立或修改本 skill 时运行[行为回归](tests/behavioral-tests.md)；来源、许可和未迁移的规则见[研究记录](references/sources.md)。

需要量化图表时，读[数据编码与标注参考](../earthstory-flat-vector/references/data-storytelling.md)，只迁移读图方法，不自动选定扁平风格。需要等距系统剖面时可比较 `$earthstory-iso-infographic`，它是未验证候选，不能满足明确要求的真实透视三维。程序化标注漂移或抽帧复现问题见[确定性与 QA 证据](../earthstory-cinematography/references/determinism-and-qa.md)。

明确比较手绘材料、墨线或图谱排版时，读[手绘语法](references/hand-drawn-grammar.md)。按既有风格分支选择，不自动把手绘铺到真实三维镜头，也不因参考库有许多编号就创建同等数量的 agents。

