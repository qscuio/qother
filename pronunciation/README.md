# 技术旁白统一发音词典

`technical-zh-CN.v1.json` 是脚本文案和配音准备共同使用的当前词条源。版本 1.1.0 覆盖 MAC、VLAN、In-LIF、Out-LIF、LIF、RIF、Ethernet。标准书面拼写用于脚本、画面、字幕；发音替代只写入单独的 `spoken_text`。

文件名的 `v1` 表示兼容的词典主版本，具体发布版本由 JSON 的 `version` 标识。1.1.0 只新增 Ethernet，原六个词条保持不变；旧版 1.0.0 的原始字节保存在 `technical-zh-CN.v1.0.0.json`，可通过 `--lexicon pronunciation/technical-zh-CN.v1.0.0.json` 或 `load_lexicon(path)` 显式使用。固定版本的制作应保存选用的词典及其摘要，不自动替换已冻结的项目副本。

## 读法与试听状态

| 画面/字幕 | 目标口头读法 | Qwen TTS 候选输入 | 实际试听 |
| --- | --- | --- | --- |
| MAC | 麦克 | 麦克 | pending |
| VLAN | V-lan，不逐个字母念 | V lan | pending |
| In-LIF | in leaf | in leaf | pending |
| Out-LIF | out leaf | out leaf | pending |
| LIF | leaf | leaf | pending |
| RIF | riff | riff | pending |
| Ethernet | E zer net | E zer net | pending |

目标读法不等于已经验证的引擎输入。这些输入是待试候选，并不保证模型一定按目标发音。此前声音本身被接受，也不能代替各词的实际试听。可先在被授权的短句里比较，再按具体模型、声音、语言和配置记录实际检查结果。制作授权与发音验证是两回事：用户可以授权带有已披露待验证项的制作，但不能因此将待试听状态改成通过，也不需要凭空增加一次用户确认。此提交不生成音频，也不授权任何新配音、声音克隆或视频制作。

Ethernet 的 `E zer net` 是口头读法提示与引擎候选输入，不是音标，也不表示任何音素已经听音核验。自动转录或文本测试不能代替实际试听；公开词条保持 `pending`。`E zer net` 只进入配音稿，正文、画面与字幕仍写 Ethernet。

PP、TM、IP、DNX 等未列出的缩写保持原样，不推导成按单词读。`leaf`、`riff` 是读法提示，不作为正文拼写或匹配别名。只有明确列出的大小写匹配；In-LIF / Out-LIF 的 U+2010、U+2011 排版连字符是显式别名，不包含任意大小写、空格或其他破折号变体。

## 使用

在仓库根目录运行，输出选择公共仓库之外的新私有目录：

```bash
python scripts/apply_pronunciation.py \
  --text "$CANONICAL_NARRATION" \
  --out "$NEW_PRIVATE_TEXT_DIR" --allow-pending
```

输出 `display.txt`（原始 UTF-8 字节不变）、`spoken.txt` 和 `pronunciation-report.json`。报告保留原文字符偏移、匹配词、候选读法、版本、词典摘要和待试听词条。`--allow-pending` 允许准备明确标记为待验证的文本，不会把状态改成通过，也不会生成音频。是否使用这份待验证文本继续制作，由实际用户授权和任务要求决定；此开关本身不授予制作权限。

默认遇到尚未针对当前配置验收的替代时失败，不创建输出目录。没有匹配项时 `no_pending_replacements` 也不代表整篇旁白已经试听。

Python API（将仓库 `scripts` 加入导入路径）：

```python
from apply_pronunciation import load_lexicon, prepare_spoken_text
result = prepare_spoken_text(canonical_text, load_lexicon(), allow_pending=True)
clause = {"text": result["display_text"], "spoken_text": result["spoken_text"]}
```

用于任意安装位置时，传明确的词典路径给 `load_lexicon(path)` 或 `--lexicon path`。脚本默认只查找自身所在仓库的规范路径，不下载词典、不读取凭据、不静默回退。

## 集成约定

- 两套视频技能使用同一根目录词典和辅助脚本，不维护各自的替代表。
- 流程图的 `narration` 和 `clauses[].text` 仍是原文；只把结果 `spoken_text` 用于该条配音。不能用修改过的发音文本生成字幕。
- 白板旁白保留规范稿，另存发音稿；字幕与标签引用规范稿。现有 Qwen 适配器 `--text` 指向生成的 `spoken.txt`，需要配音授权后才运行实际合成。
- 保留实际发音稿与词典版本的绑定。改词典、发音稿或音轨后重新测量时序；不能沿用旧音轨时码。
- 此辅助脚本只处理旁白散文，不是源代码解析器。按最长词优先单次替代，避免先改 LIF 破坏 In-LIF；不递归替代生成结果。保护 MACsec、带数字/下划线的标识符、点号成员、命名空间、函数调用、Markdown 代码、URL 和显式文件路径。代码要转述时，另写规范旁白，不能对源码运行全文替换。
- 只匹配列出的大小写；`Ethernet` 可与中文相邻，`ethernet`、`ETHERNET`、`Ethernet0`、`FastEthernet`、`Ethernet_MAC` 保持原样。当前七个词条的发音稿再次处理时文本不变，但第二次报告不能替代首次报告：没有新替代不等于发音验收通过。每次制作都应从规范稿生成并保留首次报告。

## 验收与更新

公共词典仅保存通用词汇与候选。实际声音/模型配置标识、试听证据、用户录音、参考转录、声纹、个人路径及其摘要均留在私有项目资料，不提交公共 Git。生成的报告可能包含完整旁白和私有配置，也不能自动发布。

若私有项目副本已实际试听某词，可将该词 `tts.audition` 记为 `{"status":"accepted","profile":"<exact private configuration identity>","evidence":"<private review reference>","input":"<exact tested TTS input>","engine":"<exact tested engine>"}`，运行时传相同 `--profile`。配置、引擎或输入与试听快照不匹配时仍视为待试听。不能为了绕过检查填入虚假验收，不能把一个声音的验收扩展到其他声音；公共候选不因此自动全局通过。

新增词条必须写清 `display`、显式 `aliases`、`oral_reading`、引擎 `tts.input` 与试听状态，并增加正反例。改变匹配/发音行为更新 `version`；不兼容结构更新 `schema_version` 和文件主版本。此版本的状态是数据记录与准备关卡，不是自动听音验证。

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s scripts -p 'test_pronunciation.py'
```
