# 原行星盘：2.5D 有界对照与保留的三维体积方案

## 结论与当前状态

最新方向：以画质、表达效果和制作成本选择方法，不限定只能采用 2.5D。2026-10-10 的项目方向允许利用二维资产模拟三维旋转与扩展，也保留真实三维或混合方案。目前先进行 2.5D 的有界对照，输出保持 1280×720；缓存三维体积研究与已完成的小样本验证保留，后续可依据质量和成本证据选择三维或混合方案。

缓存体渲染架构已有成熟资料与实现参考；本项目的场景转换和渲染仍需验证。第一阶段小样本检查现已完成：Geometry Nodes 与实际 Cycles 对 1,024 个采样点的字段比较，最大相对误差为 0.0079%，并非逐位相同；严格绝对误差阈值 1e-4 对密度的 1.0335e-4 最大误差产生了轻微超限。闭合性与 64×64 柱状 BVH 检查中，所有柱均为零或两次交点；重复求值结果完全一致。这些证据支持继续评估导出方法，但不应宣称严格精确或完整渲染已通过。尚未进行完整体积烘焙，也未开始三相机 720p 体积场景渲染，暂无该路线的场景级性能或画质结果。

当前交付目标是六秒、1280×720 的 2.5D 运动测试：先展示旋转，再展示径向扩展的技术效果。三个选定静帧仅用于画质检查，并非带叙述的 P10 三关键帧分镜。测试不配 P10 旁白，避免把向外扩展误述为真实坍缩或吸积过程。下述三相机 720p 体积验收是保留方案的未来条件计划，不代表正在执行。

## 当前有界对照：带轻量深度的二维尘埃片

### 方法与成熟依据

使用自行制作的半透明纹理片、短弧段和少量离面尘埃，为每片保存位置、大小、朝向、颜色和固定 ID。只在 CPU 上计算绕盘旋转、径向展开、相机变换与透视投影，再按相机深度后到前合成。这些是廉价的坐标计算；不需要高精度网格、三维密度积分或逐帧物理光照。

NVIDIA 的 True Impostors 章节先解释了普通 impostor：以二维纹理卡片产生复杂几何的视觉印象，并指出视角偏离时会失真。本次采用普通分层卡片思路，不引入该章更复杂的逐像素射线求交扩展。Three.js 官方透明度教程说明后到前排序的需要，以及单个物体内部三角形和互相穿插对象的排序局限。

### 当前 CPU 可实现的路径

- 使用已有 NumPy 处理锚点、旋转和透视投影；用 PIL/NumPy 对局部图块做 alpha 合成到 1280×720。
- 将远侧盘、核心、近侧盘分开；增加少量不同高度的尘埃片，形成厚度与相对位移。
- 较长弧段拆成短片，以降低大面积交叉导致的排序错误。不要把整个盘只当作一张贴图统一缩放。
- 以固定 ID 打破相同深度的排序平局，固定纹理与随机种子，避免每帧生成不同噪声。
- 尘埃使用正常透明合成以保留暗通道和遮挡；核心辉光可单独添加。全加法叠加容易把盘体变成发光雾，失去前后层次。
- 六秒连续测试先旋转、后扩展；选择三个静帧检查层次与细节，同时检查整段播放的视差、遮挡和排序跳变。当前尚无本方法的实测速度，不能用“只是二维”推断必然实时。

### 限制与验收重点

小角度环绕与有限缩放较适合；大角度绕背、接近侧面或穿入盘体会暴露卡片。相机面对的 billboard 本身不会自动提供盘面方向，应依据片的用途选择朝向：盘面短弧保留盘面朝向，蓬松尘埃可朝向相机。预先着色不会正确响应移动光源或观察相关散射。

按中心深度排序不能解决所有相互穿插；当深度顺序交换时，需检查跳变。固定排序规则只是提高确定性，不能消除几何错误。避免一次使用过大的高不透明度片。

旋转和径向展开用于解释概念，不代表计算了真实流体运动。若画面要表示“吸积形成”，径向向外扩散也不应被直接叙述为真实形成过程，需由镜头内容决定它是展开展示还是物理变化。

这轮验收关注：同一结构可辨认、旋转与展开可读、近远层遮挡合理、连续播放不跳片、720p 细节可用。无需要求与原 Cycles 光照逐像素一致，也不将它标成高精度真实体渲染。

## 已测证据：原生离屏后端可运行

2026-10-10，本工作区使用已有 EGL/GL 动态库与自行编写的 Python ctypes 程序完成测试，无需安装软件或启动浏览器。

- 方法：eglGetPlatformDisplayEXT 的 EGL_PLATFORM_SURFACELESS_MESA，16×16 pbuffer，OpenGL API。
- EGL：1.5。
- GL_VENDOR：Mesa。
- GL_RENDERER：llvmpipe (LLVM 19.1.7, 256 bits)。
- GL_VERSION：4.5 (Compatibility Profile) Mesa 25.0.7-2+deb13u1。
- GLSL：4.50。
- 实际绘制：编译顶点和片元着色器，绘制全屏三角形，使用 sampler3D 线性采样 2×2×2 R32F 三维纹理。
- 读回像素：[128, 64, 191, 255]，与预期一致；glGetError = 0。
- 重现脚本：[egl_volume_capability_probe.py](../../scenes/original-protoplanetary-disk/experimental/cached-volume-stage1/egl_volume_capability_probe.py)。
- 默认用户目录着色器缓存不可写；测试关闭该缓存。后续也可明确使用任务可写目录。

这是 CPU 软件光栅化的成功证据，不是硬件 GPU 加速证据，也不是完整体积场景已经快速渲染的证据。当前工作区没有暴露 /dev/dri 或 /dev/nvidia*；这不能推断其他环境没有 GPU。

## 暂缓备选：缓存体积为何适合相机单独移动的镜头

当前两秒镜头只移动相机，盘体密度、几何与三盏灯保持固定。密度噪声与灯光透射不应在每一帧中重复完整求解。NVIDIA GPU Gems 第 39 章介绍三维纹理、体积光照缓存、空区域跳过与合成；第 30 章展示对三维数据进行射线步进的实现结构。

建议缓存：

1. 原材质密度、散射颜色及独立自发光分支。
2. 原闭合网格限定的有效体积区域。
3. 各固定光源的入射光或透射率；必要时用固定的面积光求积样本近似软光。
4. 可选的保守占据块，用于跳过真正空的区域。

逐帧仍计算相机射线、透射积分、散射相位与正确遮挡。各向异性参数约为 0.35，观察方向改变会改变散射，不能把某个视角的最终 RGB 当成通用体积缓存。

### 原场景保真要求

- 从最终 Blender 材质图提取实际分支，不根据早期脚本猜测最终参数。
- 不用另一种通用 Perlin 噪声替换 Blender 噪声。可先验证临时 Geometry Nodes 字段求值：复制上游 Noise/Math/MapRange/VectorMath/VectorRotate/ColorRamp 节点，用正确物体坐标采样，通过 Store Named Attribute 读回字段。节点支持与小样本求值必须先实测。
- 原发光分支来自加入细密度调制前的链，不能直接用最终密度乘颜色替代。
- 用实际闭合翘曲盘网格限定体积。可评估对每个 x/y 柱进行 BVH 垂直交点求解；若发现多区间或复杂交点，必须正确保留，不能强行简化为一个上下表面。
- 在恒星表面真实深度处处理遮挡；背景星光乘以沿视线剩余透射率。
- 光学厚度应随实际步长变化，使用与步长一致的消光积分，避免更换步数导致盘体透明度漂移。
- 保留原始 .blend 与正式参考图，实验使用独立输出。

### 适用范围

相机移动可复用缓存；密度演化、盘体变形、光源移动或强度/颜色变化可能需要重烘焙全部或部分缓存。若之后加入旋转、坍缩或湍流动画，应重新衡量更新缓存的成本，不能沿用“每帧只算相机”的速度承诺。缓存方案保留三维空间结构，但不等于物理流体模拟。

## 候选方案比较

### 1. 已有原生 EGL + Mesa llvmpipe：体积备选后端

优点：已实测创建上下文、编译着色器、采样三维纹理并读回像素；无需浏览器与新安装；可按固定相机矩阵直接导出帧。前到后体积分天然解决单一体积内部顺序，无需透明粒子排序。

边界：Mesa 是成熟后端，我们的场景转换和照明代码不是现成成熟产品。llvmpipe 消耗 CPU；需要测总时间、纹理访问开销、内存和实际画质，不能宣称实时。

### 2. Three.js WebGL2 / WebGPU：后续交互式交付候选

官方例子提供 Data3DTexture、盒体射线求交、前到后积分与提前结束。Three.js 使用 MIT 许可。WebGL2 例子的梯度近似光照并不等同于原场景灯光；还带有随帧改变的抖动和随时间旋转，不能原样作为稳定导出流程。WebGPU 示例存在不代表当前环境已有可用 WebGPU 后端。

当前浏览器执行约束尚未解决，因此不把它作为这轮本地原型的依赖；没有再次尝试受限浏览器路径。

### 3. OSPRay：成熟 CPU 离屏渲染备选

官方 API 支持 CPU、结构化体积、VDB、SciVis 与路径追踪，以及帧缓冲读回。Apache-2.0 许可。它比自行实现完整渲染器更成熟，但需确认或引入运行时，并转换材质与灯光模型；SciVis 的体积支持不能直接保证本场景美术效果。

本次没有验证本地 OSPRay 运行时，也没有安装或测量它。

### 4. OpenVDB / NanoVDB：存储与遍历组件

支持稀疏体积及加速访问。NanoVDB 不要求 CUDA，也能用于 CPU；当前 NanoVDB 核心头文件标注 Apache-2.0，OpenVDB 官网发布的整体许可为 MPL-2.0，采用时应核对实际文件与版本。

它们不是直接替代完整灯光与渲染流程的按钮。当前盘体尺度适中而且很薄，先使用各向异性的规则纹理更简单；若空区域、内存或遍历开销成为实测瓶颈，再考虑稀疏结构。

### 5. Blender Eevee：已有完整引擎，但当前证据不支持直接切换

Blender 4.3 文档说明 Eevee 使用视锥三维纹理；体积平面分辨率、深度步数与取样区间会影响细节及内存。已有项目低分辨率试验较慢且模糊，不能作为这次保留 720p 与细节的解决方案。该试验不代表硬件 GPU 上的 Eevee 性能，也不证明所有 Eevee 设置都无效。

### 6. 普通自制分层精灵与训练式 Gaussian Splatting 分开评估

普通自制二维精灵、短弧与少量轻量三维锚点，是当前六秒 2.5D 运动测试的首选方法。它不要求机器学习训练，也不要求采用 Gaussian Splatting。对这些片做透视投影、稳定深度排序和透明合成，就可以评估旋转、展开和有限视差；其代价和限制见前文。

训练式 3DGS 暂缓：它增加图像生成与训练工作。原始 INRIA 实现需要 CUDA，并采用非商业研究许可；MIT 许可的 GaussianSplats3D 查看器并不自动解决训练许可或准确转换当前盘体的问题。不能将这些训练式方案的门槛误套到普通二维精灵上。

原始三维规范场景保留作源资产与参照。新的 2.5D 方案应保留镜头需要的结构、层次和可读性，但不要求逐像素复现原 Cycles 光照，也不将其标为精确体积模拟。选择依据是成片质量、可控运动与总制作成本。

## 暂缓体积备选的有界 720p 验收计划

### 门槛 A：小样本保真

先验证材质字段求值、坐标系与网格内外判断。字段范围、稀疏程度与原图结构明显不符时，修正导出，暂不开展完整烘焙。

384×384×64 或 384×384×96 仅是各向异性网格起点建议，不是已验证足够的精度。应以原有细丝、边缘厚度和暗通道为依据检查；单看体素数量或平均误差不够。

### 门槛 B：三相机帧

使用原镜头起始、中点、结束的确切相机参数，在 1280×720 渲染。固定世界状态，无按时间变化的噪声或随机旋转。重复中点帧，核对像素一致性。

检查原图对应裁剪区：

- 原有尘埃通道和不对称结构是否保留。
- 薄边缘是否变厚、变糊或产生切片条纹。
- 前景与远侧是否仍有真实遮挡及视差。
- 恒星是否位置正确、被体积正确遮挡，有无不合理光晕。
- 光照有无过暗、平面化或过度自发光。
- 暗区和细丝是否出现新的颗粒、跳变或随视角闪动。

高频能量、结构相似性与差分图只作辅助；三维重设计中的亮度差异不能仅靠一个分数判定通过。

### 门槛 C：完整成本

分别记录：密度导出、光照缓存、编译/启动、纹理上传、逐帧渲染、读回和保存时间，以及峰值内存。比较“单次烘焙成本 + 48 帧实际成本”，不能只引用热启动着色器时间。

已有约 79–83 秒/帧的 48 帧参考成本约为一小时。新方案目前没有可报告的速度提升倍数。必须先同时通过画质与总成本检查，再展开全部 48 帧；失败则报告具体瓶颈，不自动降到 480p 或用更少样本掩盖。

## 已核查的一手来源

- NVIDIA GPU Gems 3，第 21 章，True Impostors（普通 impostor 原理与视角限制）：
  https://developer.nvidia.com/gpugems/gpugems3/part-iv-image-effects/chapter-21-true-impostors
- Three.js 官方透明度教程（后到前合成与排序局限）：
  https://threejs.org/manual/pages/transparency.html


- NVIDIA GPU Gems，第 39 章，Volume Rendering Techniques：
  https://developer.nvidia.com/gpugems/gpugems/part-vi-beyond-triangles/chapter-39-volume-rendering-techniques
- NVIDIA GPU Gems 3，第 30 章，Real-Time Simulation and Rendering of 3D Fluids：
  https://developer.nvidia.com/gpugems/gpugems3/part-v-physics-simulation/chapter-30-real-time-simulation-and-rendering-3d-fluids
- Mesa llvmpipe 文档：
  https://docs.mesa3d.org/drivers/llvmpipe.html
- Three.js 官方 WebGL2 体积云源码：
  https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/webgl_volume_cloud.html
- Three.js 官方 WebGPU 体积云源码：
  https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/webgpu_volume_cloud.html
- Three.js 许可：
  https://raw.githubusercontent.com/mrdoob/three.js/dev/LICENSE
- Blender 4.3 Eevee 体积设置：
  https://docs.blender.org/manual/en/4.3/render/eevee/render_settings/volumes.html
- Blender Geometry Nodes Noise Texture 文档（4.0 文档用于原理依据；本地版本仍需实测）：
  https://docs.blender.org/manual/en/4.0/modeling/geometry_nodes/texture/noise.html
- Blender Store Named Attribute 文档：
  https://docs.blender.org/manual/en/5.0/modeling/geometry_nodes/attribute/store_named_attribute.html
- OSPRay 官方 API 文档：
  https://www.ospray.org/documentation.html
- OSPRay 许可：
  https://raw.githubusercontent.com/RenderKit/ospray/master/LICENSE.txt
- NanoVDB FAQ：
  https://github.com/AcademySoftwareFoundation/openvdb/blob/master/doc/nanovdb/FAQ.md
- NanoVDB 核心头文件及许可标识：
  https://github.com/AcademySoftwareFoundation/openvdb/blob/master/nanovdb/nanovdb/NanoVDB.h
- OpenVDB 许可：
  https://www.openvdb.org/license/
- 原始 3DGS 实现、依赖与许可：
  https://github.com/graphdeco-inria/gaussian-splatting
  https://github.com/graphdeco-inria/gaussian-splatting/blob/main/LICENSE.md
- GaussianSplats3D 查看器许可：
  https://github.com/mkkellogg/GaussianSplats3D/blob/main/LICENSE

这些链接是本次研究核查的上游资料；含 dev/master/main 的源码会变化，正式引入代码时需要固定版本并保留对应许可。本文没有声称所有候选都在本工作区运行过，也没有引入外部场景图像。

## 可复现源码与证据

[Stage 1 源码与记录](../../scenes/original-protoplanetary-disk/experimental/cached-volume-stage1/README.md)只保留小样本字段验证与后端能力探针；未执行的大型烘焙分支、完整渲染器草稿和媒体资产均不发布。文中六秒2.5D路线为当前对照任务的范围描述，本文不宣称它已完成或画质通过。
