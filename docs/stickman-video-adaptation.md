# 火柴人动画：独立技能与能力边界

新增入口：[create-stickman-video](../.agents/skills/create-stickman-video/SKILL.md)。用户提到「火柴人动画」「stickman-video-director 风格」时选此技能；它与带手白板手绘、流程图动态讲解并列，未替换两套现有渲染器。

## 已集成

- 六种导演预设：经典明/暗、极简科技、彩色故事、史前讽刺、治愈故事。
- 故事目标、角色身份、声音、构图、动作节拍、道具归属及转场的结构化契约。
- 离线校验器与独立提示词编译器；每个片段重复完整身份/声音约束，不依赖前文。
- 中文通用排队示例、单元测试与实际影片验收清单。
- 版本摘要绑定继续授权；支持真实的用户审阅或已委托继续，变更后不能沿用旧摘要。

## 尚未声称实现

这次交付是可运行的分镜校验和提示词包生成，不是新增 AI 视频引擎。没有提交付费生成任务，没有认证某个模型的画面质量，也没有生成火柴人视频。实际生成、音轨、剪辑和全片声画验收须使用任务当时可用且获授权的路径。预设描述不等于模型能力实测。

保留中文、现有声音选择和用户给定时长；技术口播继续使用仓库共享发音流程。事实、冻结稿和私人素材沿用原项目边界。示例为虚构排队教学情境，不是 DNX 芯片调度说明。

## 快速检查

```bash
SKILL_DIR=.agents/skills/create-stickman-video
python "$SKILL_DIR/scripts/stickman.py" validate "$SKILL_DIR/assets/queue-story.example.json"
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s "$SKILL_DIR/scripts" -p 'test_*.py'
```

示例默认 `draft`，因此不能直接编译为已放行包。先在任务工作目录复制并审查；只有已有真实对应授权和审阅证据时，记录状态、当前摘要与证据，再运行 `compile ... --out ...`。工具不自动批准项目，测试中的授权是隔离测试夹具，不是生产许可。

上游 [kaomei/stickman-video-director](https://github.com/kaomei/stickman-video-director) 采用 MIT；固定版本、改编取舍和完整许可见[来源记录](../.agents/skills/create-stickman-video/references/provenance.md)。本次没有运行上游安装脚本，也没有采用其留存率、成本或促销账号宣传。
