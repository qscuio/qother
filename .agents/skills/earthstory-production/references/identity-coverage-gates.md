# 身份、覆盖与逐段质量台账

本文件由 production、visual-design、cinematography 共同使用。入口为仓库根目录的 `scripts/validate_production_gate.py`，只用 Python 标准库。先执行 `python -m unittest discover -s scripts -p 'test_production_gate.py'`。

## 执行顺序

1. 从本次对应的冻结剧本提取唯一 H1、原始字节 SHA-256 和完整有序段落 ID。封面与视频标题卡/品牌行使用相同标题，不另起章节名。段落 JSON 的正文必须按顺序与 Markdown 正文相同。当前序章是《地球往事｜序章：地球的来处》，P01–P19；这是当前输入事实，不是通用工具硬编码。
2. 内部审查者逐段拆解有意义的主张，把全部正文连续分配给主张，再把主张连接到实际旁白 cue、镜头与视觉解释。概念、因果机制、尺度和不确定性都须按剧本表达。不能用一个“已覆盖”的段落标签替代语义审查。一个镜头可服务多条主张，一条主张也可跨镜，不规定固定镜数或全局配色。
3. 审查实际版本的关键帧、运动与相邻段落连续性，比较本任务质量对照。当前项目的 P10 是质量参考，而非全片都必须使用它的粒子或盘状材质。完成本段内容/视觉/连续性内部复核后再进入完整组装。不要重新添加逐项用户批准关卡。
4. 验收最终输出还须技术、真实播放和声音内容复核。技术解码通过不能替代观看、听审与语义判断。若授权制作未完成预览，保留门禁失败及缺口，明确交付为预览，不伪造通过。

## 输入快照与失效

运行前列出本次所有实际输入。私有输入清单仅留本地，不提交路径、音频、主持人素材或凭据。JSON 清单的键必须恰好是 `script, paragraphs, audio, assets, timeline, storyboard, render_code`，每组是非空的 `[{"id":"稳定逻辑ID","path":"相对于清单的实际文件路径"}]`。script 与 paragraphs 各一个文件；其他组列全所有依赖，包括旁白及 cue、引用视频/主持人/字体/纹理、剪辑/字幕时间表、分镜文件及全部渲染/组装源代码。无外部素材时提供实际“无素材”配置文件，不使用虚构散列。

执行：

```
python scripts/validate_production_gate.py snapshot --manifest local-inputs.json --output fresh-inputs.json
python scripts/validate_production_gate.py check --ledger production-gate.json --script docs/opening/cosmic-origin/script.md --paragraphs scenes/full-chapter-preview/script/paragraphs.json --manifest local-inputs.json --evidence-manifest local-evidence.json --gate assembly
```

`assembly/final` 每次必须传 `--manifest`，直接重读所有实际依赖文件；不能用旧 `--inputs` JSON 放行。`--inputs` 仅可用于 structural 历史检查。`--evidence-manifest` 是本地证据 ID 到实际文件路径的 JSON 映射，每次重读并核对台账中所有证据散列；路径相对该清单。`final` 还必须传 `--output-artifact` 指向实际成片，台账 `final_artifact_evidence` 指定它的证据 ID，technical/playback/audio_content 三项记录都必须引用该 ID。成片字节不同即失败。

快照逐文件 SHA-256 后按逻辑 ID 排序；输出文件拒绝覆盖。每次输入变更重新生成快照并复核，不能将旧快照冒充当前输入。台账的 input_digest、每条通过审查和每份证据都绑定七组散列的总摘要。正文、旁白、素材、时间表、分镜或源代码改变都会使旧审查失效。输入是否列全仍需实际审查，不能由工具穷尽证明。生成目标与实际输出的身份也必须由证据核验，禁止拿别的成片审查记录套用。

## 台账字段

- `schema_version: 1`；`status` 为 candidate/reviewed/rejected-quality/superseded。
- `identity`: title、script_sha256；`input_digest`: 当前快照摘要。
- `labels.cover` 和 `labels.video_header`: title 与 review。
- `narration_cues`: cue ID -> paragraph_id、source_text，另记实际时间与计时来源。文本匹配不证明声音说了这些字。
- `shots`: shot ID -> paragraph_ids、version、content/visual/continuity 三项 review。
- `paragraphs`: 完整有序 id、narration_cue_ids、claims。claim 含唯一 id、连续 source_text、concepts、visual_explanation、narration_cue_ids、shot_ids、semantic_review。每段主张文本和 cue 文本各自必须完整拼回冻结正文。引用必须存在并归属该段。
- `quality`: benchmark_ref、benchmark_comparison、input_completeness、technical、playback、audio_content。
- `evidence`: 证据 ID -> artifact_ref、artifact_sha256、scope、input_digest。使用稳定公开相对引用或私有逻辑 ID，不暴露下载链接。实际审查者须打开对应散列的产物，注明看过哪些帧/区间及局限；散列字段不是机器看过图像的证明。
- 每项 review 必须显式 status=pass/fail/not-run/blocked。pass 还需 reviewer_kind=human/agent、reviewer、scope、非空 evidence ID 列表及 input_digest。记录真实执行审查的角色，禁止自动填充“pass”。

`structural` 仅检查身份/映射/散列/字段；允许尚未审查状态。`assembly` 额外要求封面/标题、全部主张和镜头内容/视觉/连续性、质量对照、输入完整性记录通过；`final` 再要求技术、实际播放和声音内容审查记录通过。缺失、未知、not-run、blocked、fail 都不能替代通过。被否决/已替代版本不能作为 assembly/final 通过版本。

输出 `mechanical_consistency: pass` 只证明结构与所填审查记录自洽。工具明确输出 `semantic_or_visual_truth_verified_by_script: false`，不会读图、听声音、证明科学正确或鉴别虚假自我签署。生产负责人还必须读取对应实际审查证据后决定继续。

## 真实历史回归

`scenes/full-chapter-preview/production-gate.json` 保留旧完整预览的质量否决与错误标题，应失败。其 `recorded-gate-inputs.json` 只指纹化公开历史记录，不能用于新渲染，input_completeness 明确 not-run。旧技术 QA 不修改。修正台账标题也仍会因语义、视觉、连续性等缺口失败；填写元数据不修复成片。新版本须新输入快照与真实复核，历史 sidecar 保留。
