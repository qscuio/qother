# 已使用的官方参考排版源码

与原创H10场景独立；这两条管线只裁切/排版官方参考，不生成银河或星云模型。保留原署名、来源身份、科学边界与太阳原生定位圈。外部源文件未随代码发布，来源与许可见 `external-assets.json`；音轨完全不使用。历史失败的自建云团与伪银河渲染器未作为当前有效代码发布。

需要上级目录的 Node 包与 Noto Sans CJK SC。输出目录必须不存在或为空；省略 `--host` 时图中明确标注无主持人测试。可加 `--host /path/to/authorized-host.png` 原样叠加已有1920×1080透明主持人。

## ESA/Gaia

准备原1920×1080动画89秒与104秒的未修改PNG帧，命名 `source-089.png`、`source-104.png`。可从清单中的官方视频提取，保留源分辨率、原字幕、ESA角标及104秒太阳圈；不得用768×432预览放大冒充高清。示例（ffmpeg可用时）：

```sh
ffmpeg -ss 89 -i official-gaia.mp4 -frames:v 1 inputs/gaia/source-089.png
ffmpeg -ss 104 -i official-gaia.mp4 -frames:v 1 inputs/gaia/source-104.png
node scenes/reference-layouts/compose_gaia.cjs --input inputs/gaia --output outputs/gaia-reference
```

同时输出独立层SVG及PNG。SVG在运行时嵌入调用者的源图/可选主持人，因此运行产物不能盲目公开。底图为Gaia数据支持的艺术复原，不是银河外部实拍。今日太阳定位不能接成46亿年前同一坐标的连续推镜。

## ESO

准备官方 Publication JPEG 版本（并非网站的最大原图）：[eso1303a.jpg](https://cdn.eso.org/images/publicationjpg/eso1303a.jpg)（4000×3900）、[eso1436f.jpg](https://cdn.eso.org/images/publicationjpg/eso1436f.jpg)（4000×2667）。源码复现原裁切：全宽4000、裁高2250，分别从y=995和139开始，再缩至1920×1080。源图尺寸改变会改变裁切结果。

```sh
node scenes/reference-layouts/compose_eso.cjs --input inputs/eso --output outputs/eso-reference
```

Lupus 3只作同类气尘云外观参考，不能标成太阳出生云；ESO盘图含已有行星/环隙，不能直接充当刚形成太阳系的原创模型。两张不同来源图片不构成同一对象演化证据。

发布任何适配媒体前仍须核对来源许可、署名、改编条件和主持人权利。代码的公开性不自动授权资产分发。
