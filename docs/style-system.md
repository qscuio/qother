# 地球往事系列：风格、技能与制作边界

## 当前选择
纸感、土色系二维历史场景是历史试制方向，不再作为宇宙开头默认。当前宇宙开头的暗色科学图解与浅色图谱方向仍在比较，两者尚未选定或批准；系列没有最终统一风格。画面讲述事件，蓝西装玩具向导按[当前制作配置](production-style.md)作右下完整角标；16:9。已有构图试验仅验证画面布局，不等于整套风格、人物动画、渲染引擎或整集成片已通过。扁平矢量、微缩三维与等距信息图是候选方案，未经用户选择与制作验证。当前采用现成男性标准普通话，具体音色质量仍待实际验收；本次不启用声音克隆，若另行授权再评估。

机器可读入口：[style-manifest.json](style-manifest.json)。每种风格有一个真正的仓库级 `.agents/skills/<style>/SKILL.md` 和一个 [独立角色说明](agents/earthstory-paper-2d.md)。角色说明供运行环境按需调用，不是 agent 自动部署或持续运行声明；技能文档本身不会安装渲染器、创造绑定或生成配音。

## 共用制作流程

统一使用[制作流程与关卡](production-workflow.md)，由[earthstory-production](../.agents/skills/earthstory-production/SKILL.md)编排已有写作、视觉、摄影、人物素材和风格技能。那里集中维护输入输出、早期声音规划、实测时序、同版分镜/构图内部复核、逐镜缓存与声画 QA；本页只管理风格和角色边界，不另维护一套生产顺序。

## 新增一种风格
复制 [风格模板](style-skill-template.md) 的正文结构，创建独立 `.agents/skills/<new-style>/SKILL.md` 与 `docs/agents/<new-style>.md`；不要把候选项自动变成默认项。在 manifest 标注 proposed-unvalidated，写清自己的色板、材质、形状、人物身体、场景、灯光、摄影、缓动、缺陷禁区和验收点。运行 Codex skill-creator 随附 quick_validate.py，并通过本仓库分镜验证器。最后用一个真实短镜头验证，保留结果。最终风格选择由用户决定。

## 工具评估与依据

详细依据与选型比较见 [工具研究](animation_skills_research.md)。生产运行应锁定引擎、插件和资产版本；例如 HyperFrames 上游技能可能默认自动升级，应以本项目显式批准的版本锁定为准，避免重渲染发生不可追溯变化。
本包没有执行这些引擎，也不把它们列为已安装依赖。以下是供选型的公开来源；实际采用前核对最新许可、运行条件和工具输出。
- [Remotion 官方 AI skills](https://www.remotion.dev/docs/ai/skills)：配套制作规则；不能把引擎简单称为 OSI 开源，也不提供本项目角色绑定。
- [HyperFrames](https://github.com/heygen-com/hyperframes)：HTML/场景合成候选；支持动画合成不等于已有合格历史角色动作。
- [Papermotion](https://github.com/francozanardi/papermotion)：实验性纸片二维运动参考。其顺序状态推进与任意帧寻址渲染不应直接混用；如采用需做独立兼容性试验，必要时先预渲染视频素材。

项目特定约束只适用于本系列，不应写入所有项目的全局规则。

## 借鉴方法的边界

[Lemo-Opuscar 取舍记录](lemo-opuscar-adaptation.md)补充制作规划、声音表、确定性与数据编码；只引入文档和候选风格规则，不自动安装工具或扩张授权。旧试制规范若与当前主持人/旁白配置冲突，以 production-style.md 当前配置为准；历史分镜保持原样，不冒称已同步。

## 候选视觉语法扩展（待审阅）
[风格吸收范围](lemo-opuscar-style-selection.md)说明43项的取舍；本轮只新增科学结构图与博物志铜版图谱两个独立skill/角色，强化已有四项，均不变更默认。结构图只用于局部解释，不替代真实三维宇宙场景；具体风格必须遵循各自语法，不能把所有参考元素同时混在一帧。

## 人物动作素材（跨风格）

[earthstory-character-assets](../.agents/skills/earthstory-character-assets/SKILL.md)管理固定身份参考、逐动作候选、统一画布/alpha、有记录的挑帧、具体状态版本复核和独立PNG交付；它不属于 styles，不新增 style_id，也不替代风格或真实三维场景。完整方法与排除项见[sprite-gen 取舍记录](sprite-gen-adaptation.md)。人物流程部分只吸收文档；另按授权修正布局校验及测试，未安装上游工具或生成生产素材。

## Skill 与执行角色如何分工

画风是可复用的 skill/参考规范；一次任务由视觉设计、分镜/摄影、制作和检查等职责按需要协作。同一个执行者可以加载本镜所需的 skill，没有必要为每个上游编号建立常驻 agent。这里的 docs/agents 是角色说明，不证明已经部署对应进程。

只有视觉材料、空间表达及验收边界确实独立，才新增 style skill；只是纸纹、线条或版式细化就补现有参考。一次镜头选择一套主语法，跨风格切换必须有明确叙事理由与审阅。两份手绘库此次只增强已有规范，未新增 style_id 或部署框架，见[手绘适配记录](hand-drawn-adaptation.md)。
