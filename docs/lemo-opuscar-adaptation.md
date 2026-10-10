# Lemo-Opuscar：吸收长处，补足缺口

2026-10-10；仅文档与技能规则集成。基线 qother `ec4b67b7e0976907ff4fd18862ea472b447d591f`；上游固定为 `a75e2b3384cded87955c8743b5a59db06ea491a8`，不随 main 自动升级。

## 真正新增什么

原有 scriptwriting / deslop / document-editing 已覆盖非虚构结构、语言和文稿分层，cinematography 已有逐镜 why、景别、角度、时长与科学边界，visual-design 已有关键帧和双批准关卡。本次不再复制一套导演总纲，也不改冻结主稿或旧分镜。

| 判断 | 上游证据 | 本仓库适配 / 原有缺口 |
|---|---|---|
| 适配 | [DIRECTOR §§2–5](https://github.com/lemomo-ai/lemo-opuscar/blob/a75e2b3384cded87955c8743b5a59db06ea491a8/DIRECTOR.md)：先形成 treatment、备选结构、再看 demo；model sheet/style frames | [制作意图参考](../.agents/skills/earthstory-cinematography/references/treatment-and-sound.md)：只比较尚未决定的声画路线；已有契约直接复用；角色模型表按需，不重新设计锁定主持人 |
| 采用并约束 | [DIRECTOR §§6–7](https://github.com/lemomo-ai/lemo-opuscar/blob/a75e2b3384cded87955c8743b5a59db06ea491a8/DIRECTOR.md)：声音设计表、层次、阅读时间 | 同一参考补声音表、静默目的与实际旁白/阅读时间；不让音乐网格驱动冻结文字，不要求每个动作配声 |
| 适配 | [TECHNIQUE §§2–3、8](https://github.com/lemomo-ai/lemo-opuscar/blob/a75e2b3384cded87955c8743b5a59db06ea491a8/TECHNIQUE.md)：render(t)、统一投影/时间线、检查循环 | [确定性与 QA](../.agents/skills/earthstory-cinematography/references/determinism-and-qa.md)：乱序帧复现、标注锚点、统一 cue、检查证据；保留本项目分镜缓存/重建要求 |
| 选择性采用 | [dataviz §§1、3、6、8–9](https://github.com/lemomo-ai/lemo-opuscar/blob/a75e2b3384cded87955c8743b5a59db06ea491a8/styles/dataviz/STYLE.md)：真实数据、按数据选图、语义色带、数据空间标注 | [数据编码参考](../.agents/skills/earthstory-flat-vector/references/data-storytelling.md)：补单位/口径、缺失值、变尺/形变追踪；作为现有 flat-vector 的方法，不引入纸笔风格或复制完整 demo |
| 独立候选 | [iso-infographic §§1–6、8–9](https://github.com/lemomo-ai/lemo-opuscar/blob/a75e2b3384cded87955c8743b5a59db06ea491a8/styles/iso-infographic/STYLE.md)：固定等距、三面色、剖面、图标计数、focus/context | [独立 skill](../.agents/skills/earthstory-iso-infographic/SKILL.md) + [角色说明](agents/earthstory-iso-infographic.md)；manifest 标 proposed-unvalidated，填补系统剖面候选而非替代真实三维或改默认风格 |
| 暂缓 | [blueprint §§2、5、8](https://github.com/lemomo-ai/lemo-opuscar/blob/a75e2b3384cded87955c8743b5a59db06ea491a8/styles/blueprint/STYLE.md)：线型、剖切、工程注释 | 可在确有器械解释需求时评估局部技术图；本次不新增 blueprint skill，不引入全片蓝底/科技边栏 |

## 不迁移的规则与能力边界

- [bootstrap skill](https://github.com/lemomo-ai/lemo-opuscar/blob/a75e2b3384cded87955c8743b5a59db06ea491a8/plugin/skills/lemo-opuscar/SKILL.md) 是获取库/安装依赖入口；[setup.sh](https://github.com/lemomo-ai/lemo-opuscar/blob/a75e2b3384cded87955c8743b5a59db06ea491a8/plugin/skills/lemo-opuscar/scripts/setup.sh) 含克隆、更新及管理副本的 hard reset。它不是43个独立 agent。此次不导入、不执行安装脚本，不下载运行时或模型。
- DIRECTOR 的固定四种运镜、两次静默/声音转场、音乐先行、固定时长/字幕公式及默认免批准不适合作为本项目强制规范。保留有理由的静态镜头、中文实际阅读与分镜/构图双批准。
- 上游 TTS 默认/示例音色不是本项目选型；男性标准普通话、本次不启用声音克隆及已锁角色以[当前配置](production-style.md)为准。只纠正活跃规范中的旧位置/音色状态，不改历史资产与旧分镜。
- [readcheck.mjs](https://github.com/lemomo-ai/lemo-opuscar/blob/a75e2b3384cded87955c8743b5a59db06ea491a8/core/render/readcheck.mjs) 依据自报 TEXTS 矩形与文字计算首次连续在画时长，不是 OCR、重叠遮挡或视觉质量验收；打字机自报全文也不能证明字已完整显示。缺 TEXTS 返回未检查，不算通过。
- [asr_check.py](https://github.com/lemomo-ai/lemo-opuscar/blob/a75e2b3384cded87955c8743b5a59db06ea491a8/core/tts/asr_check.py) 的中文默认 difflib 阈值0.92及可覆盖期望文本只是识别比对，不证明数字/事实正确。不得为通过检查修改冻结正文或把识别错误变成标准答案。
- [mux.sh](https://github.com/lemomo-ai/lemo-opuscar/blob/a75e2b3384cded87955c8743b5a59db06ea491a8/core/render/mux.sh) 的静音/响度超标分支会警告后继续，最终可返回0；“命令成功”不能概括为严格音频质量通过。[video.mjs](https://github.com/lemomo-ai/lemo-opuscar/blob/a75e2b3384cded87955c8743b5a59db06ea491a8/core/render/video.mjs) 并行覆盖整段帧区间，不提供本项目按 shot_id 的缓存契约。
- TECHNIQUE 的GPU/three.js描述没有在本次环境实测；渲染、音频和动态 QA 均 not-run。此集成没有增加可执行制作管线。
- 不复制示例音乐、字体、fan-film资产或用户原始主持人。每个实际素材单独核对许可/署名/修改/传播条件；上游“仅 CC0/CC BY/OFL”不升级为全局禁令，CC BY-SA 等须按具体权利条件评估。

## 来源与许可

上述参考与等距 skill 是选择性中文适配，Copyright (c) 2026 LemoLab，MIT。完整原许可及第三方素材说明保留在 [lemo-opuscar-LICENSE.txt](third-party/lemo-opuscar-LICENSE.txt)。此通知仅标记列出的改编部分，不宣称整个 qother 或第三方素材改用 MIT。上游文档、相关代码只读核验，未执行。

## 验证与下一步

[行为案例与验证记录](tests/lemo-opuscar-adaptation.md)区分结构检查、人工规则走查和未运行的制作测试。新候选尚需具体选题、用户选择和真实单镜头验证；此次文档集成不授权这些后续制作。
