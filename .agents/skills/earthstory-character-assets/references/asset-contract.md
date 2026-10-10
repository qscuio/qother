# 素材交接与批准契约

改编标记：本文件由 sprite-gen（Apache-2.0，commit 3dc080aa8faa8b5a6dfe865b1247c047761f8fd1）的方法改写为 qother 的素材记录与批准契约，非上游原文；增加本项目证据分级和独立PNG交付规则。[来源与许可](../../../../docs/sprite-gen-adaptation.md)。

这是制作记录约定，当前未实现新的可执行资产验证器。仓库既有 storyboard 验证器只检查它自己的字段，不能据此声称下列内容已验证。

## 每个动作版本必须能追溯
- identity：character_id、reference asset_id/version/真实 SHA-256、来源标识、权利依据、参考批准证据；未确认权利不能进入发布。
- state：state_id、asset_id、不可变 version、方向/左右配饰、cyclic 或 one-shot、开始/结束姿态和转换条件。
- generation：provider、model、seed（不可取得时明确 unavailable，不能伪造）、生成/导入时间、请求参数、原件来源及哈希。私人文件与敏感元数据留在授权的私有资产存储，不上传公开方法仓库。
- geometry：完整主画布宽高、坐标原点、固定 pivot、统一 scale、基线、安全边距；frame 逐项记录 source_id/hash、processed hash、变换和方法版本。
- playback：有序独立 PNG 列表、每帧 duration_ms、总时长、loop；从视频取帧另记 source timestamp。PNG 列表是顺序依据，不能由文件名排序或 atlas 网格猜测。
- curation：候选池、选择/拒绝/替换及原因、源帧顺序、复核人/时间、选择记录版本。变化产生新资产版本，旧批准不自动继承。
- rights：每个来源的来源页/提供者、许可或具体授权范围、可否修改/公开/商业使用及未决限制；公开仓库许可不自动覆盖用户角色或生成服务条款。
- review_status：candidate / rejected / qa-accepted / superseded；QA 另记 pass / fail / not-run、复核者、证据和用途。proceed_authority=delegated-proceed 支持当前项目内部质量通过后继续；user_approval 独立记录真实批准者、时间、版本和证据，未获用户具体批准写 not-reviewed，不能用 QA 通过填 approved。已有历史 approval 字段保留原事实，不伪迁移。

## 三种证据，不可混称
1. static-frame：逐张检查身份（脸型/发型/西装/配饰）、头颈连接、肢体数量和长度、手指、完整性、实际 alpha 与固定尺度。必须检查每帧，抽三帧不能代表全组。
2. time-sampled-video：若有实际视频，列出确切取样时点、帧号、哈希和查看到的现象。它只证明这些时点，不证明中间无闪烁或完整动态通过；没有视频就记 not-run。
3. continuous-motion：以最终顺序和实际速度播放整个状态，并查看逐帧问题区间；检查动作可读性、节奏、身份/光线漂移、支点抖动、衣边闪烁、接地，以及 cyclic 的末首连接或 one-shot 边界。记录实际审阅工具、播放/解码能力及证据范围。工具只能展示静帧时明确 not-run，不用自行声称“看过播放”。

可安排独立第二次审阅，但审阅者也须具备对应证据能力；多数意见不能覆盖已发现的破损。哈希证明文件相同，颜色直方图/dHash 只能做粗略异常提示，不能证明脸部身份一致或像素级身份锁定；上游 identity histogram 阈值默认0即未启用，不是自动验收保障。

## 交付与正式复用
保留原始独立 PNG（无损源帧）、完整透明 processed 候选和选择记录；正式交付以 accepted/<asset_id>/<version>/<state>/ 的独立透明 PNG + manifest + QA/继续权限记录（历史 approved 目录可保留，但不伪称新版本已获用户批准）为主。atlas PNG + 帧矩形/顺序/时长 manifest 是可选便捷副本，不能成为唯一资产，也不能把棋盘联系表当透明素材。

所有帧、manifest、QA 和选择记录作为同一版本准备齐后再一次发布索引，避免消费一半新一半旧的素材；这里是待实现/验证的交付要求，不声称已有原子发布程序。消费者按完整版本哈希验证，并确认使用已应用 curation 的导出文件。源文件变动、加工方式/顺序/时长/循环政策改变均需新版本及受影响的静态/动态复核。

storyboard 的 assets 仍使用现有 {asset_id, version} 契约；具体 state 应给独立 asset_id，并在资产清单指向对应完整 manifest。不要随意增加 style_id 或修改 v1 验证器来容纳动作状态。跨镜延续同状态、切入 neutral 或 one-shot 结束时保持 continuity 与真实结束姿态一致。

制作前核对状态具体版本和质量证据、同版分镜/构图内部检查。用户已授权本项目不等待逐项批准；通过质量关卡按 delegated-proceed 继续，不能把它写成用户已看过素材。对外发布仍须独立核对权利和发布授权。资产批准不授予视频生成/上传/服务付费等额外权限。没有质量通过的动态状态或真实可用绑定时，沿用静态完整图层方式，不把绑定作为生成帧动作的唯一合法路径。
