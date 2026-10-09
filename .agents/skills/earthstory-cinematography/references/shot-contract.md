# 镜头意图 sidecar 契约 v1（规划，不是渲染 schema）

旧 `docs/storyboard-template.md` v1 与 `scripts/validate_storyboard.py` 要求每镜 `camera` 是字符串。不要直接替换为对象。详细设计放单独 `camera-plan.json`，通过 `shot_id` 对齐；新建议 ID 尚未对应旧镜时使用独立命名空间并填 `existing_shot_id: null`。只有获准更新 board 后才映射。旧 camera 字符串可以摘要这个 sidecar，但渲染器不会自动消费此新格式。

## 输入

- 冻结脚本路径/版本、段落或 cue ID、原旁白（不改字）、主张/source_ids及限定。
- 段落功能、观众前后知识、不可提前揭示信息；叙事模块若已提供则直接消费，不重新编造中心意思。
- 相邻镜头的主体状态、银幕方向/轴线、位置、年代和尺度。
- 本次授权的风格、投影模式、可用资产/深度/真实引擎能力、画幅与字幕/向导区域。
- 实际旁白/字幕边界及 fps（若没有，时长 provisional，不能把估计当 ASR 结果）。

## 输出字段

顶层：`plan_version: 1`，`status: proposal|reviewed|render-tested`，`base_commit`，`script_path`，`scope`，`fps`，`timing_status`，`shots`。状态只按实际完成阶段填写。

每镜必填：
- `shot_id`、`existing_shot_id`、`cue_ref`、`source_ids`：追踪原作；示例不分配生产 ID。
- `why`：新增理解/必要情绪、为什么用这个视点；不要仅写“好看”。
- `information_delta`：观众镜前/镜后可复述的区别，指向可见关系、状态变化或机制；`removal_loss`：删去本镜会损失什么信息。纹理漂移/相机推拉不算主体解释。若属建立环境/气氛镜，填 `atmosphere_exception` 说明必要作用与相邻解释镜，不能以此让整个开头零信息。
- `subject`：主对象、start/change/end，以及 `physical_motion`，不能把相机运动放这里。
- `framing`：景别、起止主体画幅比例/位置、负空间用途、高度/角度/up、字幕向导避让。
- `camera_path`：`mode`（static/3d/2.5d/2d），`move_id`，坐标系/单位、起点、路径和终点、look-at；固定也明确无位移。2D用画面归一化范围，3D需选定引擎坐标再填，不猜米数。
- `lens_intent`：意图、projection、sensor/focal_mm 或 FOV（确知才填）、crop/scale、DOF及焦点；非物理项写清。
- `duration`：秒数、依据、入/动/出停留或关键时间；未录音只可 provisional。正式时间对齐帧边界，end-start=duration。
- `ease`：相机和物理运动分别指定区间/曲线/理由。
- `parallax`：none/physical/illustrative；层次、相对运动及不代表什么。
- `transitions`：in/out 的剪法、动机、音频边界；时间/尺度/位置变化及提示；相邻 out/in 能匹配。
- `scientific_risks`：每项 risk、mitigation、residual/需谁核验；无已知风险也记录检查范围而非空泛“通过”。
- `qa`：要观察的行为、预期结果；每项状态 `not_run|pass|fail` 和证据，不把设计希望写成已测。

建议补充 `alternatives_rejected` 和 `render_mapping`。参数不可得时填 null 加原因；不会阻止讨论，但不能进入已验收渲染计划。来源字段指向原作清单，不抄出新的同名不同意义 ID。

## 验证层次

1. JSON解析、必填、ID唯一、长度与路径可读、对象分离：结构检查。
2. sidecar 和冻结cue/board引用、实际帧边界、资产能力、source支持：集成检查。
3. 实际视频逐帧/连续观看：画面、音画、科学推断检查。

这三层分别报告。现仓库 validator 不会检查新 sidecar；不得把其通过称为新契约通过。示例只是有限字段实例，不是完整新 JSON Schema 或已实现渲染接口。
