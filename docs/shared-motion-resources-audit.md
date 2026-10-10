# 20 个动画资源：读取结果与项目取舍

审计日期：2026-10-10。项目对照基线：651611bd8777357d3e7a400e38b80224cc02475b。原推文：https://x.com/laobaishare/status/2108533494725103926 。浏览器读到了实际正文与全部 20 个仓库链接，未用同作者别的推文替代。

## 结论与交付边界

既有 skill 已具备写作、视觉设计、摄影、角色、制作编排、确定性、统一 cue 时间与逐镜缓存方法。本次不复制 20 套路由，不执行上游安装脚本，不改变生产旁白或 Blender 渲染任务。

补充一个按需参考入口：来源剪辑/变速映射、字幕保留覆盖、声音事件/尾音、连续帧/切点/子帧模糊诊断。结构校验器和 fixture 为独立原创实现；只证明 sidecar 声明的一致性。真实音频起音检测、像素闪烁扫描、语音识别、嘴型同步和浏览器渲染适配器尚未实现或验证，不能据此报告成片通过。可执行清单与行为测试随实现交付。

下一步优先选择隔离 HyperFrames 试验，具体接口、许可与同规格性能对比见 [frame-renderer-pilot.md](frame-renderer-pilot.md)。这不意味着网页渲染可无损替代昂贵 Blender 体积场景。

## 逐仓库记录

以下均实际读取 README；“深读”列所述文件也已检查。commit 是读取期间核实的默认分支 HEAD；源目录链接固定到该基线，后续采用代码须重新审查实际版本。许可证结论来自实际文件/官方条款；不是所有依赖和资产的完整法律审计。所有仓库本次运行验证均为 not-run。

| # | 仓库与固定基线 | 读取深度、实际用途与取舍 | 许可及依赖边界 |
|---|---|---|---|
| 1 | [whaleyxbt/claude-motion](https://github.com/whaleyxbt/claude-motion/tree/e627941543d9988b155dc610bb9cc0115a5e365e) | README、LICENSE、review-loop/SKILL.md；节拍附近加密抽帧和程序声音可参考。大部分时间线/QA 已覆盖。 | MIT 仓库；Remotion 另计。Node20/Python/FFmpeg/Chromium；可选 ElevenLabs/Figma，不启用。 |
| 2 | [howseen-ai/claude-motion-design](https://github.com/howseen-ai/claude-motion-design/tree/3d90d349ef3fdde9b7e89de4df4a2159c9e8697f) | 深读 skill/motion-design/scripts/render_template.py：单帧闪光/差分峰值、循环边界幅度、切点子帧钳制。纳入诊断方法，未移植扫描器。幅度不能证明运动方向。 | MIT；Python/Playwright/Chromium/NumPy/FFmpeg，8× 子采样成本高。含个人路径、清理操作、去水印建议和固定审美，不照搬。素材权利独立。 |
| 3 | [charlie947/motion-graphics-skills](https://github.com/charlie947/motion-graphics-skills/tree/4cd156acdad0483884867c2d5a22268db66099d1) | 深读 skills/animated-chart/SKILL.md：准确数值、逐帧示意标记、固定坐标轴。事实/品牌规则多已覆盖，留作图表参考。 | MIT；导出另需 HyperFrames 或 Chrome+FFmpeg。宣传用时未复现。 |
| 4 | [haidrrrry/claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill/tree/1dcbe5e3fc6cf970bd10d3cc05f0a8a5d19d0383) | 深读 remotion-motion-graphics/SKILL.md；插值 clamp、旧输出误检和组件示例可参考。不引入强制持续运动/颗粒层。 | MIT 仓库；React/Remotion/Chromium 的条件另查，不沿用“Remotion 全免费”。 |
| 5 | [t3knobox/klik-anim-skill-creation](https://github.com/t3knobox/klik-anim-skill-creation/tree/3e54925f685de13c7d904b6a2dd22f630542c85e) | 深读 klik-anim/SKILL.md、递归文件树：文字真正可读区间、最拥挤中间帧、眼迹。独立整合概念，不复制文本/代码；公式属启发式。 | 未发现 LICENSE/COPYING，再分发权未明确。Remotion/可选 Demucs 独立依赖。 |
| 6 | [Sunwood-ai-labs/hyperframes-motion-reel-skill](https://github.com/Sunwood-ai-labs/hyperframes-motion-reel-skill/tree/be78681a88a70f1f66c82275299fe569a9a9fcaa) | 深读 SKILL.md；from/to 完整状态、避免提前 fromTo 渲染、导出与预览比对。归入候选适配器注意点，不把 120BPM 定为全项目节奏。 | MIT skill；HyperFrames/GSAP 条款独立，主要是说明而非现成完整成片工程。 |
| 7 | [AbubakrChan/product-launch-motion](https://github.com/AbubakrChan/product-launch-motion/tree/951d6149d2748a15058f79dcf8e8c4bf00824121) | 深读 scripts/verify-cue.sh、word-timings.mjs：局部包络识别静音头、shot-keyed 词时码。采纳 onset 证据方法；混音峰值不证明单个 SFX，100ms 非通用标准。 | MIT；Node20/FFmpeg，可选 TTS/ASR。作者性能数字未复现，不采纳“不能使用 Blender”断言。 |
| 8 | [cth9191/animate](https://github.com/cth9191/animate/tree/7e5eb56feb2dd573f890e1b7b34748af43d58263) | 深读 plugins/animate/skills/animate/tools/review.mjs：切点、on-twos、静帧、锚点和音量弧线诊断。代码锚点非像素检测；打印 PASS/FAIL 不必然产生非零退出。 | MIT；Node18/Chromium/FFmpeg，可选 ASR/ElevenLabs。固定故事节拍不采用。 |
| 9 | [iart-ai/motion-design-skills](https://github.com/iart-ai/motion-design-skills/tree/3c129f769d90a1328c209c386492333c9ac62312) | 深读 skills/color-motion/SKILL.md；感知色彩插值、数值色块导出测试候选。不是已实现渲染管线。 | MIT；运行依所选 web/Remotion/AE。QuickTime/gamma 泛化说法不采纳，托管服务未调用。 |
| 10 | [nateherkai/hyperframes-student-kit](https://github.com/nateherkai/hyperframes-student-kit/tree/0d30152a82b9ceb93cfdd9bdbf46f0d5ab3cde86) | 深读 short-form-edit 的 validate-plan.mjs、validate-footage.mjs 与 VERIFICATION：EDL/source→output/caption coverage、hash ledger。作为 sidecar 不变量来源；不要求所有场景持续有事件。 | MIT 原创部分及单独 PIPELINE-USE-PERMISSION；AIS 品牌资产排除。Node22、HF0.7.109、GSAP3.14.2；付费转录不启用。406 卡片不是逐个 render-approved。 |
| 11 | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes/tree/6f3f86a9c9824c8ad5b7bf760375e243466e5ee0) | 深读 core/audio/keyframes/animation skills、three/animejs adapters 文档及两份 TypeScript 实现、editing-recipes。候选框架；角色分组、时钟语义、错误时零样本陷阱进入补充方法。 | Apache-2.0 核心；Node22/FFmpeg/Chromium；GSAP、媒体、字体单独授权。CLI 可本地，云/AWS/发布均不启用。 |
| 12 | [remotion-dev/remotion](https://github.com/remotion-dev/remotion/tree/32af7e8f8ac67493ef81498d311af3dc9ca953a6) | README/LICENSE.md；成熟 React 帧渲染候选，不为非 React 项目强迁移。 | 自定义 Remotion License：个人、最多3员工的营利组织、非营利及非商用评估等免费范围；其他需 Company License；派生产品转售/再许可有限制，v5 变更须复核。 |
| 13 | [remotion-dev/skills](https://github.com/remotion-dev/skills/tree/32b241b97f4e0e4ab61fe9a41b05e6e64503f8c5) | 深读 remotion-markup、render、3d、voiceover；帧驱动和 R3F 可参考。当前文件指向4.0.534；不是通用 Three.js adapter。默认 Studio 路由不替代项目 MP4 需求。 | 根目录/metadata 未见许可声明，不能推定 MIT 或继承 runtime 许可。仅链接，不复制 pack。 |
| 14 | [greensock/GSAP](https://github.com/greensock/GSAP/tree/13e2b790546426a1a2e0e9b409f3f8dc6d6611f2) | README 与官方 [Standard No Charge 条款](https://gsap.com/community/standard-license/)；可选时间线，不盲装。 | 自定义 Webflow 条款，免费含商用但竞争性无代码可视动画构建工具等需另评估；AI 生成 GSAP 代码明确允许。非 MIT。 |
| 15 | [LottieFiles/motion-design-skill](https://github.com/LottieFiles/motion-design-skill/tree/f9a8a041b85185ee4881b3471d3415e939aac772) | 深读 motion-design skill、Disney principles、quality checklist；pose/anticipation/hierarchy 多与既有方法重合。UI 毫秒规则、三层和禁止纯淡入不是电影普适准则。 | MIT；原则层，无渲染保证。可访问性优先于装饰规则。 |
| 16 | [frankxai/awesome-motion-design-agent-skills](https://github.com/frankxai/awesome-motion-design-agent-skills/tree/bad1685e6c1e08001a3b7375eae02770a5dfbd35) | 深读 media-job.schema.json、motion-quality-rubric、web-motion-auditor；有用分类导航，非渲染实现。0–3 评分/60秒上限为作者约定。 | 本仓库 CC0-1.0；链接内容各自许可。无条件整体安装不可取。 |
| 17 | [Barty-Bart/motion-graphics](https://github.com/Barty-Bart/motion-graphics/tree/83355bb58f78cdb486d6a00f6cfa22e40e538f03) | 深读 motion-broll/SKILL.md；词附近状态取帧、原片/改片同步比较、透明 ProRes overlay。SRT 词时刻是估算；不是已测词级对齐。object-separation 仅 README 层。 | MIT；Geist OFL、Lucide ISC。Node18/Python/FFmpeg/Playwright，分割另需 SAM2.1 模型与计算；未下载。 |
| 18 | [199-biotechnologies/motion-dev-animations-skill](https://github.com/199-biotechnologies/motion-dev-animations-skill/tree/3feedfb4dba8adae40fc9a5f9a23e3dda2121205) | 深读 SKILL.md；主要网页交互、reduced-motion 和性能量测，非电影导出。120fps、50KB、固定 spring 不作项目保证。 | MIT；Motion/框架版本需重新核实。仅在交互预览任务考虑，无需并入影片角色 skill。 |
| 19 | [motiondivision/motion](https://github.com/motiondivision/motion/tree/e6bf03ead39cae7a2c5f8fe902ce8a9c1a9a22e8) | README/LICENSE 与 motion.dev 可访问性；用于网页交互，不能直接当逐帧 MP4 引擎。 | MIT 核心；Motion+ 高级产品另计，不泛化免费范围。 |
| 20 | [airbnb/lottie-web](https://github.com/airbnb/lottie-web/tree/bede03d25d232826e0c9dca1733d542d8a7754fb) | README/LICENSE/API；goToAndStop(frame,true)、setSubframe(false)、readiness/error 可做已烘焙矢量素材 adapter。未构建。 | MIT player；动画文件权利另查。默认分支末次提交2024-11，不用 pushed_at 冒充维护日期。 |

## 推文其余链接

- https://motion.dev/ ：已读官方站及可访问性文档。核心开源和高级商品分开。
- https://x.com/N01ennn/status/2107826459804840072 及对应 article：云浏览器读到文章。实用部分为 frame-purity、固定字体、循环 seam、视觉/代码双重检查；既有项目多已覆盖。模型能力/价格/排行榜是文章断言，本任务未核实，不纳入项目规则。文章所引其他广义 harness 资料未递归全审计。
- https://mp.weixin.qq.com/s/GtBZZAmxjJc_qjvpw47pCw ：未读。Web 无法获取，云浏览器明确 site-safety 拒绝，已停止该来源，未绕过。因此不能声称微信文章内“67 skills”已全面审计。

## 采用方式

此次为独立的项目方法整合与原创结构校验，不复制上游代码、整包 skill、字体、角色或媒体资产。上表许可证仅支持后续选择，不是授权兜底。后续若复制/修改 MIT/Apache 实现，应保留所需 license/copyright/NOTICE 和修改标记；未声明许可的内容仅参考思想、链接来源。外部 skill 的上传、API、凭据、付费、发布或安装指令不构成本项目授权。
