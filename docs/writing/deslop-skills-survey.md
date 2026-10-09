# Earthstory：deslop / humanizer 写作编辑技能核验

核验日期：2026-10-09。只读研究，实际读取六个作者仓库的 SKILL.md、README.md 与根 LICENSE；没有安装 skill，也没有执行上游脚本。下面的完整提交号来自 git ls-remote，技能与许可随后按该提交读取；搜索引擎的提交历史有旧缓存，未用它推定当前版本。本文是适配判断，不是运行成绩或 AI 检测有效性评测。

## 建议

创建独立、原创的 earthstory-deslop，把它放在内容写作之后，用于编辑已有中文旁白；保留 content writer 负责资料选择、故事推进与新内容。最值得借鉴 op7418/Humanizer-zh 的语义保护，以及 humanizer 的段落级重复诊断。不要把六套规则直接叠加成越来越长的禁词表。

编辑目标是更清楚、具体、连贯、好听；不判断作者身份，不承诺通过 AI 检测，不为“人味”虚构见闻、情绪、数字、专家或来源。空洞内容应退回内容写作环节补研究，deslop 不偷偷扩写。

## 六个实际技能

### 1. blader/humanizer：英文 humanizer，v3.1.0

- 实际文件：[SKILL.md](https://github.com/blader/humanizer/blob/225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8/SKILL.md)
- 核验提交：`225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8`
- 方法：通读诊断、整段重写、朗读、检查信息增删；识别假对比、重复结语、夸大与无来源权威。写作样本优先。
- 取舍：适合借鉴编辑流程。其标点禁令和允许添作者反应的部分不作 Earthstory 默认；事实旁白不添加情绪。
- 许可证据：[LICENSE](https://github.com/blader/humanizer/blob/225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8/LICENSE)。MIT；Copyright (c) 2025 Siqi Chen。
- 项目说明：[README](https://github.com/blader/humanizer/blob/225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8/README.md)

### 2. op7418/Humanizer-zh：中文编辑，优先参考

- 实际文件：[SKILL.md](https://github.com/op7418/Humanizer-zh/blob/f4518a8eab97b8bfebc66a89d34320a89bef6930/SKILL.md)
- 核验提交：`f4518a8eab97b8bfebc66a89d34320a89bef6930`
- 方法：明确保护否定、范围、条件、时间、归因和确定程度；每种模式配不应修改的边界。已经通顺的段落可保留。
- 取舍：最适合科学旁白的编辑约束，但保留主张不等于已核实主张；事实审核仍是独立步骤。
- 许可证据：[LICENSE](https://github.com/op7418/Humanizer-zh/blob/f4518a8eab97b8bfebc66a89d34320a89bef6930/LICENSE)。MIT；Copyright (c) 2026 歸藏。
- 项目说明：[README](https://github.com/op7418/Humanizer-zh/blob/f4518a8eab97b8bfebc66a89d34320a89bef6930/README.md)

### 3. ai-zixun/humanizer-zh：中文长文与翻译腔编辑

- 实际文件：[SKILL.md](https://github.com/ai-zixun/humanizer-zh/blob/f75f1ac9735c4f10da1bba0148e0ea7228c5c3b3/SKILL.md)
- 核验提交：`f75f1ac9735c4f10da1bba0148e0ea7228c5c3b3`
- 方法：从全文主线及各段功能入手，处理翻译句法、机械段落节奏和空泛收尾，再朗读。
- 取舍：借鉴篇章诊断；不采用默认禁止破折号或名家声音菜单。补足因果只能补表达，不能创造证据；用户未要求时不套作者人格。
- 许可证据：[LICENSE](https://github.com/ai-zixun/humanizer-zh/blob/f75f1ac9735c4f10da1bba0148e0ea7228c5c3b3/LICENSE)。MIT；Copyright (c) 2026 aizixun。
- 项目说明：[README](https://github.com/ai-zixun/humanizer-zh/blob/f75f1ac9735c4f10da1bba0148e0ea7228c5c3b3/README.md)

### 4. stephenturner/skill-deslop：英文散文与科学写作 deslop

- 实际文件：[SKILL.md](https://github.com/stephenturner/skill-deslop/blob/a906154bef375d9d49ed2ad7da13b2db16f0d3d2/SKILL.md)
- 核验提交：`a906154bef375d9d49ed2ad7da13b2db16f0d3d2`
- 方法：关注冗余、虚假主语、节奏、文体与具体性；将结构问题和词语问题分开。
- 取舍：不直接采用：固定少用三项、强制主动和人物主语会误伤地学；科学改写示例引入原句没有的模型排名、地理与集成结论，说明具体化必须受证据约束。自评分不是质量证明。
- 许可证据：[LICENSE](https://github.com/stephenturner/skill-deslop/blob/a906154bef375d9d49ed2ad7da13b2db16f0d3d2/LICENSE)。MIT；Copyright (c) 2026 Stephen D. Turner。
- 项目说明：[README](https://github.com/stephenturner/skill-deslop/blob/a906154bef375d9d49ed2ad7da13b2db16f0d3d2/README.md)

### 5. ProfSynapse/DeSlop：带审计流程的散文 deslop，v1.2.0

- 实际文件：[SKILL.md](https://github.com/ProfSynapse/DeSlop/blob/6b71b32109def051408623b281774ff4f8e99a01/skills/deslop/SKILL.md)
- 核验提交：`6b71b32109def051408623b281774ff4f8e99a01`
- 方法：区分模式候选与编辑判断，要求先排除误报；保留主张、核对新增事实，按调用模式交付。
- 取舍：可借鉴逐项说明保留或修改的理由。无需搬入整套脚本、默认审批停顿及机械标点关卡；本次没有运行这些脚本。
- 许可证据：[LICENSE](https://github.com/ProfSynapse/DeSlop/blob/6b71b32109def051408623b281774ff4f8e99a01/LICENSE)。根 LICENSE 为 MIT，列 Siqi Chen 2025 与 Joseph Rosenbaum 2026；另载 GOV.UK 摘录的 OGL v3.0。README Attribution 还说明 Wikipedia 来源为 CC BY-SA 4.0，不能把所有素材一概当成单一 MIT 原创。
- 项目说明：[README](https://github.com/ProfSynapse/DeSlop/blob/6b71b32109def051408623b281774ff4f8e99a01/README.md)

### 6. fayerman-source/deslop：法律与专业文本 plain-English 编辑

- 实际文件：[SKILL.md](https://github.com/fayerman-source/deslop/blob/bab1b1470fe76183f44ad8e69f7dcb253e84cc52/SKILL.md)
- 核验提交：`bab1b1470fe76183f44ad8e69f7dcb253e84cc52`
- 方法：保持主谓距离、精简名词化表达、保护术语含义及术语一致性。
- 取舍：只借鉴清晰表达与术语保护方法。法律内容未作本项目事实依据；英语字数、可读性分数、法律格式与强制主题句不适合直接套中文纪录片。
- 许可证据：[LICENSE](https://github.com/fayerman-source/deslop/blob/bab1b1470fe76183f44ad8e69f7dcb253e84cc52/LICENSE)。MIT；Copyright (c) 2026 Legal Plain English Contributors。
- 项目说明：[README](https://github.com/fayerman-source/deslop/blob/bab1b1470fe76183f44ad8e69f7dcb253e84cc52/README.md)

## 与 coding deslop 区分

同名不代表同功能。例如 [brianlovin/agent-config 的 deslop](https://github.com/brianlovin/agent-config/blob/main/skills/deslop/SKILL.md) 检查分支 diff、注释、防御代码与类型转换；[kubb 的 deslop](https://github.com/kubb-labs/kubb/blob/main/.agents/skills/deslop/SKILL.md) 也明确把 prose/Markdown 交给 humanizer。这些不能代替纪录片编辑。本次六个主体候选均为文字编辑技能。

## earthstory-deslop 原创工作流建议

1. 确定边界：输入现成旁白、目标受众、允许改动幅度、必要时附文风样本。审阅只给建议，明确要求改稿才写回。
2. 建立简短的语义底稿：关键主张、数字/单位、年代、比较对象、术语、否定、归因、条件与不确定性。它用于检查编辑损失，不重复生产一份研究报告。
3. 通篇标出问题：每段在推进哪个疑问？是否重复上一段？哪里只宣布重要而没有解释？哪里强行反驳无人持有的观点？先处理这些问题，再处理词句。
4. 围绕原有信息重写：具体主体和过程优先，抽象名词转换为有证据的动作。信息已够时删掉重复铺垫；信息不足时在编辑说明里标缺口，不虚构填充。
5. 保持听觉连贯：修长定语、术语首次出现、代词指向和拥挤句子；保留真实的时间、因果、并列和转折。句长随内容变化，不设置每句字数配额，不强行拆成短句清单。
6. 做语义差异核对：编辑前后是否把相关改成因果、部分改成全部、可能改成确定、某个模型改成共识、先后改成同时？数字、范围及来源是否仍在正确的主张旁？实质变化退回事实审核。
7. 独立试读：仅凭成稿能否复述过程与本集问题？检查开头的疑问有无得到回答。可读性好不等于科学正确；句式命中少也不等于内容更好。
8. 交付干净成稿。另附必要的少量修改说明与待核验项；不要把自评分、审计表或编辑过程塞进旁白。

### 应保留与应修改的边界

- 保留“可能”“约”“之一”“模型显示”承载的证据强度；删掉同一处重复堆叠的犹疑词时，留下等价限定。
- 真正澄清误解的对比、有信息的三项并列、自然四字词、被动句、必要术语都可以保留。不能为变化而把术语换成几个近义词。
- 地质过程可以用非人物主语；不要为主动语态创造一个不存在的行动者。
- 保留已核实的具体景物或过程。没有依据的气味、声音、触感、人物记忆与内心感受不能靠润色新增。
- 单个词或标点不证明文本来自 AI；模式只提示检查空泛、重复、歧义或文体冲突。

### 原创教学例（纯表达演示，非本片事实资料）

输入：“值得注意的是，甲过程不仅体现了环境变化，更开启了全新篇章。模型显示，在给定条件下，甲过程可能使乙增加。由此可见，这一变化意义非凡。”

可编辑为：“模型显示，在给定条件下，甲过程可能使乙增加。”

不能改为：“甲过程使乙增加。”后者丢掉模型归因、适用条件和不确定性。例中的甲、乙只是占位符，不构成科学主张。

## 包结构与验证建议

主 SKILL.md 保持简短；另设中文编辑案例、语义保护清单和来源取舍说明。至少用一个需要修改的片段、一个无需修改的片段、一个信息不足片段，以及一个带关键限定的科学片段测试。评审时比较同一材料有无编辑步骤的可理解程度、信息损失和误增内容；不以缩短百分比或“像人”分数决定通过。

上游文本只作研究参照；新 skill 的指令与例子原创。若未来复制或改编上游实质内容，应保留对应许可和署名，并单独确认混合来源要求。本报告只记录仓库声明，不构成许可证法律判断。
