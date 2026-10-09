# 《地球往事》动画 Skills / Agents / 引擎选型核查

核查日期：2026-10-09（UTC）。用途：真实地球与人类历史系列的制作方案，当前为约 120 集的工作提纲；不是科幻小说改编。本文是公开资料研究与选型建议，不是已完成的安装、渲染或生产验收记录。

## 1. 结论先行

**建议用一个共用渲染底座承载多个独立风格 skill / agent，先验收一个 20–30 秒无配音样片。**

- 优先方案：**Remotion + 官方 Agent Skills + 项目自己的角色/场景资产库**。它负责时间线、合成、可重复导出，适合长期维护一套系列模板；它不会自动提供合格的历史人物、肢体表演和历史考证。
- 开源替代候选：**HeyGen HyperFrames**。有实际运行时、Studio、测试、发布记录和官方 skills，值得做同题短片对照；目前仍在 0.x 快速变化期。无需因为多一种画风就维护第二套引擎。
- **Lemo-Opuscar、ClaudeAnimationBase、Papermotion 都真实存在**，但三个项目均创建于 2026 年 9 月，不能把近期传播热度等同于成熟生产履历。前两者适合借鉴导演/风格规范与角色模板；Papermotion 适合研究纸片骨骼、物理和场景联动。
- **人物连续性是单独的资产工程**。禁止把“能写动画代码”“有嘴型/表情函数”直接写成“已解决人物动画”。本轮不启用配音、口型同步或在线语音服务。
- 风格层建议拆为纸片 2D、扁平矢量、微缩 3D 三份独立规范及角色 brief；后两者是候选对照风格。每份均输出同一 shot / asset contract，共享事实来源、版本锁定和验收规则。

### 与本项目的硬约束

主画面为 16:9 满幅历史场景。角落主持人保留完整身体，约画面高度 20%，不能依靠放大头像或口部补丁成为主画面。历史场景中的主要叙事人物可以按镜头需要放大；其比例规则与角落主持人应分别定义。静态角色设定、完整姿态和动作连续性先过关，再谈嘴型。事实脚本、分镜、美术、动作和技术 QA 各有独立验收，不让画风演示替代史实证据。

## 2. 成熟度矩阵

下列评级是针对本项目的判断，不是第三方认证。“有测试”只表示读到了测试文件/命令，本轮未运行测试。

| 项目 | 核实的身份与许可证 | 工程证据 | 本项目定位 | 当前分级 |
|---|---|---|---|---|
| Remotion + remotion-dev/skills | 官方引擎与官方技能仓库；引擎为 Remotion 专有许可证下的 source-available，**不是 OSI 开源**；独立 skills 仓库根目录未见 LICENSE，不自行标成 MIT | 引擎自 2020 年存在；实际发布页、monorepo 测试脚本、技能同步与链接校验；技能包含 maps、markup、render、studio | 系列时间线、地图/图解、素材合成、参数化模板与稳定导出；角色另建 | **成熟生产基础候选**，需项目样片验证 |
| heygen-com/hyperframes | HeyGen 官方；Apache-2.0；不是 HeyGen 在线 avatar 服务的同义词 | runtime、engine、Studio、registry、媒体/分镜模块，单元/集成/回归/skill 测试命令及实际测试文件，持续 0.8.x 发布 | HTML/GSAP 的可控场景与镜头；矢量、Lottie、Three.js 接入；可作共享底座替代方案 | **工程基础较强、快速演进候选**，不能称长期系列制作已验证 |
| lemomo-ai/lemo-opuscar | 真实作者仓库；当前 LICENSE 与 package.json 为 MIT；第三方素材另有许可 | DIRECTOR.md、TECHNIQUE.md、43 个风格目录的展示、core 渲染/检查工具、plugin skill；当前 package 无 test script | 学习风格 bible、分镜和逐帧检查流程；筛少量手绘风格，不把 43 种风格带进同一季 | **有价值的实验性导演/风格工具包** |
| JohnHeibel/ClaudeAnimationBase | 真实作者仓库；MIT | p5.js + p5.brush、角色源码、模型表、镜头函数、11 秒 demo 源码、联系表/MP4 渲染器；package 无 test script；无 GitHub Release | 完整角色模板与表演语法的参考，水彩美术试验 | **实验性角色 starter kit** |
| francozanardi/papermotion | 此处特指这个同名仓库；MIT；README 明确声明 experimental | 骨骼、弹簧、IK、确定性物理、纸片绘制、镜头/视差、beats/edit；Vitest 测试有具体断言；无 GitHub Release | 纸片场景运动及可复用动作 primitive 的试验来源 | **实验性引擎**，不直接承诺全系列维护 |
| 未指明作者的“Papermotion”或第三方技能目录摘要 | 搜索中存在多个同名仓库，功能并不相同；目录文案可能过时 | 未给定 canonical repository / commit / LICENSE 时无法审计 | 不纳入依赖清单 | **未验证** |

## 3. 官方底座：能控制什么，不能代替什么

### 3.1 Remotion Agent Skills

官方 [Agent Skills 文档](https://www.remotion.dev/docs/ai/skills) 与 [skills 仓库](https://github.com/remotion-dev/skills) 相互对应。当前技能已按 markup、maps、render、studio 等拆分，不应照抄旧文章里的固定文件数。

实际阅读了 [remotion-markup/SKILL.md](https://github.com/remotion-dev/skills/blob/32b241b97f4e0e4ab61fe9a41b05e6e64503f8c5/skills/remotion-markup/SKILL.md)：动画以帧数驱动，时间换算读取 fps，普通 CSS 动画不能直接视为离线导出可靠。其建议把可复用 scene 注册为 composition，与跨集复用思路相符。

这类 skill 是给编码 agent 的操作规则，不是会自主导演完整动画的独立模型。它最适合封装统一镜头接口、画面安全区、镜头时长、地图/时间轴、资产版本及导出参数。完整人物转身、道具接触、脚步着地、历史服饰一致性仍需资产与动作设计。

维护依据：[v4.0.534 发布页](https://github.com/remotion-dev/remotion/releases/tag/v4.0.534)（2026-10-07）；[引擎 package.json](https://github.com/remotion-dev/remotion/blob/main/package.json) 包含 e2e、SSR、模板、Studio、视觉效果等测试命令，并有 skills 同步/校验任务。本轮没有读取全部测试，也没有执行 CI，因此不声明所有测试通过。

许可注意：[官方 LICENSE](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)、[许可 FAQ](https://www.remotion.dev/docs/license/faq)、[价格页](https://www.remotion.dev/docs/license/pricing) 需在实施前按实际团队结构复核。当前官方列出个人/小团队免费条件与公司许可分界；不要只看到 GitHub 有源码便当作 MIT，也不要把项目规模或个人账号等同于许可资格。

### 3.2 HyperFrames 与 HeyGen

[HeyGen 官方介绍](https://help.heygen.com/en/articles/15001510-hyperframes-x-heygen) 明确区分 HyperFrames 和主视频编辑器。它可用 HTML/CSS/JavaScript 描述合成；本地开源工具链与可选托管、数字人、生成媒体、语音服务分别计费/授权，不能混为一个“永久免费全自动视频 agent”。

实际阅读了 [入口 skill](https://github.com/heygen-com/hyperframes/blob/0576b24c75a604deb9c909407b8328b3df17b0c1/skills/hyperframes/SKILL.md)、[动画 skill](https://github.com/heygen-com/hyperframes/blob/0576b24c75a604deb9c909407b8328b3df17b0c1/skills/hyperframes-animation/SKILL.md)。明确存在暂停且可 seek 的时间线、确定性约束、多运行时 adapter；角色 walk/gesture 指向 Lottie 资产路线。这恰好说明：播放角色资产的框架，不等于自动生产合格角色资产。

工程核查不只看 README：[package.json](https://github.com/heygen-com/hyperframes/blob/0576b24c75a604deb9c909407b8328b3df17b0c1/package.json) 有单元、集成、回归、skills 校验；[compositionReadiness.test.ts](https://github.com/heygen-com/hyperframes/blob/0576b24c75a604deb9c909407b8328b3df17b0c1/packages/core/src/compositionReadiness.test.ts) 实际测试未解码图片/资源就绪状态。目录还包含 storyboard、registry 与媒体模块。这些是工程完整性的积极信号，并不证明历史场景的艺术质量。

选择 HyperFrames 时应关闭或覆盖与项目相冲突的上游默认工作流，尤其自动升级、自动选择其他画风/媒体来源及附带语音流程。系列制作按已验收版本锁定，升级必须重渲代表镜头比对。规范可以借鉴，外部 skill 的指令本身不是项目授权。

## 4. 三个开源候选的实际价值与风险

### 4.1 Lemo-Opuscar：优先借鉴导演方法，不把它当资产工厂

核实了 [DIRECTOR.md](https://github.com/lemomo-ai/lemo-opuscar/blob/4d7014aa7ba7d22c00513052dd996a4f200d5102/DIRECTOR.md)、[core 工具说明](https://github.com/lemomo-ai/lemo-opuscar/blob/4d7014aa7ba7d22c00513052dd996a4f200d5102/core/README.md)、[plugin skill](https://github.com/lemomo-ai/lemo-opuscar/blob/4d7014aa7ba7d22c00513052dd996a4f200d5102/plugin/skills/lemo-opuscar/SKILL.md)。提供的实物包括 treatment、style frame、角色 model sheet、shot list、联系表及文字阅读时间检查；这是比“写一个好看动画”更可迁移的价值。

对本项目的取舍：保留模型表、表演预备动作/跟随动作、道具接触和镜头检查；不机械执行每片必须四种镜头运动等创作规则。上游默认主体需要足够大，本项目应区分场景主角与约 20% 高的角落主持人。上游短片 30–60 秒工作法不能直接推导为 120 集批量成功率。

重要更正：当前 [LICENSE](https://github.com/lemomo-ai/lemo-opuscar/blob/4d7014aa7ba7d22c00513052dd996a4f200d5102/LICENSE) 是 MIT，且保留第三方素材许可提醒；有旧第三方目录仍写 MIT + CC BY 4.0，不能据此标注当前版本。GitHub 的自动许可识别仍可能显示 NOASSERTION，应看固定 commit 的实际文本。样片中的品牌、既有角色、音乐/字体权限不能由代码许可证一并担保。

### 4.2 ClaudeAnimationBase：完整角色系统比补嘴巴更值得学

直接核实 [ANIMATION_GUIDE.md](https://github.com/JohnHeibel/ClaudeAnimationBase/blob/0ac8bf2b31942376cb6b8c4074715595d512acd2/ANIMATION_GUIDE.md)、[demo.js](https://github.com/JohnHeibel/ClaudeAnimationBase/blob/0ac8bf2b31942376cb6b8c4074715595d512acd2/src/scenes/demo.js)、[package.json](https://github.com/JohnHeibel/ClaudeAnimationBase/blob/0ac8bf2b31942376cb6b8c4074715595d512acd2/package.json)。文档围绕预先绘制的角色视角/情绪、完整 shot 与时间纯函数组织；11 秒 demo 的代码实际包含发现、移动、拾取和抛出等连贯事件。

适合学习“角色设定 → 模型表 → 动作词汇 → 分镜 → 联系表”的路线。不能把现成 Clawd 吉祥物当成项目主持人，也不能认为换个名字就完成原创人物设计。其水彩线条抖动可能影响小尺寸主持人轮廓，要在最终显示尺寸复核。README 的 Linux 渲染方案涉及 Chrome `--no-sandbox`；研究不等于批准在生产环境沿用该设置。

### 4.3 Papermotion：最接近纸片场景动力学，仍须隔离试验

核实 [README](https://github.com/francozanardi/papermotion/blob/aafddbe2dbc2b594bcd57c19c4a5a75c5c271be8/README.md)、[package.json](https://github.com/francozanardi/papermotion/blob/aafddbe2dbc2b594bcd57c19c4a5a75c5c271be8/package.json)、[film.test.ts](https://github.com/francozanardi/papermotion/blob/aafddbe2dbc2b594bcd57c19c4a5a75c5c271be8/tests/film.test.ts)、[motion.test.ts](https://github.com/francozanardi/papermotion/blob/aafddbe2dbc2b594bcd57c19c4a5a75c5c271be8/tests/motion.test.ts)。测试有镜头切换、确定性粒子、跳跃落点等明确断言，超出了纯提示词合集。但未执行，且作者公开强调粗糙边缘和 API 变动风险。

最有价值的是 engine/content 分离、动作 primitive、镜头视差、天气及角色对场景的接触，而不是“全靠代码、完全不要资产”的宣传主张。历史系列仍需经考证的衣服、建筑、器物和地图。

关键接入限制：它的 Stage 是固定步长模拟，capture 要求按递增帧序调用；与任意帧采样/并行渲染不是同一个契约。建议独立顺序渲染为镜头素材后合成；若需直接接入，先开发可重置/可确定性重放的 adapter 并测试，不能假设 iframe 嵌入就可靠。其 template 会复制引擎，现有项目不会自动拿到更新；应维护一个经过审查的项目级 fork，不能让每集各自漂移。

## 5. 维护时间与证据边界

下表来自 2026-10-09 GitHub 只读 API；日期是仓库/commit 元数据，不是声称稳定性或发布日期承诺。main 可能继续变化，引用尽量固定 commit。

| 仓库 | 创建日期 | 本轮读到的默认分支最新 commit | Release 核查 |
|---|---|---|---|
| remotion-dev/remotion | 2020-06-23 | 此处不锁定移动中的引擎 main；以 v4.0.534 作为已查发布证据 | v4.0.534，2026-10-07 |
| remotion-dev/skills | 本轮不报告创建日期 | 32b241b97f4e0e4ab61fe9a41b05e6e64503f8c5，2026-10-07 | package 版本 4.0.534，与主引擎技能同步体系对应 |
| heygen-com/hyperframes | 2026-03-10 | 0576b24c75a604deb9c909407b8328b3df17b0c1，2026-10-09 | [v0.8.143](https://github.com/heygen-com/hyperframes/releases/tag/v0.8.143)，2026-10-08；网页搜索缓存曾只显示 v0.8.135，以 API 较新记录为准 |
| lemomo-ai/lemo-opuscar | 2026-09-26 | 4d7014aa7ba7d22c00513052dd996a4f200d5102，2026-10-08 | `web`，2026-09-26，不能当稳定引擎语义版本；package 0.1.0 |
| JohnHeibel/ClaudeAnimationBase | 2026-09-23 | 0ac8bf2b31942376cb6b8c4074715595d512acd2，2026-09-24 | Release API 返回空；package 1.0.0 不是成熟度认证 |
| francozanardi/papermotion | 2026-09-26 | aafddbe2dbc2b594bcd57c19c4a5a75c5c271be8，2026-09-26 | Release API 返回空；package 0.1.0 |

可复核的 API 示例：[HyperFrames releases](https://api.github.com/repos/heygen-com/hyperframes/releases?per_page=1)、[Papermotion 元数据](https://api.github.com/repos/francozanardi/papermotion)、[Lemo 元数据](https://api.github.com/repos/lemomo-ai/lemo-opuscar)、[ClaudeAnimationBase 元数据](https://api.github.com/repos/JohnHeibel/ClaudeAnimationBase)。

### 样片观看记录

**本轮没有完整播放任何样片，也没有安装或渲染任何仓库。** 已阅读官方文档、目录、许可证、部分源码、测试文件和发布元数据。下列只是可观看入口，不能写成已经目测通过：

- [Lemo 官方风格画廊](https://lemomo-ai.github.io/lemo-opuscar/)：可供挑选候选画风；样片表现、镜头质量及素材权限待观看/复核。
- [ClaudeAnimationBase 示例与模型表入口](https://github.com/JohnHeibel/ClaudeAnimationBase)：本轮读了 11 秒 demo 源码，未观看输出影片。
- [Papermotion Gallery](https://github.com/francozanardi/papermotion#gallery)：包含 snow、sea、embers 等视频链接；未观看，不以标题推导其历史叙事能力。
- [HyperFrames Studio](https://www.hyperframes.dev/studio)：官方产品/演示入口；未操作 Studio 或实测编辑-导出往返。

因此，当前已验证的是“项目与工程构件存在”，尚未验证的是“能在目标环境稳定渲染”“画风适合本片”“同一人物跨镜头/跨集不漂移”。不采信 README 中模型名称或一键成功描述作为独立能力证据。

## 6. 最小实现栈与验收方案

### 推荐职责分离

1. **共用底座**：选 Remotion 或 HyperFrames 其一；锁定引擎、浏览器、依赖、字体、fps 与随机种子。优先让技能遵守项目规则，避免多个上游 skill 抢占默认引擎。
2. **共用事实/分镜 contract**：每镜头记录史实来源、年代地点、叙事事件、景别、机位、运动、时间、角色/道具 asset ID、动作起止/接触点、转场与不确定性。
3. **独立风格 skill / agent brief**：纸片 2D、扁平矢量、微缩 3D 分开保存自己的线条、材质、形状、配色、光线、镜头与禁则；输出统一 contract。一个风格文件不是已经部署运行的 agent。
4. **项目级资产库**：主持人完整模型表及姿态、历史人物/服饰、器物、地貌/建筑、动作片段。每件资产有来源、许可、风格版本、历史适用范围、锚点、预览图与已验收镜头。先少量高质量，不从 120 集需求出发一次性画完全部资产。
5. **共用 QA**：满幅/裁切/遮挡、转场空白帧、时间确定性、字体加载、色彩一致、肢体/道具接触与历史事实分别检查；保存关键帧、联系表、完整输出和版本记录。

### 第一个无配音验证片

用同一事实脚本、同一角色资产做 20–30 秒、3–4 镜头：满幅环境建立镜头 → 一个角色和道具发生明确事件 → 一次有动机的推/拉/横移 → 简短结果镜头。角落主持人始终完整且约 20% 高，先只使用少量已批准整姿态，不贴补丁嘴/头。候选风格各自独立输出，不能一条样片中来回换画风。

验收至少包括：

- 三个镜头里同一角色的身材、配色、服饰、视角和道具保持一致。
- 走/举/转身等动作有预备和跟随，手与物体接触无漂移，重要事件能一眼读懂。
- 主画面仍为历史场景，主持人无裁切且不遮挡关键事实；无为“电影感”擅自加黑边。
- 同一固定版本重复导出关键帧一致；失败镜头可单独修复，其他镜头不被改坏。
- 任何物理型候选先证明顺序渲染与重放一致性，再讨论并行合成。
- 看完整速度视频，不仅看海报；额外检查动作中间帧与所有切点前后帧。
- 记录人工返工次数、渲染耗时和资产复用比例，不以模型自己打分代替验收。

达到上述门槛后，再决定是否把某个实验库纳入正式依赖。若失败，先修角色资产/动作设计/镜头规范，不能继续靠增加提示词或换嘴型来掩盖结构问题。配音和口型是后续独立阶段。

## 7. 依赖与公开仓库卫生

本次只保存研究结论与链接，没有安装上游插件、复制其素材、接受新增许可或调用付费媒体服务。实施前应审查安装脚本、网络下载、自动升级与许可；保留必要署名与第三方素材台账。不要把 token、私人素材、无权分发的样片/音乐或用户个人信息写入公开仓库。

此报告的“成熟”“候选”“实验性”为基于上述公开工程证据和项目需求的技术判断；最终视觉质量与目标环境兼容性需用样片验收建立证据。
