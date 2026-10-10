# 下一步：可寻址网页合成的隔离试验

状态：候选计划，未安装、未运行、未测得性能改善。现有 Blender 场景、48 帧任务、生产时间线保持原状。

## 选择

优先试验 HyperFrames 的 HTML 合成层，适用于字幕、图解、二维动态、已有视频/透明层以及轻量 Three.js 场景。它与现有非 React 管线衔接较短；Apache-2.0 核心可本地使用，无强制逐渲染付费。运行条件是 Node 22+、Chromium/浏览器能力和 FFmpeg，仍有安装/资产/许可证检查。不要启用托管渲染、AWS、发布或付费媒体服务来完成本地试验。

Remotion 作为已有 React/R3F 项目或需要其组件生态时的候选。当前自定义许可对个人、合资格小团队和非营利等有免费范围；其他情况需要 Company License，实际版本须复核。官方 skills 未找到明确再分发许可，故只链接参考。GSAP 免费商用但自定义条款限制竞争性无代码动画编辑器；不一概禁止，也不当 MIT。试验可先以不含 GSAP 的显式时间 canvas/Three.js 或 Anime.js 路径隔离风险。

两者都不会自动降低 Blender 体积光/路径追踪的成本。降分辨率、简化体积、烘焙、换实时材质是不同画质取舍，需要同场景对比。网页轻量图解快于重体积场景并不是公平速度结论。

## 已读上游真实接口

HyperFrames 读取基线：6f3f86a9c9824c8ad5b7bf760375e243466e5ee0。

- packages/core/src/runtime/adapters/three.ts 发出 hf-seek 并写入 __hfThreeTime；场景仍自行设置状态并 renderer.render。显式 duration 必须给出。加载管理只会检查它能发现的 window.THREE；ES module 私有 namespace、定制加载器和 CPU/着色器初始化不可假定被自动等待，必须用经过验证的就绪承诺。
- skills/hyperframes-animation/adapters/three.md 的 buildReady hold 须同步注册且 key 唯一；迟注册不能保证捕获前就绪。模型/纹理要在抓帧前冻结成本地资产。
- packages/core/src/runtime/adapters/animejs.ts 对 __hfAnime 注册实例调用 seek(seconds×1000)；v4 不能依赖 anime.running 自动发现，autoplay 关闭。该 adapter 会捕获实例异常，因而“渲染命令完成”不等于每个动画成功，必须检测日志/像素及预期状态。
- Core 说明 lint 错误会使布局/对比度检查跳过，0 samples 或 0/0 不能算通过。渲染报告须记录 beginframe/screenshot 路径、GPU/软件模式与各阶段耗时。

源文件： https://github.com/heygen-com/hyperframes/tree/6f3f86a9c9824c8ad5b7bf760375e243466e5ee0

## 最小可验收试验

先检测执行环境和已有依赖，锁定具体 npm 发布版本及 lockfile。只在隔离目录制作一个 2 秒、48 帧、固定分辨率的原创图解 fixture：主体位移、中文标签、一次明确切换、末尾 hold；不复制外部角色/字体/素材，不用远程 API。

1. 同一输入顺序、乱序和重复取帧；输出解码像素/合理容差与状态证据。测试字体缺失、资产失败、初始化迟到、动画实例异常和中途取消，失败不得覆盖已验证缓存。
2. 对切前后与 hold 边界抽帧；完整导出并观看。检查实际帧数、fps、SAR=1、尺寸、时长、色彩标记及意外黑帧。
3. 接入现有 per-shot 缓存边界，仅改一镜、仅平移前镜时间、换共享字体各测失效范围。不要让上游全片并行替代逐镜缓存。
4. 分别报告冷启动/准备、捕获、编码和总耗时；先一 worker，再有限并发。记录 CPU/GPU/内存、质量参数与是否启用子帧模糊。以同内容、同尺寸、同帧率和可比视觉质量作基线，不把营销 benchmark 当本机实测。
5. 对带真实音频的后续 fixture 才测声画同步、尾音及混音；静音试验不得宣称音频已通过。

停止条件：确定性/就绪/边界/导出/缓存有一项失败就记录未通过并诊断；出现新付费、私有上传、凭据或授权需求暂停对应步骤。达到以上证据后才考虑作为可选后端，不迁移全片或宣称总流程完成。
