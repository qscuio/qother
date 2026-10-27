# 借鉴来源与独立实现边界

此技能为独立的小说/剧本写作指引，不是上游软件的移植，也不需要运行它。

研究参考：EthanYoQ/AI-Novel-Writer（Pagekin），固定版本 `62880d629af7bbfaf968c0cda5ae76816e917915`，上游标示 GPL-3.0。

- [chapter-goal-review.ts](https://github.com/EthanYoQ/AI-Novel-Writer/blob/62880d629af7bbfaf968c0cda5ae76816e917915/src/shared/chapter-goal-review.ts)：目标与文本证据应分别核查。
- [character-roster.ts](https://github.com/EthanYoQ/AI-Novel-Writer/blob/62880d629af7bbfaf968c0cda5ae76816e917915/src/shared/character-roster.ts)：人物身份、别名及范围要明确。
- [blueprint-semantic-contract.ts](https://github.com/EthanYoQ/AI-Novel-Writer/blob/62880d629af7bbfaf968c0cda5ae76816e917915/src/shared/blueprint-semantic-contract.ts)：计划与实际内容需要语义层面的对照。
- [review-cycle.ts](https://github.com/EthanYoQ/AI-Novel-Writer/blob/62880d629af7bbfaf968c0cda5ae76816e917915/src/shared/review-cycle.ts)：区分检查、修订和复核，避免空转。
- [ADR 0017](https://github.com/EthanYoQ/AI-Novel-Writer/blob/62880d629af7bbfaf968c0cda5ae76816e917915/docs/adr/0017-source-bound-character-state-and-continuity.md)：人物状态及连续性结论绑定具体来源。
- [builtin-prompt-templates.ts](https://github.com/EthanYoQ/AI-Novel-Writer/blob/62880d629af7bbfaf968c0cda5ae76816e917915/src/services/builtin-prompt-templates.ts)：研究写作任务之间的职责划分，不复用提示词正文。

本技能用独立措辞把上述思想转化为轻量的人工文件工作流，并补充独立的小说语言、戏剧动作和剧本交付路线。没有复制上游代码或提示词，不声称具有其程序化检测、数据库、模型后端或自动代理能力。未来若引入上游代码或实际文本，须另行核对许可证和使用范围；本文件不是许可豁免。
