# SRT 驱动的暖纸流式手绘

在已有白板 skill 中选择 `warm-paper-stream` 主题，不另建一个重复 agent。

## 已接入的能力

- 读取 SRT 的实际时间，保留字幕全文、空隙及原时间轴；每个语义绘图 beat 明确引用 cue ID。
- 使用原有矢量笔迹与独立填色多边形，按部位先描线再添彩；不是矩形擦除静态图。
- 画布可设置 RGB `background`，主题使用 `[245,235,215]`；深灰轮廓、少量低饱和强调色。
- 所有字幕必须有画面关联，绘图窗口不得重叠，结尾留出手退出和至少半秒观察时间。
- 文本可保留技术标识和字幕。生成插画时不把文字烘焙进图片，独立排版，避免文字失真。

## 用法

准备与音频同一版本的 SRT，以及包含 `duration_ms`、`caption_timing`、`beats` 的 JSON。
每个 beat 包含 `id`、`narrative_role`、`cue_ids`、`start_ms`、`end_ms` 和现有渲染器格式的 `parts`。

```bash
python "$SKILL_DIR/scripts/srt_storyboard.py" narration.srt beats.json storyboard.json
python "$SKILL_DIR/scripts/render_whiteboard.py" storyboard.json --audio narration.wav --font "$CJK_FONT" --output whiteboard.mp4
```

先按实际字幕语义写分镜和绘图部位，再运行编译器；编译器不会猜测图像内容或自动生成插画。
资产中的 `srt-paper.example.srt` 和 `srt-paper.example.json` 是可编译的无声预览案例，不能当作音频对齐证据。
`caption_timing` 仅接受已有 measured/provider/forced-alignment 或 `preview_only` 声明；生产仍须验证 SRT 与当前 master 一致。

建议一幕只讲清一个关系，25–35 秒可作为初始估计，不机械切断句子或为了满足时长重复镜头。
多幕分开编译、按现有生产流程拼接视觉，再与唯一 narration master 合成；不能各幕擅自增加尾帧导致全片音画漂移。

## 从上游吸收、但有边界的设计

参考 geeklee/srt-whiteboard-animation，固定版本 `696a7243c0e6ffb6827676e539c2ca5ebae2bf6b`（检查日期 2026-10-17），MIT，作者 江哥是老登啊。
仓库：https://github.com/geeklee/srt-whiteboard-animation
许可证：https://github.com/geeklee/srt-whiteboard-animation/blob/696a7243c0e6ffb6827676e539c2ca5ebae2bf6b/LICENSE

吸收字幕事件决定绘制顺序、持久画布、轮廓后填色和暖纸配色。这里是独立编写的矢量适配，不复制其渲染器、手部素材或预览台，也没有安装或执行上游代码。

若未来加入栅格线稿模式，需要单独实现和验证如下合同，不能声称现有适配器已支持：
- 查看原图像素后标注真实区域；每区域允许掩码扣除后续区域与保护区。
- 路径落墨和填色均受同一掩码约束；笔尖不能穿越未绘制主体留下连接线。
- 区域矩形代理预览只用于编排，不是最终笔迹预览。
- 上游 grid/skeleton 路线不保证汉字书写笔顺；汉字继续用真实笔画数据。
- 不在结尾直接切回完整原图来掩盖漏画，否则会提前显示未覆盖内容或造成跳变。

本项目不采纳每一步强制等用户确认的流程；按用户已有授权自检推进，只在真实决策或权限缺失时询问。技术 diagram 流程仍无手，以因果状态变化为主，不因为主题选择失去标识或正确性。

## 验收

运行新编译器测试及既有 renderer tests；渲染代表帧，检查开头底色、进行中实际笔迹、未出现主体、完成画面和退出。
SRT 全覆盖检查只证明存在关联，不证明画面解释正确；逐 beat 审阅叙事语义。自动测试也不证明配音自然。
