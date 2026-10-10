# sprite-gen 核心方法吸收

> 当前执行规则更新（2026-10-10）：用户已要求本项目“不要等我批准”。下文原集成/测试中关于分镜、构图与样片等待批准的描述仅保留历史背景；当前按[统一流程](production-workflow.md)完成内部质量复核后自主继续，不伪改过去的批准或测试事实。费用、私有外传、冻结稿与对外发布边界不因此放开。

## 范围与选择
本轮将“固定参考 → 分动作生成 → 统一画布/透明帧 → 人工挑选 → 批准版本复用”完整方法引入[人物动作素材 skill](../.agents/skills/earthstory-character-assets/SKILL.md)。主体提交文档、技能和来源许可；另经用户明确许可，修复当前主持人几何校验及其回归测试，不安装上游、不复制其代码/资产、不调用付费模型、不上传原角色、不制作视频，也不改变已冻结脚本或当前构图。技能文档可审阅，不表示具体素材或实现已通过。

选择独立的跨风格素材 skill，而不是再加一个风格：身份、状态、透明度、时序和素材版本是共同生产约束，不能混入 style-manifest.json 的 styles。现有纸感/矢量/微缩等风格、真实三维宇宙场景及当前 production-style.md 保持各自职责。用户之后明确修改状态、冻结范围或工具授权时，按新范围建立版本并重审，当前配置不是永久禁令。

## 吸收什么，为什么
- 单一获批基准与逐动作候选：让身份成为输入约束，失败能定位到某个动作，而非每次整套重画。
- 小型可复用状态库：先中性、眨眼、点头、指示等，再验证复杂动作；不直接照搬游戏攻击/奔跑和像素化默认。
- 原件与派生结果分离：保留 source、单帧与处理参数，避免人工修完却交回未修的缓存。
- 固定画布/支点/尺度与实际 alpha：将每帧可合成性作为素材质量，保护完整身体和衣物；不采用逐帧包围盒归一化。
- 非破坏式人工 curation：候选池、选择顺序、拒绝/替换与循环选择都属于正式生产信息；不得把人工选好的子集谎称原序列自动合格。
- 静态与动态分别验收：逐帧身份/解剖正确只是必要条件，循环要查末首接缝，单次动作保留边界；用户批准锁定具体状态版本后才能复用。
- 独立透明 PNG 优先：符合本项目分开保存素材的需求；保留原始单帧和选择后单帧，atlas 仅为可选派生。

## 有意不引入
上游安装器、CLI、自动纠错/插值、provider 执行、像素网格/像素还原、游戏引擎输出及 UI 服务都未集成。上游 Codex provider 涉及本地会话记录读取和清理，不进入本项目工作流，禁止由此访问或删除会话记录；OpenAI/xAI 等外部调用涉及凭据、上传和费用，需独立授权和实现审查。文档中的上游命令不是本仓库可执行步骤。

sprite-gen 不提供本项目的旁白口型同步；video.py 的 generate_audio 选项和批处理无音频路径不能推导出 lip-sync。直方图相似度、dHash、方向模型输出不构成身份保证。当前250 px圆形主持人是完整主素材的最后合成蒙版，不是小头像生成目标；实际成片仍需分镜与构图双批准。

## 固定来源与许可
只读核查基线：aldegad/sprite-gen v2.44.0，commit `3dc080aa8faa8b5a6dfe865b1247c047761f8fd1`。本地新增文本为针对本项目的中文方法改编，并非上游原文或能力保证。方法参考：
- [SKILL.md](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/SKILL.md)：路由、方法和能力边界。
- [atlas-workflow](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/docs/atlas-workflow.md)：参考锁定与分动作流水线。
- [run-contract](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/docs/run-contract.md)：原件、派生、选择后导出及一致发布。
- [curation](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/docs/curation.md) 与 [locomotion-curation](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/docs/locomotion-curation.md)：非破坏式选帧、独立候选池和显式选定子序列。
- [qa-motion](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/docs/qa-motion.md)、[states-and-frames](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/docs/states-and-frames.md)、[loop-review](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/docs/loop-review.md)：动作、循环和证据边界。
- [chroma-alpha](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/docs/chroma-alpha.md) 与 [engine-export](https://github.com/aldegad/sprite-gen/blob/3dc080aa8faa8b5a6dfe865b1247c047761f8fd1/docs/engine-export.md)：透明边缘和导出元数据参考，不移植算法。

保留上游 [Apache-2.0 LICENSE](third-party/sprite-gen-LICENSE.txt) 与 [NOTICE](third-party/sprite-gen-NOTICE.txt) 原文。NOTICE 中另列 perfectpixel-studio 的 MIT 算法归属；本次没有复制这些实现，也没有将其重新许可为本项目代码。未来若移植相应代码，应另行核对并保留对应 MIT 许可与归属。本项目改编文件为本 skill 及 references 下两份方法文档；许可保存只覆盖相应上游材料，不代表角色图、声音、模型服务或其他第三方资产已获许可。

验证与行为案例见[验收记录](tests/sprite-gen-adaptation.md)。
