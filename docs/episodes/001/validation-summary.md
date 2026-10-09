# 第001集交付验证摘要

2026-10-09 · v2.1。仅验证文字稿、来源与分镜规划；没有媒体制作。

## 已执行

- 旁白1409个汉字，七个阅读章节；24个历史镜号按新版故事顺序连续覆盖0—420秒。变长预算并非实测时长。
- 三份JSON的镜号、顺序、起止时间、旁白、来源ID逐项严格等于共同骨架；三份Markdown逐镜旁白相同。主稿每段旁白与骨架逐字一致。
- 三份JSON来源ID、URL、支持范围与sources.json一致；kind=factual、原分类保存在source_type。
- 现有分镜验证器通过三套demo规划：纸感二维24镜/8项资产需求、扁平矢量24镜/6项、微缩三维24镜/11项。均9个来源，420秒。
- 每套生产模式均被正确拒绝；内存中仅将mode改为production仍被零资产哈希拒绝。没有虚构生产文件或真实哈希。
- 原验证器回归：有效样例及16个拒绝样例通过。
- 新增test_episode_001_sync.py通过；检查旁白、来源、时间、生产阻断及全仓库166个Markdown相对链接。
- 三个新写作技能的官方quick_validate检查均通过；对应功能用例由独立文本评审执行，结果及限制见[研究索引](../../writing/research-index.md)。
- 逐项事实与改稿复核见[事实核查](fact-check.md)；模拟初读问题和处理见[编辑记录](editorial-review.md)。文学判断不由结构校验器决定。

## 复现

在仓库根目录执行：

```sh
python scripts/test_storyboard_validator.py
python scripts/test_episode_001_sync.py
python scripts/validate_storyboard.py docs/episodes/001/storyboard-paper-2d.json
python scripts/validate_storyboard.py docs/episodes/001/storyboard-flat-vector.json
python scripts/validate_storyboard.py docs/episodes/001/storyboard-miniature-3d.json
```

后三条加 --production 应失败。这是如实标明规划状态的保护，不能通过改状态、编造哈希绕过。

## 尚未验证

- 真人试读、录音语速、停顿和正式片长。420秒预算须在配音后重定。
- 生成图、模型、运动样片、灯光、实际字幕可读性、口型、角色绑定、音效与完整视频。
- 实际资产文件、真实哈希、授权、完整原角色图片及像素验收。完整向导、高度约20%和字幕避让目前仍是制作要求。
- Markdown只作文本与链接检查，未做浏览器渲染预览。
- 模拟初读不是真实观众测试；最终风格与审美仍待用户评阅。


## 第一节局部精修复验 · 2026-10-09

仅第一节及对应S01、S02、S05、S06更新。第2—7节正文按修改前后字节比较一致；其余20镜数据不变。三套JSON、Markdown与共同骨架逐字同步，时间和来源ID保留。再次执行上述同步检查、验证器回归及三套demo／production测试；production仍被规划状态拒绝。未重新验证媒体或真实口读时长。
