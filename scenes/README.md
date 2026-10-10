# 可复现的场景与合成源码

这次提交实际运行代码，不含图像、音频、主持人素材、私人源包或大型 `.blend`。运行产物放在新目录，勿提交含私有素材的合成图或 SVG。

- [原创原行星盘](original-protoplanetary-disk/README.md)：完整四阶段 Blender 建模链、双机位渲染、参数、源文件指纹、静态 QA 和实验性运镜基准。
- [官方参考合成](reference-layouts/README.md)：此前实际使用的 ESA/Gaia、ESO 参考排版源码，外部文件由使用者按来源清单自行取得。这些是参考图合成，不是原创银河或云团三维模型。

已排除失败的早期云团、实体盘和伪银河试验渲染器；它们不代表当前资产。原行星盘的早期三个建模阶段仍保留，因为最终模型确实依赖它们；默认不渲染这些已被取代的中间状态。现有其他 `production/` 目录保持原状。

## 合成依赖

实测 Node 24.19.0，`@napi-rs/canvas` 0.1.100，`sharp` 0.35.4。在本目录运行 `npm install`（官方 npm 包）；本次发布未重新安装软件。中文字体需要本地 Noto Sans CJK SC；未提供字体二进制。不同字体/引擎版本可能改变字形或像素，不保证跨平台逐字节一致。

`node test_sources.cjs` 检查 CLI 和语法；`python original-protoplanetary-disk/test_sources.py` 检查作者链指纹与 Python 语法。技术检查不替代视觉、动态播放或音频验收。
