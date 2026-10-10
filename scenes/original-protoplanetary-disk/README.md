# H10 原创原行星盘：静态候选源码

自编程序化三维几何、体积密度、材质与灯光。形成中的恒星和不规则气尘盘属于同一世界状态；两机位用来检查遮挡和空间结构。不是流体动力学模拟，不代表实测太阳出生形态，不按物理尺度标定；没有成熟八行星或规则环隙。

## 从零重建

需要 Blender 4.3.2（实测内置 Python 3.13.5、自带 bpy/mathutils）和系统 Python 3.12。Blender 建模不需要 pip 包、外部图片、API 密钥或网络。

从仓库根目录运行：

```sh
python scenes/original-protoplanetary-disk/pipeline.py --output outputs/h10-v05
```

输出目录必须不存在或为空，避免覆盖旧结果。`--blender /path/to/blender` 可指定可执行文件。默认 CPU、8线程；`--threads 2` 可降低占用。四阶段顺序固定为 build_scene → refine_volume → refine_art → finalize_scene，先构建同版最终场景，再渲染 hero 与 side。`--build-only` 只生成模型和参数。低成本技术冒烟测试：

```sh
python scenes/original-protoplanetary-disk/pipeline.py --output outputs/h10-smoke --smoke --threads 2
```

冒烟使用320×180、8样本，不是交付质量。正常主机位1920×1080/最多512样本，独立机位1152×648/最多256样本，seed=46109，关闭去噪。历史单帧耗时分别约246秒和92秒；机器不同会变化。

最终 `.blend` 保存在主机位状态。重渲染到该构建目录（目标图片不可已存在）：

```sh
blender -b -t 8 --python scenes/original-protoplanetary-disk/render.py -- --output outputs/h10-v05 --view hero
```

`expected-settings.json` 是交付版本的参数；新构建产生 `settings.json`。`provenance.json` 记录原作者源码和可移植版本 SHA-256；移植仅分离输出目录与默认渲染调用，没有修改几何、材质、灯光、相机或核心修正。生成报告记录引擎、seed、机位、耗时与图片哈希。跨版本、CPU和操作系统不承诺逐像素相同。

## 可选中文与原主持人合成

先按上级目录安装 Node 依赖和字体。`--input` 指含 `H10-original-disk-clean.png` 的目录；`--output` 仍须新建或为空。

```sh
node scenes/original-protoplanetary-disk/compose_review.cjs --input outputs/h10-v05 --output outputs/h10-review --host /path/to/authorized-host.png
```

主持人应为已授权1920×1080透明原图层，原样叠加，不替换角色。省略 `--host` 明确产生“无主持人测试”，不能当成最终合成。公开仓库不提供或授权主持人像素。

## 实验脚本与质量范围

`experimental/benchmark_motion.py` 仅在同一静态世界测试15°相机轨道的第1/25/48帧；`measure_grain.py` 测试独立随机种子的局部噪声。不是云团演化，也不是动态质量通过。它们读取现有最终blend，将文件写入自己的 motion-benchmark 子目录，可能耗时数分钟；不要并发写同一目录。

```sh
SCENE_OUTPUT="$PWD/outputs/h10-v05" blender -b -t 8 --python-exit-code 1 --python scenes/original-protoplanetary-disk/experimental/benchmark_motion.py
SCENE_OUTPUT="$PWD/outputs/h10-v05" blender -b -t 8 --python-exit-code 1 --python scenes/original-protoplanetary-disk/experimental/measure_grain.py
```

`historical-QA.json` 是原静态候选的历史检查，不宣称本仓库任何新渲染自动通过。细粒噪声、外缘偏软和色域较窄仍为已知限制。历史静态验收不覆盖视频；后续48帧技术视频的实际结果见下方更新。连续动态播放、旁白和最终成片验收仍未通过。

定性事实背景：[NASA Solar System Facts](https://science.nasa.gov/solar-system/solar-system-facts/)。[ESO1436f](https://www.eso.org/public/images/eso1436f/)仅提供斜视盘面的外观参考，没有贴入、复制或投影到模型。无外部位图纹理依赖。

`experimental/render_camera_batch.py` 是实验性的48帧相机批处理源代码。公开移植版为防止混入旧样本，要求新建 camera-motion-48/frames，禁用未验证的基准帧复用，实际重渲染全部48帧；可能耗时约一小时。发布时仅语法检查，未运行公开版完整批处理，不能称为动画通过。执行方法与上面相同，只替换脚本名。

噪声统计和编码工具也保留在 experimental：

```sh
python scenes/original-protoplanetary-disk/experimental/analyze_grain.py --output outputs/h10-v05
python scenes/original-protoplanetary-disk/experimental/encode_camera_test.py --output outputs/h10-v05
```

噪声工具的可选依赖见 experimental/requirements.txt（实测 NumPy 2.3.5、Pillow 12.3.0）；统计是PNG显示亮度差分，不是线性辐亮度误差。编码另需 FFmpeg/ffprobe 与 libx264；拒绝覆盖现有视频，检查48帧、1280×720、24fps、2秒。像素格式与帧数不证明源图确为3D，也不证明视觉播放通过；源头与播放仍需独立验证。公开编码工具仅语法检查，尚未执行完整48帧编码。


## 2026-10-10 实测更新

[48帧技术视频结果](experimental/RESULTS.md)及[机器可读结果](experimental/results.json)：原执行已渲染并编码48帧、1280×720、24fps、2秒，无声、无插帧、无去噪。全片解码及相邻帧粗异常扫描完成；浏览器连续播放受环境限制，未取得掉帧或呈现帧遥测。不是最终画质验收。公开版新目录/不覆盖防护保持不变；该历史执行不冒充公开版完整重跑。

```sh
python scenes/original-protoplanetary-disk/experimental/scan_motion_frames.py --movie outputs/h10-v05/camera-motion-48/H10-actual-3D-camera-test-2s.mp4 --output outputs/h10-motion-qa
node scenes/original-protoplanetary-disk/experimental/qa_browser_playback.cjs --movie outputs/h10-v05/camera-motion-48/H10-actual-3D-camera-test-2s.mp4 --output outputs/h10-playback-qa --chromium /path/to/chromium
```

[三组性能试验](performance-pilot/README.md)另列代码、历史计时与像素指标；保持原画质默认值，不自动采用更快配置。
