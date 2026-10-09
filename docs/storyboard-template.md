# 分镜 JSON 契约 v1

[可执行的两镜头结构示例](../examples/storyboard-demo.json) 使用纯几何示意和演示来源，不声称历史事实，不是可交付历史成片。它完整演示字段、素材锁定、跨镜连续性与时间分配，不能直接转成生产模式。演示哈希不代表已存在的资产。

## 顶层字段
- schema_version: 1；mode: demo 或 production；style_id 对应 manifest。
- width、height、fps、duration_s、expected_shot_count：画幅必须16:9，镜头连续覆盖完整时长，起止时间对齐帧边界。
- sources: 唯一 id、kind（illustrative 或 factual）、url、supports。生产模式仅允许 factual 的 HTTPS 来源；审稿人还必须实际检查它是否支持断言，程序不能证明事实。
- assets: 唯一 id、version、sha256、path、rights、intact。path 为仓库/资产包相对路径；本验证器不读取资产也不证明权利。
- guide: asset_id、version、height_fraction、bbox。bbox=[x,y,w,h]，坐标以画面左上角为原点，宽高均归一化；height_fraction 约0.20，bbox 的 h 必须相同。原图比例由实际合成检查，不在示例中假定。
- captions: bbox；示例底部字幕区与向导区不重叠。实际文本边界和逐帧遮挡仍须目检。
- voice: status（deferred、temporary 或 approved）、note。

## 每个镜头必填
shot_id、start_s、end_s、narration、visual、action、camera、assets、source_ids、continuity、audio、qa。

assets 是 {asset_id, version} 列表。source_ids 引用顶层来源。continuity 包含 in、out；相邻镜头的 out 与 in 使用同一个状态标识。action 写明开始、变化、结束；camera 写固定/运动及幅度；qa 是非空检查项列表。必须引用完整向导资产，即使该镜头只让向导静止。

示例只有几何演示，不包含临时伪造的人类历史断言。生产分镜需要替换为真实脚本、事实来源和真实资产哈希，并先确认候选风格是否被选用。

## 运行
在仓库根目录运行：python scripts/validate_storyboard.py examples/storyboard-demo.json

生产验收加 --production，防止演示模式漏入交付：python scripts/validate_storyboard.py path/to/storyboard.json --production

运行拒绝样例测试：python scripts/test_storyboard_validator.py

验证器检查字段、有限数值、唯一标识、来源引用、版本锁定、时长/帧对齐、重复/重叠/空隙、向导完整性与区域、字幕区域、跨镜状态。它不渲染、不访问网络、不验证图片像素或来源内容；通过不等于历史正确、真实绑定或合格动画。
