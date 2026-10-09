# 实际小说与故事写作技能调查

核查日期：2026-10-09。目的：为中文事实地球史系列借鉴叙事方法，而不是寻找排版模板。

## 结论先说

确实已有大量真实故事/小说 SKILL.md。最值得采用的不是“你是世界级作家”或更长禁词表，而是四个工作动作：先搭可理解的因果链；先写小段确定声音；把结构诊断和重写分开；让不知道大纲的初读者模拟指出具体卡顿。

建议首选 wgwtest 的因果/信息顺序，liuxiao 的事实账本与证据式问题报告，haowjy 的编辑分层，danjdewhurst 的隔离初读。中文 snowflake 与 Yunshiro 的分层修订可作补充，但不照搬其网文节拍、身体感配额或禁词阈值。

### 本次做了什么、没做什么

- 先通过网页搜索找到真实项目，再读取 GitHub 默认分支的 SKILL.md、参考文件或具体脚本/测试；不是仅转述技能目录。
- 通过 GitHub REST API 获取仓库树、许可识别与最近提交；内容抓取固定到 commit SHA。
- 只做静态阅读，没有安装、运行仓库代码、调用它们的在线发布功能，未改动写作项目。
- 提交日期只证明近期维护活动，不证明技能最近有文学改进；代码测试也不等于作品读起来好。
- 许可标识来自 GitHub 检测及目录。若要复制大量内容仍应复核完整许可证并保留应有声明。本次建议借鉴方法并重新编写。

## 十个实际项目

### 1. wgwtest/novel-writing：优先借鉴：因果与信息顺序

- 项目：[wgwtest/novel-writing](https://github.com/wgwtest/novel-writing)；类型：actual SKILL.md skill or collection。
- 实读入口：[novel-writing/SKILL.md](https://github.com/wgwtest/novel-writing/blob/838729695148008d42c01bd7c3c0c1a5c15de830/novel-writing/SKILL.md)。
- 可借方法：把场景的因果、谁知道什么、真实约束和作者原有声音分开处理；正文应让第一次读的人能复述事件如何接续。
- 地球史改造：把人物决策链改成自然过程的条件、变化和结果；先让读者知道一个术语指什么，再让它承担解释。每节交代开始与结束状态。
- 风险：SKILL 明确排除 non-fiction，因此只能改造方法；不应安装后原样调用。测试是规则文档契约，不证明文学效果。
- 测试/样例证据：examples/03-style.md 是中英双语最小修改示范，明确自述不是实测模型比较；tests/test_story_outline_contract.py 只检查参考文档必需概念。
- 维护与许可：最近仓库提交 2026-09-26T16:45:58Z，许可 MIT；提交 `838729695148`。
- 其他实读源文件：[novel-writing/references/story-outline-and-causal-summary.md](https://github.com/wgwtest/novel-writing/blob/838729695148008d42c01bd7c3c0c1a5c15de830/novel-writing/references/story-outline-and-causal-summary.md); [novel-writing/references/scene-causality-and-agency.md](https://github.com/wgwtest/novel-writing/blob/838729695148008d42c01bd7c3c0c1a5c15de830/novel-writing/references/scene-causality-and-agency.md); [novel-writing/references/realism-constraints.md](https://github.com/wgwtest/novel-writing/blob/838729695148008d42c01bd7c3c0c1a5c15de830/novel-writing/references/realism-constraints.md); [examples/03-style.md](https://github.com/wgwtest/novel-writing/blob/838729695148008d42c01bd7c3c0c1a5c15de830/examples/03-style.md); [tests/test_story_outline_contract.py](https://github.com/wgwtest/novel-writing/blob/838729695148008d42c01bd7c3c0c1a5c15de830/tests/test_story_outline_contract.py).

### 2. Yunshiro/yunn-skills：借鉴分层修订，拒绝机械阈值

- 项目：[Yunshiro/yunn-skills](https://github.com/Yunshiro/yunn-skills)；类型：actual SKILL.md skill or collection。
- 实读入口：[skills/novel-writer/SKILL.md](https://github.com/Yunshiro/yunn-skills/blob/2d94bc84e26dbcdf45b02390fb1cc061a6cdadab/skills/novel-writer/SKILL.md)。
- 可借方法：六阶段规划、人物、节拍、正文、检查与分层修订；先补有效具体体验，再删套句与复述。
- 地球史改造：先补读者缺少的尺度、物理变化或证据，再删空话；“先加有效信息、再压缩”比一味缩短更有用。
- 风险：检查脚本强制至少12处感知词、3处身体感、8个短段及平均段长25–35字等，会制造新的公式。地球史不得采用这些身体感/爽文指标。
- 测试/样例证据：实读 scripts/check_novel.py；它是正则与计数规则。目录未见该技能独立测试；未运行。
- 维护与许可：最近仓库提交 2026-08-11T11:44:22Z，许可 MIT；提交 `2d94bc84e26d`。
- 其他实读源文件：[skills/novel-writer/references/writing-and-revision.md](https://github.com/Yunshiro/yunn-skills/blob/2d94bc84e26dbcdf45b02390fb1cc061a6cdadab/skills/novel-writer/references/writing-and-revision.md); [skills/novel-writer/scripts/check_novel.py](https://github.com/Yunshiro/yunn-skills/blob/2d94bc84e26dbcdf45b02390fb1cc061a6cdadab/skills/novel-writer/scripts/check_novel.py).

### 3. liuxiao20051106-prog/novel-writer-skill：优先借鉴：事实账本与证据式评审

- 项目：[liuxiao20051106-prog/novel-writer-skill](https://github.com/liuxiao20051106-prog/novel-writer-skill)；类型：actual SKILL.md skill or collection。
- 实读入口：[SKILL.md](https://github.com/liuxiao20051106-prog/novel-writer-skill/blob/6d83102060c01c4db0f337ad81c1b084f9d451d2/SKILL.md)。
- 可借方法：任务路由、十五类技法、连续性模板、事实核查及逐段有证据的验收。去机器腔文档同时警告统计只用于定位。
- 地球史改造：采用来源记录和“问题—证据—影响—最小修复”；科学可能性不能当成弱化词删掉。事实错误不能被语言总分抵消。
- 风险：部分禁词示例仍过度笼统；“仿佛/似乎”在科学推断中不能一刀切删除。通过诊断脚本不代表文字好。
- 测试/样例证据：实读 tests/test_draft_diagnostics.py：字数、标点、重复、已知短语与命令行行为的单测。references/evaluation-and-test-cases.md 是人工行为验收设计，未见本次运行结果。
- 维护与许可：最近仓库提交 2026-09-17T06:03:11Z，许可 MIT；提交 `6d83102060c0`。
- 其他实读源文件：[references/craft-ai-tells.md](https://github.com/liuxiao20051106-prog/novel-writer-skill/blob/6d83102060c01c4db0f337ad81c1b084f9d451d2/references/craft-ai-tells.md); [references/research-and-fact-checking.md](https://github.com/liuxiao20051106-prog/novel-writer-skill/blob/6d83102060c01c4db0f337ad81c1b084f9d451d2/references/research-and-fact-checking.md); [references/evaluation-and-test-cases.md](https://github.com/liuxiao20051106-prog/novel-writer-skill/blob/6d83102060c01c4db0f337ad81c1b084f9d451d2/references/evaluation-and-test-cases.md); [templates/source-log.md](https://github.com/liuxiao20051106-prog/novel-writer-skill/blob/6d83102060c01c4db0f337ad81c1b084f9d451d2/templates/source-log.md); [tests/test_draft_diagnostics.py](https://github.com/liuxiao20051106-prog/novel-writer-skill/blob/6d83102060c01c4db0f337ad81c1b084f9d451d2/tests/test_draft_diagnostics.py).

### 4. renky1025/agent-skills：借鉴：从一句话逐层展开、先试样章

- 项目：[renky1025/agent-skills](https://github.com/renky1025/agent-skills)；类型：actual SKILL.md skill or collection。
- 实读入口：[snowflake-novel-writer/SKILL.md](https://github.com/renky1025/agent-skills/blob/32ce6c04a9c0627343da024b678e05dcacaa17a5/snowflake-novel-writer/SKILL.md)。
- 可借方法：snowflake-novel-writer 从核心概括展开为骨架、关系、场景及声音样章；包含反俗套检查，允许跳步与回退。
- 地球史改造：将核心概括换成每集一个可回答的历史问题，展开因果段落清单；先写几段审美样章再推广整集。
- 风险：角色弧与三幕不是地球史规律；词表把连接词也当问题，需避免为了反套路扭曲科学。
- 测试/样例证据：examples/evals.json 是行为用例规格，不是已经跑过的质量证明；本次未运行。
- 维护与许可：最近仓库提交 2026-09-25T03:09:24Z，许可 MIT；提交 `32ce6c04a9c0`。
- 其他实读源文件：[snowflake-novel-writer/references/snowflake-steps.md](https://github.com/renky1025/agent-skills/blob/32ce6c04a9c0627343da024b678e05dcacaa17a5/snowflake-novel-writer/references/snowflake-steps.md); [snowflake-novel-writer/references/anti-ai-writing.md](https://github.com/renky1025/agent-skills/blob/32ce6c04a9c0627343da024b678e05dcacaa17a5/snowflake-novel-writer/references/anti-ai-writing.md); [snowflake-novel-writer/examples/evals.json](https://github.com/renky1025/agent-skills/blob/32ce6c04a9c0627343da024b678e05dcacaa17a5/snowflake-novel-writer/examples/evals.json).

### 5. danjdewhurst/story-skills：优先借鉴：隔离的初读评估

- 项目：[danjdewhurst/story-skills](https://github.com/danjdewhurst/story-skills)；类型：skill collection with CLI。
- 实读入口：[skills/reader-panel/SKILL.md](https://github.com/danjdewhurst/story-skills/blob/c46163b53df6c3ad13805db424ebf3a52122db75/skills/reader-panel/SKILL.md)。
- 可借方法：独立 scene-craft、revision-continuity、reader-panel；模拟读者只读已经到达的正文，不偷看大纲或结局，反馈必须定位。
- 地球史改造：安排普通中文读者模拟，仅看正文并逐段记录失去方向、疑问、继续读的动力；事实核查另做。修订顺序由结构到句子。
- 风险：功能与CLI非常庞大，短集无需完整实体/注册表架构；模拟读者不是人类盲测，多个模拟角色也非独立人类证据。
- 测试/样例证据：实读 reader-panel 的评估 fixture/checks.json 与示例反馈：有具体段落、simulated 标记、POV异常和长度检查。仓库大量CLI测试存在；未运行、不声称全绿。
- 维护与许可：最近仓库提交 2026-10-08T20:58:39Z，许可 MIT；提交 `c46163b53df6`。
- 其他实读源文件：[skills/scene-craft/SKILL.md](https://github.com/danjdewhurst/story-skills/blob/c46163b53df6c3ad13805db424ebf3a52122db75/skills/scene-craft/SKILL.md); [skills/revision-continuity/SKILL.md](https://github.com/danjdewhurst/story-skills/blob/c46163b53df6c3ad13805db424ebf3a52122db75/skills/revision-continuity/SKILL.md); [evals/examples/reader-panel.md](https://github.com/danjdewhurst/story-skills/blob/c46163b53df6c3ad13805db424ebf3a52122db75/evals/examples/reader-panel.md); [evals/fixtures/reader-panel/checks.json](https://github.com/danjdewhurst/story-skills/blob/c46163b53df6c3ad13805db424ebf3a52122db75/evals/fixtures/reader-panel/checks.json); [examples/salt-and-lantern/story.md](https://github.com/danjdewhurst/story-skills/blob/c46163b53df6c3ad13805db424ebf3a52122db75/examples/salt-and-lantern/story.md); [test/prose.test.js](https://github.com/danjdewhurst/story-skills/blob/c46163b53df6c3ad13805db424ebf3a52122db75/test/prose.test.js).

### 6. haowjy/creative-writing-skills：优先借鉴：诊断、初读、重写三者分开

- 项目：[haowjy/creative-writing-skills](https://github.com/haowjy/creative-writing-skills)；类型：actual SKILL.md skill or collection。
- 实读入口：[cw/skills/story-review/SKILL.md](https://github.com/haowjy/creative-writing-skills/blob/254d4bb9b3b2e50a47def955b6461c06057eedae/cw/skills/story-review/SKILL.md)。
- 可借方法：story-review 选择编辑层次后诊断，reader-sim 单独报告第一遍阅读的感受；要求限定读者与其知识边界。
- 地球史改造：用普通中文科普读者视角检查理解负担、好奇心与流畅度，定位实际句段；先给修订优先级，再改稿。
- 风险：所谓阅读感受仍是模型模拟，不能把角色评分当真实观众反馈或保证提升。
- 测试/样例证据：实读两个 SKILL 及 developmental-edit/line-edit 资源；仓库源文件已验证，本调查不声称有文学效果基准。
- 维护与许可：最近仓库提交 2026-10-08T17:24:15Z，许可 Apache-2.0；提交 `254d4bb9b3b2`。
- 其他实读源文件：[skills/story-review/SKILL.md](https://github.com/haowjy/creative-writing-skills/blob/254d4bb9b3b2e50a47def955b6461c06057eedae/skills/story-review/SKILL.md); [skills/reader-sim/SKILL.md](https://github.com/haowjy/creative-writing-skills/blob/254d4bb9b3b2e50a47def955b6461c06057eedae/skills/reader-sim/SKILL.md); [skills/story-review/resources/developmental-edit.md](https://github.com/haowjy/creative-writing-skills/blob/254d4bb9b3b2e50a47def955b6461c06057eedae/skills/story-review/resources/developmental-edit.md); [skills/story-review/resources/line-edit.md](https://github.com/haowjy/creative-writing-skills/blob/254d4bb9b3b2e50a47def955b6461c06057eedae/skills/story-review/resources/line-edit.md).

### 7. JeroTan/novel-writer-english：次选：系列宪章与事实状态追踪

- 项目：[JeroTan/novel-writer-english](https://github.com/JeroTan/novel-writer-english)；类型：actual SKILL.md skill or collection。
- 实读入口：[SKILL.md](https://github.com/JeroTan/novel-writer-english/blob/6d836f23281e240eed36d50529424e086c8ff42d/SKILL.md)。
- 可借方法：八步从创作宪章、规格、澄清、规划、任务到写作、编辑和跨章审查；角色状态、情节和时间线分文件。
- 地球史改造：轻量采用系列边界、每集开头已知内容、术语表及时间线；把“计划会写什么”与“已发布什么”分开。
- 风险：自称 proven 的方法不能据此算验证；过多 JSON 与任务文件会把写作变成维护工程。
- 测试/样例证据：实读根 SKILL、consistency-checker 和 scene-structure 子技能；树中有 test/mcp-story-library.test.js，属于工具测试，本次未读取或运行它。
- 维护与许可：最近仓库提交 2026-08-09T14:29:31Z，许可 MIT；提交 `6d836f23281e`。
- 其他实读源文件：[src/skills/quality-assurance/consistency-checker/SKILL.md](https://github.com/JeroTan/novel-writer-english/blob/6d836f23281e240eed36d50529424e086c8ff42d/src/skills/quality-assurance/consistency-checker/SKILL.md); [src/skills/writing-techniques/scene-structure/SKILL.md](https://github.com/JeroTan/novel-writer-english/blob/6d836f23281e240eed36d50529424e086c8ff42d/src/skills/writing-techniques/scene-structure/SKILL.md).

### 8. kshanxs/book-writer-skill：次选：邻章全文与有边界的润色

- 项目：[kshanxs/book-writer-skill](https://github.com/kshanxs/book-writer-skill)；类型：actual SKILL.md skill or collection。
- 实读入口：[book-writer/SKILL.md](https://github.com/kshanxs/book-writer-skill/blob/306477e4738a2204fce77fab0aa74e3abb903916/book-writer/SKILL.md)。
- 可借方法：书稿记忆库、相关上下文加载、顺序起草、并行审核；修订时读本章和相邻章节，禁止擅自新增事件。
- 地球史改造：保留相邻集文本/少量风格样本，修订仅改善说明和节奏，不增加未经证实的情景；待核实问题单独留存。
- 风险：author_rules 带个人默认偏好，如固定第三人称、Oxford comma、特定作者声音；研究代理产物被叫主事实源也不够严谨，必须回到原始证据。
- 测试/样例证据：实读 SKILL 与 author_rules、revision_checklist；本次树查询未见专用测试目录，不能宣称自动化验证。
- 维护与许可：最近仓库提交 2026-07-10T11:28:06Z，许可 MIT；提交 `306477e4738a`。
- 其他实读源文件：[book-writer/references/author_rules.md](https://github.com/kshanxs/book-writer-skill/blob/306477e4738a2204fce77fab0aa74e3abb903916/book-writer/references/author_rules.md); [book-writer/references/revision_checklist.md](https://github.com/kshanxs/book-writer-skill/blob/306477e4738a2204fce77fab0aa74e3abb903916/book-writer/references/revision_checklist.md).

### 9. EchoAI-Design/novel-writing-skill：结构参考，暂不复制

- 项目：[EchoAI-Design/novel-writing-skill](https://github.com/EchoAI-Design/novel-writing-skill)；类型：actual SKILL.md skill or collection。
- 实读入口：[SKILL.md](https://github.com/EchoAI-Design/novel-writing-skill/blob/0b9d02ec1b1f5bb79f49d0f722ee123e5236fb4e/SKILL.md)。
- 可借方法：十个编号模块，从项目、世界、人物、情节、卷纲、章纲到正文、审阅、风格与提示词；模块有填写模板。
- 地球史改造：可借每章审阅日志与严重问题优先处理；短集仅需少量文件，不必十目录。
- 风险：更像组织模板，缺少具体改稿证据；API license 为 null，树中未见许可证。只研究思路，复制前需解决许可。
- 测试/样例证据：实读 SKILL、章节审阅 README、风格 README；未见测试或真正完整已写小说样本，模板不是质量评测。
- 维护与许可：最近仓库提交 2026-04-09T20:46:20Z，许可 NO LICENSE FOUND；提交 `0b9d02ec1b1f`。
- 其他实读源文件：[07_chapter_reviews/README.md](https://github.com/EchoAI-Design/novel-writing-skill/blob/0b9d02ec1b1f5bb79f49d0f722ee123e5236fb4e/07_chapter_reviews/README.md); [08_style_control/README.md](https://github.com/EchoAI-Design/novel-writing-skill/blob/0b9d02ec1b1f5bb79f49d0f722ee123e5236fb4e/08_style_control/README.md).

### 10. xin-yi33/-novel-writer-skill：仅借轻量连续性，不采用发布自动化

- 项目：[xin-yi33/-novel-writer-skill](https://github.com/xin-yi33/-novel-writer-skill)；类型：actual SKILL.md skill or collection。
- 实读入口：[novel-writer/SKILL.md](https://github.com/xin-yi33/-novel-writer-skill/blob/d01ba0d157740de1557dbbb084877cc0ab7f3341/novel-writer/SKILL.md)。
- 可借方法：细纲写作加 bible、摘要、近期全文、状态与人物卡；续写从断点恢复，压缩长期材料。
- 地球史改造：使用一个事实/术语表、上一集正文与当前集纲；时间线与不确定性应由证据维护，不被摘要压缩抹去。
- 风险：固定压缩公式与“超过三章移除全文”不具普适性；在线发布能力无关写作质量，不应因读技能就触发。
- 测试/样例证据：实读 SKILL、writing-quality-guide 与 long-form-writing；未见测试证明摘要压缩保持事实，文档声称不丢失不能照信。
- 维护与许可：最近仓库提交 2026-09-18T04:00:29Z，许可 MIT；提交 `d01ba0d15774`。
- 其他实读源文件：[novel-writer/references/flows/writing-quality-guide.md](https://github.com/xin-yi33/-novel-writer-skill/blob/d01ba0d157740de1557dbbb084877cc0ab7f3341/novel-writer/references/flows/writing-quality-guide.md); [novel-writer/references/flows/long-form-writing.md](https://github.com/xin-yi33/-novel-writer-skill/blob/d01ba0d157740de1557dbbb084877cc0ab7f3341/novel-writer/references/flows/long-form-writing.md).

## 怎么转成中文事实叙事，而不写成小说

1. 核心问题：每集先用一句普通话说“读完会明白什么变化、为什么值得知道”。不能只列时代名称。
2. 事实底稿：给时间、规模、机制、证据和争议分别找来源。标明事实、模型解释、仍不确定的地方。任何拟人或视觉类比都不得改变这些边界。
3. 因果纲：每段只承担一个实质变化。记录起始条件、发生什么、凭什么认为如此、如何接到下一段。时间先后不能自动写成因果；未确定的因果直接限定。
4. 信息顺序：先给读者可理解的对象/现象，再给名称与必要机制；必要时先交代尺度。不要一开头堆概念，也不要每段补一段百科。
5. 样段定声：写两三段，读出节奏与解释密度。具体来自可证实细节，不来自虚构见证者。自然过程不分配动机；没有证据的对白、感官或个体动作不写。
6. 分层修订：先修事实和因果，再修缺失的解释，随后删复述、套句与无功能比喻，最后朗读查中文节奏。保留科学所需的“可能”“约”“目前证据”。
7. 初读检验：只给模拟读者正文，不给研究报告或大纲；要求标出第一处不懂、想跳过、指代不清、仍想继续的问题。结论注明是模拟反馈，不能包装成人类验证。
8. 连载记忆：仅维护事实/术语表、每集核心问题、已讲过的解释、相邻集正文与待解疑问。避免为短系列引入庞大角色数据库。

## 不值得照搬的常见做法

- 每章必须反转、必须留钩子、每若干字有爽点：可能让事实叙事变成假悬念。
- 固定感官词数量、短段数量、比喻上限：指标本身会成为另一种机器模板。
- 所有“然而”“似乎”“仿佛”都禁：削弱真实中文表达，也可能删掉关键的不确定性。
- 多角色模拟都给高分：不等于真实读者喜欢。
- 持续压缩摘要而不回查证据：会把初稿设想误升级成事实。
- 通用“专业作家”“publishable”“proven”表述：是提示词角色或作者主张，不能当性能证据。

## 补充中文专项

另有中文专项调查，覆盖 Tomsawyerhu/Chinese-WebNovel-Skill、xiaofeng-928/chinese-longnovel-skill、XINGANLIU/web-novel-writing-skill、zhougz520/novel-architect、PenglongHuang/chinese-novelist-skill。该报告进一步支持：先修结构再修机器腔；把创作计划与已接受文本分开；确定性检查与文学判断分开。对应的公开链接见[中文专项报告](chinese-novel-workflows.md)。这里的十个候选不把额外项目冒充为已深入检查。

## 最小验收建议

用相同事实材料做旧稿/新稿短段盲序比较，分别评“是否一次读懂”“能否复述因果”“哪里想跳过”“是否有无来源细节”。自动诊断仅提供重复/句长的线索。科学事实错误或无来源编造一票否决，其他文风判断由实际文本与人的偏好决定。
