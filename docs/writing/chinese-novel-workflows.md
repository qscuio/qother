# Chinese novel workflow inspection

Checked 2026-10-09. Read-only web inspection of actual skill/runtime files; no installation, execution, or public writes. These are real repositories with inspectable instructions, not evidence that their prose is excellent. Branch links are mutable. GitHub snapshots can lag; exact latest commit timestamps were not reliably exposed, and I did not test any pipeline.

## 1. Tomsawyerhu/Chinese-WebNovel-Skill — strongest editorial diagnosis

Repository: https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill
Actual entry: https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill/blob/v2/SKILL.md
Actual voice procedure: https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill/blob/v2/references/modules/anti_ai_voice/runtime.md

The 349-line entry routes work into planning, scene execution, and final review. Its repair priority is causal logic/character continuity, then transitions/dialogue/endings, then voice. Chapters require an objective, resistance, changed situation, and reason to continue; scene review checks temporal, physical, information, emotional, relational, and ending continuity. The specialized voice procedure diagnoses abstract verdicts, interchangeable voices, atmospheric clichés, and monotonous rhythm before proposing local replacements. It explicitly rejects equating natural prose with deliberate roughness.

Best borrowing: locate the actual narrative failure before polishing words. For documentary prose, use verifiable physical processes and evidence in place of invented actions or dialogue. No blanket ban on explanation: scientific explanation is often essential.

Status: public v2 tree, 24 commits shown by indexed repository snapshot; latest displayed update August 28, 2026. No license shown in inspected root and no license text located. Treat permission to copy implementation/text as unverified; borrow general methods in original wording rather than vendoring.

## 2. xiaofeng-928/chinese-longnovel-skill — strongest canon discipline

Repository: https://github.com/xiaofeng-928/chinese-longnovel-skill
Actual entry: https://github.com/xiaofeng-928/chinese-longnovel-skill/blob/master/SKILL.md
Actual context protocol: https://raw.githubusercontent.com/xiaofeng-928/chinese-longnovel-skill/master/references/%E9%95%BF%E7%AF%87%E4%B8%8A%E4%B8%8B%E6%96%87%E4%B8%8E%E4%B8%80%E8%87%B4%E6%80%A7.md
License: https://github.com/xiaofeng-928/chinese-longnovel-skill/blob/master/LICENSE

The entry separates planning, drafting, naturalization, formal review, and export. Drafting does not silently trigger naturalization. Formal review is bound to a manuscript hash; editing invalidates that review. The context protocol distinguishes approved history from future plans, reads recent actual prose plus layered summaries, and prevents uncommitted alternatives entering the canon. Stable facts receive source anchors; semantic equivalence still requires human/model judgment rather than pretending a hash checks meaning. It explicitly says style cannot change events or numbers.

Best borrowing: separate factual canon, structural plan, working draft, and accepted revision. Re-check changed dates, quantities, uncertainty, and causal claims after every literary edit. Do not import its elaborate transaction system unless project scale justifies it.

Status: v2.2.0 stated on repository page; 63 commits shown; tests/evals directories visible but unrun. MIT label verified on GitHub; third-party notices exist and would need reading before copying components.

## 3. XINGANLIU/web-novel-writing-skill — clearest hierarchical workflow

Repository: https://github.com/XINGANLIU/web-novel-writing-skill
Actual entry: https://github.com/XINGANLIU/web-novel-writing-skill/blob/main/skills/SKILL.md
Actual Codex adapter: https://github.com/XINGANLIU/web-novel-writing-skill/blob/main/AGENTS.md
License: https://github.com/XINGANLIU/web-novel-writing-skill/blob/main/LICENSE

Its actual 279-line skill moves from premise/world/characters to master outline, volume outline, chapter beat sheet, prose, review, state update, and revision. Each chapter blueprint identifies needed context and planned information delivery. Revision defaults to the affected passages; multiple severe faults justify rewriting the chapter. Review precedes state updates, so later chapters use the accepted outcome. Seven expert labels organize responsibilities, but role switching itself is not proof of independent review.

Best borrowing: a chapter has a job within a larger arc and a scene-level plan, not a list of facts to expand. For an Earth-history documentary, replace character cards with entities/processes, chronology, evidence, uncertainty, and the reader's current knowledge.

Status: public main tree, 3 commits shown, MIT label verified. Small visible history; no output-quality benchmark verified. Avoid importing the universal 3:1 pacing formula or treating banned terms as an authenticity detector.

## 4. zhougz520/novel-architect — strongest production gate separation

Repository: https://github.com/zhougz520/novel-architect
Actual entry: https://github.com/zhougz520/novel-architect/blob/master/skill/novel-architect/SKILL.md
License: https://github.com/zhougz520/novel-architect/blob/master/LICENSE

The 408-line skill separates deterministic state/index/hash checks from model literary judgment. Its production loop prepares context, compares beat alternatives, drafts, reviews, repairs, and commits. A source directory holds canonical world/character rules; rolling volume plans avoid fixing every distant chapter too early. Failed gates produce a repair task rather than a false completion. The framework is explicitly commercial serial fiction, with retention, visible payoff, and market position embedded in its decisions.

Best borrowing: prepare a self-contained chapter brief, compare two legitimate narrative organizations, and make reviewers identify concrete repair targets. Do not optimize a factual documentary for enemies losing, escalating personal gains, or mandatory cliffhangers.

Status: v3.0.0 stated; 82 commits shown; Apache-2.0 label verified. Tests directory visible, not run. README claims a completed 140-chapter production case; this is a maintainer claim, not independently assessed prose quality or commercial success.

## 5. PenglongHuang/chinese-novelist-skill — useful prose-context calibration

Repository: https://github.com/PenglongHuang/chinese-novelist-skill
Actual entry: https://github.com/PenglongHuang/chinese-novelist-skill/blob/master/SKILL.md
Actual chapter procedure: https://github.com/PenglongHuang/chinese-novelist-skill/blob/master/references/flows/phase3-writing.md
License inspected: https://github.com/PenglongHuang/chinese-novelist-skill/blob/master/LICENSE

The chapter procedure reads the outline, relevant character information, prior chapter ending, and a prose style benchmark. Crucially, prose rather than a table or summary should be the final material seen before drafting. It calibrates later chapters against good passages from the first accepted chapter. It also tracks what terminology the reader already knows. Its rigid quotas include dialogue percentage, conflict intervals, surprise, and length, which are commercially oriented rather than universal craft principles.

Best borrowing: preserve tonal continuity through an accepted, original sample and maintain a reader-knowledge ledger. Reject mandatory dialogue, surprise, padding to length, and independent parallel drafting where cross-chapter causality is unresolved.

Status: MIT text verified, copyright 2026; repository shows v2.0 announcement and 38 commits. Inspected instructions only; no claim that automated word counts verify quality. Another researcher covers this repository in more detail.

## Synthesis for our factual Earth-history documentary

This recommendation is my adaptation, not any repository's claim:

1. Establish the evidence contract first: sourced chronology, quantities, physical mechanisms, uncertainty, and forbidden inventions. A scene cannot invent an observer, sensation, quotation, or unrecorded event merely to become vivid.
2. Build narrative hierarchy: overall explanatory question → chapter's causal change → a few process/evidence scenes → paragraphs. Each level should do different work.
3. Give each scene an entry state, evidenced pressure or mechanism, observable change, consequence, and remaining question. This translates story movement without anthropomorphizing nature or inventing conflict.
4. Track reader knowledge separately from scientific truth. Introduce a term with a concrete referent; advance understanding instead of repeating definitions or revealing later explanations too soon.
5. Assemble the factual brief first, then reread the previous accepted ending and a short original tonal sample immediately before drafting. Keep research notes out of the final voice.
6. Review in order: factual fidelity → causal/temporal continuity → chapter/scene purpose → Chinese sentence movement and image precision → read-aloud cadence. A lexical edit cannot repair missing causality.
7. Judge images by explanatory value and evidence, not ornament count. Let rhythm follow changes in scale, speed, pressure, and consequence. Long and short sentences need reasons, not a forced alternation formula.
8. Keep both a fact reviewer and a prose editor. Reconcile their findings explicitly; never let a beautiful rewrite silently change certainty, duration, quantity, or causal direction.

## What to reject across these projects

- Commercial retention mechanics are a genre contract, not a universal model of beautiful writing. Mandatory hooks can become repetitive withheld information; fixed excitement quotas can destroy proportion and quiet accumulation.
- Word bans can flag repetition but cannot establish whether prose is natural or well written. Ordinary Chinese words such as 竟然 or 不禁 are not intrinsically wrong; an awkward causal structure remains awkward after synonyms.
- More roles, files, or agents do not establish better prose. Require visible before/after passages and a faithful, readable result.
- “Show, don't tell” is selective. Documentary narration must sometimes explain an unseen mechanism or summarize millions of years. The real question is what the reader needs to perceive now and what the evidence permits.
- Never transfer invented fictional canon into a historical truth claim. In fiction, canon means the project's accepted story. In documentary, even an accepted draft remains subordinate to external evidence.
