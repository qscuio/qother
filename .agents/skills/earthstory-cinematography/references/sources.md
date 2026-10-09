# 来源、证据层级与读取边界

研究日期：2026-10-09。以官方制作说明、主创一手文字、机构教育/分析为依据；一般术语和项目适配由作者综合编写，不把每个启发式都称为来源原话。没有复制整篇教程，没有下载影片、截图或配乐作为资产；阅读权不等于素材再使用权。本 skill 不声称穷尽电影史或提供保证审美的算法。

## 已实际读取的基础来源

- CINE-01：[AFI, What is Cinematography and What Does a Cinematographer Do?](https://www.afi.com/news/what-is-cinematography-and-what-does-a-cinematographer-do/)。读网页摄影与视觉叙事说明；仅支持摄影应服务讲述及基本职责，不把项目规则归为AFI标准。
- CINE-02：[Nashville Film Institute, Camera Movements](https://www.nfi.edu/camera-movements/9/)。读 pan/tilt、dolly/truck、pedestal、handheld/stabilized、crane、rack focus 等术语段落。只用作基本分类交叉检查；该页部分zoom用语可能混淆远近位移，本 skill 明确改为视场变化，不照抄营销式“everything”。动作库的数字映射/禁忌是项目综合。
- CINE-03：[Nikon, Understanding Focal Length](https://www.nikonusa.com/learn-and-explore/c/products-and-innovation/understanding-focal-length)。读焦段、视场、FX/DX、定焦/变焦与类型说明。实际机位/透视区分是基础投影几何；不采用“标准焦段完全等同人眼”的过度简化。未观看页面视频。
- CINE-04：[Adobe, Perform J cuts and L cuts](https://helpx.adobe.com/in/premiere/desktop/edit-projects/trim-clips/perform-j-cuts-and-l-cuts.html)。读定义与基本操作段落；用于音画边界定义，未启动Premiere，不能称软件执行已验证。
- CINE-05：[DINFOS, One Shot–One Still](https://pavilion.dinfos.edu/Article/Article/3287623/one-shotone-still-getting-it-right-the-first-time/)。读 continuity、cutting、close-ups、composition 段落；只借鉴视觉关系与信息选择，不采用机构的其他传播目的。
- SCI-01：[NASA, Webb Telescope & The Big Bang](https://science.nasa.gov/mission/webb/big-bang-q-and-a/)。读John Mather问答的膨胀、无中心、约38万年与观测段落；不用旧版Webb未来时态描述当前任务状态，不将问答中无限宇宙措辞写成已证定论。

六个作品的来源及阅读范围逐条附于 [film-cases.md](film-cases.md)。电影案例包含主创一手文章与BFI评论，明确区分；科学纪录片以BBC制片人、Eames作品说明、NASA制作信息为基础。正文“原创迁移”的镜头不是原片镜头分析。

## 找到但未充当已读正文证据

[Documentary Making for Digital Humanists](https://www.openbookpublishers.com/books/10.11647/obp.0255)，Darren R. Reid、Brett Sanders，2021。实际读到出版页与第10/12/16章目录页；章PDF遇浏览器机器人检查，国会图书馆镜像取文失败。搜索摘录含30/180度惯例，但没有把它当完整读过章节的证据。本 skill 的连续性规则标为行业惯例与项目综合，不能据此宣称系统精读该书。不要绕过阻挡或复制第三方镜像全文。

未观看《Cosmos》片段，也未以搜索列表构造斯皮尔伯格镜头分析；《Human Planet》未作为事实拍摄范本。若未来需要精确场面、焦段或时间码，先获得可观看且合规的影片/制作资料，再记录实际版本与观测。

## 仓库适配证据

通过连接GitHub读取 qscuio/qother 固定提交 `2a9eb8acf95f21b3ac8bc70aed681eccd53e9aa9` 完整递归树（未截断），没有发现 `AGENTS.md`。读到：
- `docs/style-system.md`、`docs/production-style.md`
- `docs/storyboard-template.md`、`scripts/validate_storyboard.py`
- `.agents/skills/earthstory-scriptwriting/SKILL.md`
- `docs/opening/cosmic-origin/script.md`、`sources.json`
- `production/cosmic-origin/shot_design.py`

因此：新方案是sidecar，不能修改现camera字段类型；宇宙示例引用原source_id，仅演示镜头意图，未重新审查每个科学来源全文。系列旧纸感基线与本次写实demo授权要分开处理，镜头skill不替代任何风格skill。原作、board、render代码与资产均未改动。

## 如何继续维护

出现真实失败时补最小反例与规则，不不断增加电影名单。保存方案版本、输入、实际QA证据；改动后重跑相关行为场景。摄影设计通过不等于实现、授权或科学审稿通过。
