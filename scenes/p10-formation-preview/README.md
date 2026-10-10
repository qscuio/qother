# P10太阳系形成：V2预览源码（字幕时序未核验）

本目录是完整P10段落预览的可移植源码，独立于此前六秒空间运动技术演示。1280×720、24fps；同一批870,375个材料锚点按预设轨迹收缩、变扁并向中央汇集。V2使用较低俯角和薄盘轮廓；这是分层投影艺术示意，不是引力/流体模拟或照片级效果承诺。

原执行已完成551帧预览，渲染与编码490.462秒；完整音视频解码通过。六张实际解码图已逐张检查，音频峰值0.89109、削波0、与原音轨估计相关延迟0样本。540–550帧的11个相邻零差分来自片尾约0.5秒停留，不是中途异常冻结。见recorded-original-qa.json。

本便携代码只渲染过无主持人的单帧；其decode验证器也已独立检查该原视频并复现音频数值结果，但完整551帧编码分支尚未重新端到端运行。逐字旁白、字幕切点与完整有声播放仍未核验，解码成功不等于声画内容批准。

## 旁白与时间

[P10-review.md](P10-review.md)保留原28秒暂定分镜和冻结旁白；它是历史设计记录。当前预览使用约22.456875秒的既有男声候选，音频保持原速，仅施加−1dB增益并补静音到视频末尾。总计551帧，551/24=22.958333秒，不为凑60秒拉长音频。

estimated-timings.json 和 estimated-subtitles.srt 是停顿启发式估计，非ASR或逐字强制对齐结果。估计音频切点0/3.49/9.62/17.89/22.456875秒经单调PCHIP映射到模型0/5/13/23/28秒。字幕与模型节奏仍待精校；候选音频的逐字内容尚未核验。代码没有转写上传、语音合成、网络请求或自动对外传输。

## 本地复现

使用现有Python 3.12、requirements.txt所列NumPy/SciPy/Pillow和已安装中文字体；视频需要FFmpeg/libx264/AAC及ffprobe。代码不自动安装软件或字体。

无需音频的单帧技术检查（新输出目录）：

```sh
python scenes/p10-formation-preview/render_preview.py --output outputs/p10-check --frame 288
```

制作估算时序预览须显式提供本地、已授权的mono 24kHz int16 PCM WAV：

```sh
python scenes/p10-formation-preview/render_preview.py --output outputs/p10-preview --audio inputs/authorized-narration.wav --font inputs/ChineseFont.ttf
```

此固定模板拒绝时长偏离22.456875秒超过0.01秒的输入；更换旁白须先修订并复核切点，不能仅把另一个文件塞进相同时序。默认不含主持人；可用 --host-image 指定已授权、预裁切的正方形头像，按原166px圆窗显示。没有任何角色或音频随源码打包，主持人不做口型。输出目录必须不存在，FFmpeg使用−n拒绝覆盖。

检查视频（解码与音频数值检查，不是试听/逐字识别）：

```sh
python scenes/p10-formation-preview/verify_preview.py --video outputs/p10-preview/P10-section-preview-v2.mp4 --audio inputs/authorized-narration.wav --output outputs/p10-qa --render-metrics outputs/p10-preview/render-metrics.json
```

该固定检查预期551帧/24fps/720p。相关性只检查原音频到编码音频的近零延迟，不证明旁白内容或字幕正确。完整有声播放、内容核听与句子同步须独立记录。

## 数值优化与限制

使用V2实测优化：缓存真正不变的屏幕几何，把每帧RGB/暗纹计算移出12层循环，并用四次float64 bincount累加后转换float32代替逐点float32 add.at。保留原坐标边界保护、滤波sigma、材质值和轨迹。

必须按out.dtype选择float32/float64 RGB模板，不能按层号猜测。静态LIGHT/RIDGE缓存依赖固定相机与画幅；改成动态倾角时必须重算。三点速度试验中，纯外提结果像素相同；加入bincount后仅t=12有一个蓝通道相差1/255，不声称所有时间逐字节一致。该三点试验不是完整视频速度保证。

provenance.json记录原执行代码与便携代码哈希；便携化不改state或render数值表达式，仅把主持人叠加变为可选。原渲染目录和正在运行的脚本保持不变。所有图片、音频、视频、数组与私有源包均不提交。

运行 `python test_sources.py` 可检查三个源文件指纹、输出保护、显式音频要求和估计切点标签，不会编码完整预览。
