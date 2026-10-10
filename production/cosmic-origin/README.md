# 《地球的来处》纸感二维制作源码

## 历史实现与当前流程

本目录保留旧纸感二维实现和当时测试记录。当前跨阶段规则见[统一制作流程](../../docs/production-workflow.md)，当前布局/声音见[制作配置](../../docs/production-style.md)。下文1280×720、左下角色、字幕底栏及临时声音描述是旧实现，不能覆盖当前1920×1080、右下角标和全幅场景要求。现有生产验证器不会自动迁移这些参数；此目录不可直接作为新规格正式生产入口，需另行授权适配与验证。

本轮仅更新方法文档，未改代码、未重跑这里的媒体测试，也没有在本目录实现 Anime.js/Three.js/Blender 适配器。已有逐镜缓存、实测 cues、音轨/字幕哈希和合成边界可供迁移，不能因保留源码就宣布新版生产可用。视频按统一流程完成同版分镜与构图内部复核后继续，不再逐项等待用户批准。下文“交用户检查后才继续”等为旧时工作安排，当前以自主复核继续为准，历史测试事实不改写。

## 历史状态记录

已完成并实际解码：1280×720、24fps、24秒无声技术预览。它不是完整视频，也不是配音试听。全片依赖实际配音和逐句对齐，当前等待外部语音服务传输授权；未虚构全片时长、音轨或生产分镜时码。

## 视觉制作

原始完整角色是唯一位图素材。它以96×144像素固定合成在1280×720画幅左下、字幕区域上方；不拆头、不贴嘴、不伪造绑定或口型。科学画面由原创程序化形状和合成图层生成，固定种子的低对比静态纸纹不产生逐帧噪点。画面使用纸底、深褐、土赭与灰绿。所有形成过程有相应示意、模型或艺术化复原标识。

扩张网格无中心爆炸；散射光路转为自由传播；气体收缩与恒星聚变；元素层次与恒星物质逸出；星系汇聚与银河循环；太阳云盘与颗粒生长；吸积和熔融分异；碰撞碎屑到月球。相邻镜头动作由旁白实际句界触发，而非固定时长网格。月岩证据仅用定性样品对照，不制造定量柱图。

旁白稿、事实边界和来源在仓库 docs/opening/cosmic-origin/。最终通用中文合成音色仍为临时音色，不代表声音选择已获验收，也不模仿任何真人。

## 私有角色素材输入

仓库不包含角色图片、用户参考照片或其他身份素材。角色由用户选择，原始来源与权利未经独立核验；仅在本次私人视频交付中使用。克隆此目录不能自行还原角色。运行者须通过 --host 显式提供其有权使用的完整原始角色 PNG。不得把该私人素材补交到公开仓库。生产分镜用可移植占位路径 user-assets/guide.png 记录输入及实际 SHA-256，不保存本机私人路径。

## 运行环境

Python 3.12；Pillow；FFmpeg 的 libx264 / AAC；系统 Noto Sans CJK 与 Noto Serif CJK。字体路径可在 render.py 常量中按环境修改。不需要新账号、API密钥、付费模型或浏览器运行时。

技术预览：

    python render.py --host LOCAL_GUIDE_PNG

完成实际配音之后，生成锁定分镜与字幕：

    python build_timeline.py --host LOCAL_GUIDE_PNG --audio-dir PATH_TO_MEASURED_CUES --script-dir PATH_TO_FROZEN_SCRIPT --audio PATH_TO_NARRATION_WAV

旧版兼容导出（保留，不用于本次正式交付）：

    python render.py --host LOCAL_GUIDE_PNG --audio PATH_TO_NARRATION_WAV --output OUTPUT_MASTER_MP4

此旧入口也核验音轨和字幕锁定信息，但没有逐镜缓存流程。本次正式交付统一使用下方 `shot_pipeline.py assemble`，避免误走全片重绘路径。

生产分镜结构检查（从仓库根目录）：

    python scripts/validate_storyboard.py production/cosmic-origin/storyboard.json --production

源码与媒体分离。不要将大体积音视频、服务凭证、私人报告或绝对用户路径提交仓库。原始向导素材的文件权利与完整性、以及源码 SHA-256 由生成的分镜锁定清单记录。

## 正式交付前仍须执行

- 所有段落与冻结稿逐字覆盖检查
- 以实际音轨/ASR句界生成最终分镜，检查时间轴覆盖、帧边界及字幕完整性
- 完整视频 ffprobe、全程解码与响度/削波检查
- 每镜首中末及转场解码帧视觉检查；最后字幕、最后画面、音尾完整
- 压缩观看版控制在原生附件容量内，并检查字幕可读性

结构验证、静帧检查与已解码短预览分别成立，均不等于完整成片已验收。

## 推荐流程：逐镜生成、检查、替换，再拼接

`shot_pipeline.py` 是逐镜制作入口。原 `render.py` 全片导出功能保留，但现在优先使用下面的可复用流程。

1. 实际配音获得授权后，先录制/取得开头若干完整段落的真实音轨和对齐文件。用 `build_timeline.py --through-paragraph N` 生成开头样片的 `storyboard-opening.json` 和 `subtitle_cues-opening.json`；输入必须逐字覆盖冻结稿前 N 段，不能用估算时码。此步骤不改冻结文字。
2. 仅导出开头镜头，逐镜检查动作和标签，再拼接成约30–45秒的带配音样片。实际时长按语句而定。交用户检查后，才继续其余镜头。
3. 其余镜头分批导出、逐镜检查。修改一个镜头的 `render` 参数或 `visual_revision` 后，按同一个镜头 ID 再次导出，产生新的缓存版本。旧缓存保留，可回退。
4. 所需片段齐备后，拼接阶段统一加入实际旁白、字幕和总进度。拼接会完整解码检查，并校验帧数、尺寸、帧率和音轨；不是把未检查的段落直接拼起来算完成。

导出一个或多个镜头（省略 `--shot-ids` 才会遍历全部镜头）：

    python shot_pipeline.py render --storyboard storyboard.json --host LOCAL_GUIDE_PNG --cache LOCAL_CACHE_DIR --shot-ids CO2-S01 CO2-S02 --report render-report.json

拼接已缓存的连续镜头，作为开头或局部检查段：

    python shot_pipeline.py assemble --storyboard storyboard.json --host LOCAL_GUIDE_PNG --cache LOCAL_CACHE_DIR --shot-ids CO2-S01 CO2-S02 --audio REAL_NARRATION_WAV --subtitles subtitle_cues.json --output opening-review.mp4

拼接全部镜头（不会自动生成缺失缓存）：

    python shot_pipeline.py assemble --storyboard storyboard.json --host LOCAL_GUIDE_PNG --cache LOCAL_CACHE_DIR --audio REAL_NARRATION_WAV --subtitles subtitle_cues.json --output full-master.mp4

若使用开头独立配音，将上面的分镜和字幕参数分别换为 `storyboard-opening.json` 与 `subtitle_cues-opening.json`，并传入对应的开头音轨。正式音轨的文件哈希必须与该分镜锁定记录一致。

### 缓存与时间规则

- 缓存是无声、无字幕、无全片进度的 FFV1 无损片段，1280×720、24fps。每镜有前后各12帧余量，主体帧数由实际分镜决定。
- 镜头内部使用局部时间。前面某镜变长时，后续镜头只要主体时长和视觉内容没变，就无需重画。
- 缓存键包含该镜参数、版本、完整角色哈希、字体哈希，以及该场景分支/共用渲染逻辑指纹。修改单场景分支不会让无关场景失效；修改共用配色、绘图函数或字体会使受影响缓存失效，这是正确行为。
- 拼接只读取已有匹配缓存。转场使用前镜后余量和当前镜首帧段；前余量保留供后续剪辑。总帧数不因转场被缩短，不挪动音轨和字幕时间。
- 替换不覆盖旧缓存。缓存按内容哈希命名，导出报告列出命中情况及版本键；用户自行管理缓存存储空间。
- 最终合成仍需顺序读取、编码所有选中帧，但不会重新计算未改镜头的场景动画。片段为无损中间文件，可能占较大空间。

### 已实施的短测试与限制

运行：

    python test_shot_pipeline.py --host LOCAL_GUIDE_PNG --output-dir LOCAL_TEST_DIR

测试只生成3个明确测试镜头、静音及可区分频率的工程测试信号，以及3.5秒和2.5秒的测试拼接。画面写有 `TEST FIXTURE · 非正式样片`，文件名也强制带 test/fixture；这些不能作为正式样片交付。

中段音轨截取还用330/660/990Hz测试信号验证实际seek；字幕用解码帧与预期字形的重合度检验源时间偏移。这些均不是语音生成。

覆盖独立镜头导出、再次缓存命中、修改一镜只重做该镜、局部时间不受前段平移影响、单场景源码依赖隔离、连续子集剪辑、帧数精确覆盖、完整解码，并拒绝缺镜、非连续选择、尺寸/帧率/帧数不符和错误的正式音轨哈希。

尚未验证：真实配音对齐、完整47镜的音画节奏、正式全片视觉验收和附件压缩版质量。测试通过不代表上述事项完成。

### 字幕与冻结稿的完整性

生成分镜时，句级和字幕级文本都必须逐字覆盖所选冻结段落（忽略标点）。字幕文件哈希及规范化文本哈希随音轨一起锁定；最终拼接与保留的旧式全片导出均核对这些哈希。负时间、NaN/无穷、空字幕、实质重叠、倒序或越过音轨的字幕会被拒绝。音轨末端仅允许50毫秒ASR舍入容差，重叠仅允许1毫秒舍入噪差。`--through-paragraph 0` 会明确失败，不会默认为整篇。

冻结稿/字幕构建器的可复现测试：

    python test_build_timeline.py --host LOCAL_GUIDE_PNG --script-dir FROZEN_SCRIPT_DIR --validator REPO_VALIDATOR_PY --report TEST_REPORT_JSON

它只在临时目录构造明确的dummy时序，分别验证整篇47镜和前两段4镜；正式模式应拒绝这些demo。测试结束删除临时静音文件与分镜，不生成正式样片。
