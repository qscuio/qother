# 第一章完整预览：可复现源码

> Historical quality status: rejected-quality. The full preview remains a technical record; non-P10 visuals require rebuilding, and its “第一章” header does not match the frozen “地球往事｜序章：地球的来处” script. See [production gate](production-gate.json). Workflow changes and a separate cover candidate do not repair this video.

完整19段《地球的来处》预览，不是P10单段。冻结正文来自[e04f055版本](https://github.com/qscuio/qother/blob/e04f0556e983a75efcca7599278b04014ffe917c/docs/opening/cosmic-origin/script.md)，Git blob 13a35f2b6a484c7ff33acd815611b68454a95e6f；script/保留相同正文与段落拆分，共1434个规范化文字字符。字幕不得改写以凑时长。

原完整运行：1280×720、24fps、8584帧、357.666667秒（约5分58秒）。19段主体349.666667秒，加8秒参考片尾。原始19段旁白合计340.176秒；加入段间静音得到349.276秒，再逐段向上对齐帧边界。便携适配只做独立静帧、源码和输入保护检查，未重新渲染完整章。

## 画面与声音边界

- P01–P09：early.py原创参数化宇宙演化示意；P11–P19：late.py原创太阳系、地球和月球示意。它们是可重复的动画图解，不是精确数值模拟或照片级重建。
- P10：显式输入此前551帧720p24视频，只取画面、去掉旧音轨，均匀变速适配新的P10旁白。其烧录字幕仍是原估时，不能声称与新的词边界逐字同步。
- 默认不加载主持人。--host只影响新渲染的18段；P10输入中已烧录的角色/字幕不会被这个开关移除。若需要完全无主持人的章，须自行提供等规格无主持人P10源片。角色是静态图层，没有口型同步。
- 原运行统一使用临时合成男声zh-CN-YunyangNeural（合成时rate=-5%），不是最终获认可音色；组装时不再变速、不剪字，统一−1dB并补静音。代码不包含TTS生成、语音克隆、网络调用或服务上传。
- 原19段服务端词边界文本与冻结稿规范化匹配，不是独立ASR、逐字听辨或发音正确性证据。P10像素中的旧字幕是明确例外。音色和完整有声播放尚未验收。

## 依赖

现有Python 3.12.14、requirements.txt中实测NumPy 2.3.5/SciPy 1.17.0/Pillow 12.3.0，以及FFmpeg/ffprobe、libx264/AAC和已安装中文字体。无自动安装。原字体为Noto Sans CJK SC Regular/Bold；其他字体可能改变版式。

## 便携CLI：仅使用显式本地输入

从仓库根目录生成一个无主持人静帧（无音频、无网络）：

```sh
python scenes/full-chapter-preview/run.py frame --output outputs/chapter-frame --timeline scenes/full-chapter-preview/recorded-timeline.json --paragraph P05 --progress 0.5 --font /path/to/Chinese-Regular.ttc --bold-font /path/to/Chinese-Bold.ttc
```

frame可选P01–P09/P11–P19；P10是外部指定视频，不能误走图解模块。输出目录必须不存在。

完整章构建、组装和解码QA：

```sh
python scenes/full-chapter-preview/run.py full --output outputs/chapter-full --timeline inputs/timeline.json --audio-dir inputs/audio --boundary-dir inputs/boundaries --p10-video inputs/P10-section-preview-v2.mp4 --host inputs/authorized-host-circle.png --font /path/to/Chinese-Regular.ttc --bold-font /path/to/Chinese-Bold.ttc
```

- timeline.json结构见recorded-timeline.json：恰好19个顺序段落、相同冻结正文、WAV文件basename及实际duration。19个WAV必须为mono 24kHz int16，实际长度须与清单匹配。录音/合成音频文件不在仓库中。
- --boundary-dir可选，使用P01.edge.json…P19.edge.json。每个JSON只需boundaries列表，每项含text、offset、duration（100ns单位）。文本规范化吻合时使用服务端边界，否则记录为段内估时。原数据未作为服务请求/事件包公开；recorded/content_manifest.json保留原运行的最终cue文本与时刻。
- --host可省略；传入前自行准备已授权RGBA圆形图层，代码缩放至166px，不重新生成人物。P10烧录图层仍保留。
- --p10-video为明确输入的原551帧、720p、24fps片段；不从私人目录自动寻找。其原声音不会进入最终片。
- 便携版为保护证据采用全新输出目录，去掉原执行器仅按“MP4+JSON存在”恢复的逻辑。中断结果不自动当缓存复用；不覆盖已有目录/文件，不自动重跑长渲染。

完整编码分支尚未用便携CLI端到端重跑。旧运行成功不等于适配后的全部分支已经通过。

## 可独立运行的追加QA

```sh
python scenes/full-chapter-preview/audio_alignment_qa.py --video outputs/chapter-full/地球往事_第一章_完整预览_v1.mp4 --manifest outputs/chapter-full/content_manifest.json --timeline inputs/timeline.json --audio-dir inputs/audio --output outputs/audio-alignment-check.json
python scenes/full-chapter-preview/motion_qa.py --video outputs/chapter-full/地球往事_第一章_完整预览_v1.mp4 --manifest outputs/chapter-full/content_manifest.json --output outputs/motion-check.json
python scenes/full-chapter-preview/test_sources.py
```

QA报告输出必须是新文件。波形比较不是转写，也不会上传声音。低分辨率灰度差分仅用来发现近静止区间，不证明视觉流畅或正确。

## 已记录的原运行证据

recorded/保存经过私人路径清理的原运行记录，不能套用于任意新输入：

- 全片音视频完整解码、8584帧和19段覆盖通过；57个实际解码采样（每段3张）另供视觉检查。
- 所有19段最终AAC与各自源WAV波形相关性≥0.999804，相关峰延迟均0样本；它只支持未错拼/错位，不证明说对了字。
- 主PCM峰值约0.72797、无满幅样本；QA中的此指标不是独立AAC峰值实测。
- 主体最长逐像素完全相同连续段4帧；一秒间隔灰度比较仍有最长约5.75秒近静态区间，部分是阅读/说明停留，片尾8秒静止。不能声称每秒24张视觉独特画面。
- 未执行连续浏览器有声播放或独立逐字听辨；临时音色未获认可。技术解码与字幕文本覆盖不替代这些检查。

源文件及便携修改指纹见provenance.json，独立适配检查见validation.json。仅公开文本源码、冻结公共文稿、参数和测量记录；不公开图片、音频、视频、原始provider请求、私有角色、数组或ZIP。现有P10及六秒技术样例保持独立不变。
