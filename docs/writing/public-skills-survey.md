# Earthstory：公开写作 skills 核验与取舍

核验日期：2026-10-09。范围：通过搜索引擎、skills.sh 等目录发现候选，再打开作者仓库中的实际 SKILL.md 与可取得的许可文件。本文是与中文科学纪录片相关的定向调查，不是穷尽全网的清单，也不是运行效果排名。本次没有安装或执行任何第三方 skill。

## 结论

建议自己编写一个小而明确的中文纪录片写作 skill，组合四种能力：叙事正文、科学主张核对、口语编辑、交付检查。现成技能各有所长，但没有一个经本次验证能直接同时保证中文旁白好听、地学事实准确、Markdown 好读。

首要目标是内容本身好看、听得懂，而非排版漂亮。不能把“去 AI 味”缩减成禁词替换：删掉套话以后，仍须有值得讲的细节、顺着读者疑问展开的解释、具体而准确的过程，以及自然的叙事节奏。humanizer 适合作为后期诊断；内容取舍、章节推进和作者判断必须先完成。样式规则全部通过也可能得到一篇平庸的稿子。

最值得借鉴的是：doc-coauthoring 的独立读者测试；scientific-writing 的主张—证据映射；humanizer 的重复修辞诊断；scriptwriting 的朗读检查。Word/PDF 技能解决文件制作；Remotion 技能解决视频实现。它们不能代替写作能力。

下文“维护状态”只描述取得的证据。页面可读取、近期被搜索引擎抓取，不等于作者近期提交代码；未核实提交日期的地方明确保留未知。许可证信息是出处记录，不代替法律意见。新 skill 应原创，不拼贴上游指令。

## 一、直接帮助写作与编辑

### 1. Anthropic — doc-coauthoring

- 类型：真正的文档协作 skill。
- 原文件：[skills/doc-coauthoring/SKILL.md](https://github.com/anthropics/skills/blob/main/skills/doc-coauthoring/SKILL.md)。
- 方法：先补齐作者上下文，再分节修改，最后让没有对话背景的读者回答问题，暴露歧义与遗漏。
- 用于 Earthstory：让测试者只看旁白，复述本集问题、关键因果和结尾；参考资料放附录，正文独立成立。
- 局限：原流程偏规格说明、提案等文档；逐节询问会拖慢一次性重写，应调整成合并评审。
- 许可：官方仓库说明许多示例为 Apache-2.0，但本次未取得此目录的专用许可证，不据此批量复制。见[仓库许可说明](https://github.com/anthropics/skills#about-this-repository)。
- 状态：当前 main 原文件可读；具体最后提交日期未核实。

### 2. K-Dense-AI — scientific-writing

- 类型：真正的科研写作与审计 skill。
- 原文件：[skills/scientific-writing/SKILL.md](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-writing/SKILL.md)。
- 方法：先建证据与主张记录，再起草；修改措辞后重新检查支持关系，区别结果与解释。
- 用于 Earthstory：每个重要数字、年代、机制和争议主张在独立事实表中留来源、定位和可信度；正文只保留影响理解的不确定性。
- 局限：面向学术稿件；IMRAD、作者声明、临床报告检查不能直接套入纪录片。源文件要求的人类核验不能被自动 lint 冒名完成。
- 许可与状态：原文件标 MIT，版本 2.3，标注 last-reviewed 2026-10-01。版本与日期是作者自述，并非本次运行证明。只借鉴证据管理方法，不采用其自带科学事实作为本片证据。

### 3. blader — humanizer

- 类型：真正的语言编辑 skill。
- 原文件：[SKILL.md](https://github.com/blader/humanizer/blob/main/SKILL.md)。
- 方法：检查结构性重复、假反驳、空洞强调、机械排比；重写后核对事实是否增删。
- 用于 Earthstory：优先修掉无来由的“不是……而是……”、一段一个结语、先宣布重要再说内容；保留真正澄清科学误解的对比。
- 局限：这是一套编辑启发式，不是 AI 检测器，也不是科学准确性证明；不能为增加“人味”编造人物、感受或细节。
- 许可与状态：原文件标 MIT、v3.1.0；[仓库](https://github.com/blader/humanizer)可见版本记录。未核实该版本发布日。

### 4. ComposioHQ — content-research-writer

- 类型：真正的通用内容写作 skill，存放在兼有目录功能的项目中。
- 原文件：[content-research-writer/SKILL.md](https://github.com/ComposioHQ/awesome-claude-skills/blob/master/content-research-writer/SKILL.md)。
- 方法：明确受众和目的，先大纲与研究缺口，再逐节检查清楚程度、衔接、证据及声音一致性。
- 用于 Earthstory：保留研究缺口清单、具体句子修改和整体连贯性检查。
- 局限：文章开场、号召行动等范式偏内容营销。文件中数字和专家引语属于示例，不能拿来当真实证据；必须独立核验。
- 许可：[README](https://github.com/ComposioHQ/awesome-claude-skills#license)称仓库 Apache-2.0，同时警示单项可能不同；本次未取得本项专用许可证。只借鉴方法。
- 状态：当前 master 原文件可读；精确最后提交日期未核实。

### 5. bmcgauley — scriptwriting

- 类型：真正的跨媒介脚本 skill，含教育视频、纪录片与播客模板。
- 原文件：[scriptwriting/SKILL.md](https://github.com/bmcgauley/SKILLs/blob/master/scriptwriting/SKILL.md)。
- 方法：为听觉写作，减少单句负荷，术语先解释；以朗读检查拗口、呼吸、节奏和时长。
- 用于 Earthstory：旁白先写成连贯段落，再制作镜头稿；逐段朗读，检验一遍能否听明白。
- 局限：英语单词数规则不能直接变成中文汉字限制；钩子、价值承诺、行动号召和固定三幕比例也不应机械移植。
- 许可：在实际 skill 和[仓库主页](https://github.com/bmcgauley/SKILLs)中未确认许可证；不复制或再分发正文。
- 状态：当前 master 原文件可读；维护频率和最后提交日期未知。

### 6. XucroYuri — how-to-make-script

- 类型：真正的剧本技能与知识库项目，根 skill 负责选择具体工作流。
- 原文件：[SKILL.md](https://github.com/XucroYuri/how-to-make-script/blob/master/SKILL.md)。
- 方法：先区分媒介、阶段、输出和限制，只加载当前任务需要的知识；草稿、诊断、润色分别处理。
- 用于 Earthstory：明确“阅读版旁白”“录音稿”“分镜表”是不同交付物，避免把生产信息塞进阅读稿。
- 局限：主要覆盖叙事、商业、互动剧本；本次只核实入口和项目结构，未逐一评测全部子技能，不应宣称其纪录片质量已验证。
- 许可：[根 LICENSE](https://github.com/XucroYuri/how-to-make-script/blob/master/LICENSE)为 MIT，署名 XucroYuri 2026。
- 状态：当前 master 可读，项目含测试与评审结构；精确最后提交日期未核实。

## 二、制作我们自己的 skill

### 7. OpenAI — skill-creator

- 类型：真正的 skill 构建技能，不是写作风格技能。
- 原文件：[skills/.system/skill-creator/SKILL.md](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)。
- 可借鉴：主说明简短，例子具体，详细参考资料按需读取；用真实任务迭代，并验证元数据与命名。
- 对本项目：核心工作流留在 SKILL.md，中文改写案例、证据表规范、评审标准分开放；不要堆入与本片无关的通用教科书。
- 局限：结构验证不证明旁白好听，也不证明事实正确。
- 许可：[专用 LICENSE.txt](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/LICENSE.txt)为 Apache-2.0。
- 状态：当前 main 可读；精确最后提交日期未核实。

### 8. Anthropic — skill-creator

- 类型：真正的 skill 构建与评测技能。
- 原文件：[skills/skill-creator/SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)。
- 可借鉴：同一任务对比有无 skill 的结果，观察用户真正关心的产物；写作优劣用定性判断，不强行做成简单分数。
- 对本项目：比较旧稿与新稿的可读性、听觉理解、信息保留；再用另一集题材检查是否过拟合第一集。
- 局限：工具和运行机制面向 Claude，不能照搬命令；基线与新稿应保有同等信息条件。
- 许可：[专用 LICENSE.txt](https://github.com/anthropics/skills/blob/main/skills/skill-creator/LICENSE.txt)为 Apache-2.0。
- 状态：当前 main 可读；精确最后提交日期未核实。

## 三、排版和制作工具：用途不同

### 9. OpenAI — 历史 doc skill

- 类型：真正的 DOCX 文件制作 skill，但已从公开主分支移除。
- 原文件：[删除前 45d05d7 版本](https://github.com/openai/skills/blob/45d05d7/skills/.curated/doc/SKILL.md)，路径 skills/.curated/doc/SKILL.md。
- 方法：导出后逐页渲染检查，反复修正版式；有助于交付 Word/PDF，不能修复旁白叙事。
- 状态：[删除提交 228962a](https://github.com/openai/skills/commit/228962a)确认移除该目录；[官方提交列表](https://github.com/openai/skills/commits)将其列于 2026-05-01。仍在推荐 main 分支旧安装路径的目录已过时。
- 许可：旧路径专用许可本次获取失败，保留未核实；不分发历史包。

### 10. Anthropic — docx

- 类型：真正的 Word 生成与编辑 skill。
- 原文件：[skills/docx/SKILL.md](https://github.com/anthropics/skills/blob/main/skills/docx/SKILL.md)。
- 用途：DOCX 表格、标题、编辑与渲染检查。适合未来制作审阅文档，本次 Markdown 旁白不必引入。
- 许可：[LICENSE.txt](https://github.com/anthropics/skills/blob/main/skills/docx/LICENSE.txt)为专有许可，限制复制、派生与分发；不得放入自有公开技能包。
- 状态：当前 main 原文件可读；精确最后提交日期未核实。

### 11. Anthropic — pdf

- 类型：真正的 PDF 读取、生成和处理 skill。
- 原文件：[skills/pdf/SKILL.md](https://github.com/anthropics/skills/blob/main/skills/pdf/SKILL.md)。
- 用途：处理 PDF 内容和文件；不提供中文科学旁白的叙事方法。
- 许可：[LICENSE.txt](https://github.com/anthropics/skills/blob/main/skills/pdf/LICENSE.txt)为专有许可；同样不复制到本项目。
- 状态：当前 main 原文件可读；精确最后提交日期未核实。

### 12. Remotion — remotion-best-practices

- 类型：真正的视频制作技能入口，负责转到动画、字幕、渲染等实现技能。
- 原文件：[skills/remotion-best-practices/SKILL.md](https://github.com/remotion-dev/skills/blob/main/skills/remotion-best-practices/SKILL.md)。
- 用途：把已确定的脚本实现为 React 视频、字幕、地图与渲染流程。
- 对本项目：放在脚本确认之后；不能用“视频 skill”之名替代故事、事实和中文表达检查。
- 许可：在本次读取的仓库主页与 package.json 中未确认，不能以产品代码许可推定技能文本许可。
- 状态：文件自报版本 4.0.527；本次未验证其发布时间。精确路径已核验，旧 skills/remotion/SKILL.md 链接不能替代当前入口。

## 应用到 Earthstory 的原创设计

1. 先从已核验事实确定一个观众可以追踪的问题，以具体过程推进章节。
2. 先完成无技术注释打断的阅读版旁白。时码、镜头、字幕、声音提示进入独立生产稿。
3. 把事实映射放在独立资料表：主张、来源、页码或段落、证据支持范围、是否推断、待确认事项。改写后检查事实是否变化。
4. 不确定性就近而简明地出现一次；没有影响科学含义的免责声明从正文移出。绝不为了流畅把假说说成定论。
5. 用可见的对象与动词解释抽象概念；类比只帮助理解，不生成新事实或虚假因果。
6. 对正文朗读、计时；不强制每 15 秒切一块，不按英语单词数限制中文。
7. 让没有研究背景的读者复述因果链，指出首次不懂的词；让事实审稿人检查主张与来源。
8. 用第一集和至少一种不同题材做检查。事实完整、引用可追踪、版面检查只是底线，不能冒充读者喜欢或专业配音实测。

## 发现目录与排除原则

[skills.sh 的 scientific-writing](https://www.skills.sh/k-dense-ai/scientific-agent-skills/scientific-writing)与[content-research-writer](https://www.skills.sh/composiohq/awesome-claude-skills/content-research-writer)用于发现来源，最终判断回到作者原文件。收藏量和安装量没有被用作质量证明。

未将只列链接的 awesome list、仅摘录模板的镜像页、带“AI agent”名称但无可核验技能文件的项目视作已验证 skill。也未采用营销转化、病毒式标题或消除 AI 痕迹的检测分数作为本片写作目标。
