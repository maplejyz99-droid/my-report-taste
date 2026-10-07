# My Report Taste

**把你认可的汇报方式变成可复用的工作流，而不是反复换一套 PPT 皮肤。**

[English](README.en.md) · [风格预览](#风格预览) · [配色编号](#配色编号怎么看) · [安装](docs/installation.md) · [定制自己的偏好](docs/customization.md) · [完整示例](examples/synthetic-study/README.md)

这是一个面向 Codex 的个人汇报品味 skill：按“内容任务 → 证据与密度 → 视觉外观”组织材料，核对成品，再整理逐页中英文讲稿。支持 PPT、PDF、HTML 幻灯片和汇报型 Markdown；实际文件生成与渲染由使用环境提供。

## 它解决什么

- 先梳理论文或实验，再决定每页放什么；原图、表格、公式有明确去向。
- 保留官方模板与当前用户意图，不把作者喜欢的颜色当作所有人的默认。
- 区分真正的证据密度与缩字堆内容，避免连续套用同一种卡片页。
- 修订时保护已确认的结论与主线，记录页序、角色和立场变化。
- 讲稿对应实际版本，中英文分别计数与估时；短版必须有真正缩短的正文。
- 区分机械检查、视觉核验、事实核验和真人试讲，不用一个 PASS 冒充全部完成。

它不是自动保证“好看”的生成器，不自带 PowerPoint 引擎，不会自动上传材料，也不能替代研究者核对科学结论。

## 快速开始

需要 Python 3.10+。下载本仓库后，在仓库目录运行：

```bash
git clone https://github.com/maplejyz99-droid/my-report-taste.git
cd my-report-taste
python3 tools/install.py
```

默认安装到 `~/.agents/skills/my-report-taste`；若已有同名版本会停止，不覆盖个人库。也可以使用项目级安装，见[安装说明](docs/installation.md)。目前按 Codex 官方本地 skill 发现机制组织；其他代理产品需自行验证，未宣称全平台兼容。

之后在 Codex 中调用：

> 使用 $my-report-taste。我要做一份英文会议 Oral，已有官方模板。先核对论文的主张、图表和方法，再给逐页内容计划，暂时不做 PPT。

> 使用 $my-report-taste，按当前 PPT 的实际页序写中文和英文讲稿。主讲目标 12 分钟，备份页不计时，给出真正可讲的短版。

> 使用 $my-report-taste。收藏这份报告的表格组织方式，不收藏它的颜色；记录适用场景和来源。

## 三类内容任务，不是九套内容套路

先判断这次汇报要完成什么，再决定重点和顺序：

| 内容任务 | 主要回答的问题 |
|---|---|
| 研究／技术讲解（explain） | 研究对象是什么，方法如何工作，证据支持什么？ |
| 进展／结果汇报（progress） | 相比之前，新增证据改变了什么判断，还有什么没解决？ |
| 方案比较／选择（compare） | 按相同标准看，各方案的收益、代价与约束是什么？ |

比较不等于推荐；只有任务需要选择时才给有条件的倾向。同一报告可以以一种任务为主、局部借用另一种，不强制目录、页数、三个 bullet 或独立未来工作页。

证据形式和密度再按材料、受众与阅读距离决定；最后采用官方模板、自己的偏好或下方呈现候选与配色。**换成绿色不应多出里程碑，换成酒红也不应凭空补出研究议程。**

直接说明任务即可，不需要先学参数：

> 使用 $my-report-taste。组里已经知道背景，重点讲这次实验改变了什么判断。外观借用 project-green，不增加里程碑或部署建议。

> 使用 $my-report-taste。只比较这几种方案的收益与代价，暂时不替我们选。已有内容不变，只把外观调整为 academic-oral-wine。

给代理或自动化使用时，`--content` 选任务，`--visual` 仅借呈现，`--preset` 明确选完整组合，`--card` 选单个维度。[内容取舍规则](skills/my-report-taste/references/content-modes.md) · [参数与兼容说明](skills/my-report-taste/references/routing.md)

减少模板感首先靠内容编辑：保留具体对象与证据，删掉重复背景和无信息增量的总结，给难点足够篇幅。不是禁用某些词，也不是要求每页换一种布局；现有检查不能保证生成稿已经“没有 AI 味”。

## 先看内容怎样组织

同一份散乱笔记：Baseline 84% / 120 ms，Compact 86% / 85 ms，Large 86.5% / 160 ms。编辑后的页面保留全部设置、单位与合成数据身份，区分“增加 2.0 个百分点”和“延迟相对减少 29.2%”，并说明尚未测量什么。

[修改前—组织后案例](examples/synthetic-study/editing-case.md)展示这些取舍，也列出“只放大表格”时应保留的结论与页面。它是教学示例，不是已完成的有／无 skill 对照。

![合成示例结果页：完整保留准确率与延迟对照，明确标注合成数据](examples/synthetic-study/preview.png)

[完整五页 PPTX、内容计划与双语讲稿](examples/synthetic-study/README.md) · [仅需 Python 的 HTML／Markdown 重建路径](examples/portable-report/README.md) · [任务级评测方案与未验证项](docs/evaluation.md)

## 风格预览

这里按**候选呈现方向、页面类型、阅读方式和配色**分别展示，不再把原来的九个便捷组合都称作独立主题。三类内容任务保持不变。

- 原 01／03／04 合并为“浅色编辑式”入口，指标页、实验图表页和架构页作为同一体系下的页型。
- 高密度阅读报告单列为阅读版式，不与配色主题并排计数。
- 下方六个方向用于对照，**不是六套已经证明互不重复的主题**。旧预设 ID 和调用方式仍兼容。

### 同内容对照

每个候选都展示相同的两页：左为结果比较，右为机制解释。标题、三组数据、两项差值、四个机制节点及限制说明保持一致；改变的是证据摆放、导航、文字层级与配色。所有数值来自原创合成数据。

[完整对照说明与可编辑文件](examples/style-gallery/comparison/README.md) · [保留的九张旧页型示例](examples/style-gallery/README.md) · [配色编号](#配色编号怎么看)

### 01 · 浅色编辑式

蓝色的指标、实验图表、架构流程统一归入这个入口。页面职责决定用表格还是流程，不再把换页型称作换主题。

![浅色编辑式：相同结果页与机制页对照](examples/style-gallery/comparison/pages/light-editorial/preview.png)

[结果页原图](examples/style-gallery/comparison/pages/light-editorial/result.png) · [机制页原图](examples/style-gallery/comparison/pages/light-editorial/mechanism.png) · [两页可编辑 PPTX](examples/style-gallery/comparison/pages/light-editorial/example.pptx)

配色：[CLR-002](skills/my-report-taste/references/CLR-002.md)；沿用调用 `--visual author-light`。这里的展示名称不是新增 CLI 参数。

旧的 `experiment-review` 和 `technical-review-light` 仍保留原有工程证据／流程规则，不静默改写成同一个路由；只合并 README 的主题入口。原案例按[指标与表格](examples/style-gallery/pages/author-light.png)、[实验图表](examples/style-gallery/pages/experiment-review.png)、[架构流程](examples/style-gallery/pages/technical-review-light.png)查阅。

### 02 · 学术证据式

以正式证据为主体，解释与来源有固定位置。这里保留酒红作示范，但学术证据组织不依赖酒红，也不额外加载 NAR-001 叙事。

![学术证据式：相同结果页与机制页对照](examples/style-gallery/comparison/pages/academic-evidence/preview.png)

[结果页原图](examples/style-gallery/comparison/pages/academic-evidence/result.png) · [机制页原图](examples/style-gallery/comparison/pages/academic-evidence/mechanism.png) · [两页可编辑 PPTX](examples/style-gallery/comparison/pages/academic-evidence/example.pptx)

配色：[CLR-010](skills/my-report-taste/references/CLR-010.md)；沿用调用 `--visual academic-oral-wine`。这里的展示名称不是新增 CLI 参数。

### 03 · 深色编辑式

深石油蓝背景、共享蓝灰表面和明度层级。结果页与机制页都采用主证据／解释的强分区，不默认增加金色。

![深色编辑式：相同结果页与机制页对照](examples/style-gallery/comparison/pages/dark-editorial/preview.png)

[结果页原图](examples/style-gallery/comparison/pages/dark-editorial/result.png) · [机制页原图](examples/style-gallery/comparison/pages/dark-editorial/mechanism.png) · [两页可编辑 PPTX](examples/style-gallery/comparison/pages/dark-editorial/example.pptx)

配色：[CLR-003](skills/my-report-taste/references/CLR-003.md)；沿用调用 `--visual technical-review-dark`。这里的展示名称不是新增 CLI 参数。

### 04 · 轻导航浅色

在白色内容区上加入细边导航与小型章节胶囊。保留既有鲜绿配色；与浅色编辑式仍有重叠，暂不宣称是完全独立的主题。

![轻导航浅色：相同结果页与机制页对照](examples/style-gallery/comparison/pages/green-navigation/preview.png)

[结果页原图](examples/style-gallery/comparison/pages/green-navigation/result.png) · [机制页原图](examples/style-gallery/comparison/pages/green-navigation/mechanism.png) · [两页可编辑 PPTX](examples/style-gallery/comparison/pages/green-navigation/example.pptx)

配色：[CLR-006](skills/my-report-taste/references/CLR-006.md)；沿用调用 `--visual project-green`。这里的展示名称不是新增 CLI 参数。

### 05 · 侧轨证据式

固定窄侧轨组织导航，主体保留连续证据。结果页以少量沙金标记第二指标；机制页没有必要的第二颜色语义，因此不强加沙金。

![侧轨证据式：相同结果页与机制页对照](examples/style-gallery/comparison/pages/rail-evidence/preview.png)

[结果页原图](examples/style-gallery/comparison/pages/rail-evidence/result.png) · [机制页原图](examples/style-gallery/comparison/pages/rail-evidence/mechanism.png) · [两页可编辑 PPTX](examples/style-gallery/comparison/pages/rail-evidence/example.pptx)

配色：[CLR-007](skills/my-report-taste/references/CLR-007.md)；沿用调用 `--visual project-summary-dual-semantics`。这里的展示名称不是新增 CLI 参数。

### 06 · 无彩编辑式

通过字号、位置、细线和灰度组织证据。原始素材可保留颜色；这次纯表格／流程对照未覆盖照片、截图与跨页节奏，独立性仍待更多材料验证。

![无彩编辑式：相同结果页与机制页对照](examples/style-gallery/comparison/pages/neutral-editorial/preview.png)

[结果页原图](examples/style-gallery/comparison/pages/neutral-editorial/result.png) · [机制页原图](examples/style-gallery/comparison/pages/neutral-editorial/mechanism.png) · [两页可编辑 PPTX](examples/style-gallery/comparison/pages/neutral-editorial/example.pptx)

配色：[CLR-008](skills/my-report-taste/references/CLR-008.md)；沿用调用 `--visual neutral-evidence-review`。这里的展示名称不是新增 CLI 参数。

## 独立阅读版式

`dense-reading-report` — 独立阅读型密度，预览采用横向 A 系列比例；不是远距投影默认，也不自动改变目标格式。

![高密度阅读报告：原创合成内容页预览](examples/style-gallery/pages/dense-reading-report.png)

配色卡：**无固定 CLR 编号**。该组合选取 `GRD-004 + OTH-003`，不绑定颜色；下图仅记录[当前示例构建器](examples/style-gallery/build_gallery.mjs)的实际取值，不是新增配色预设，也不是 `CLR-010`。

![高密度阅读报告的示例用色，无固定 CLR 编号](examples/style-gallery/palettes/dense-example.svg)

- 示例强调 `#96324A`；浅底 `#FAEFF2`；画布 `#FFFFFF`。
- 正文 `#27242A`；辅助文字 `#656068`；线条 `#E2DADF`。

实际使用时可以另选配色卡，或沿用用户／官方模板；改变颜色不改变阅读型密度。

> 使用 $my-report-taste，只借用 `dense-reading-report` 的呈现规则；内容按当前任务组织，保留已确认主线与证据。

## 配色编号怎么看

`CLR` 是配色卡，`GRD` 是版式／密度卡，`NAR` 是叙事卡。它们可以分别选取。六套配色不等于六条内容路线，也不能单凭颜色证明版式独立。

以下色值来自既有配色卡，是近似重建配方，不是外部品牌的官方色值。等大的色块仅用于查色，不代表页面用色面积；示例页会按角色选取色阶。高密度阅读示例的用色已在上方单独标注，不新增 CLR 编号。

> 使用 $my-report-taste，只采用 CLR-006 配色；内容、页序与版式保持不变，风险色仅在有实际风险时使用。

配色卡：[CLR-002 · 明亮蓝](skills/my-report-taste/references/CLR-002.md)

![CLR-002 配色：主蓝、浅蓝、冷白画布与深灰正文](examples/style-gallery/palettes/CLR-002.svg)

- 主蓝 `#0B6FCA`；深蓝 `#075CA8`；浅蓝 `#91C5F0`；淡蓝底 `#DDE9F4`。
- 画布 `#F7F7F7`；表面 `#FFFFFF`；正文 `#343A40`；辅助文字 `#6B737A`；线条 `#DCE3E8`。

珊瑚色 `#FE7265` 仅标记真实风险／异常，不作为普通方法分类色。

配色卡：[CLR-010 · 学术酒红](skills/my-report-taste/references/CLR-010.md)

![CLR-010 配色：酒红标题、浅酒红强调底、来源蓝与冷白背景](examples/style-gallery/palettes/CLR-010.svg)

- 标题 `#7D1E2F`；局部强调 `#A12746`；浅酒红底 `#FAE9EC`；引用／链接 `#0077CC`。
- 画布 `#FFFFFF`；表面 `#F3F4F6`；正文 `#1F2430`；辅助文字 `#666A73`；线条 `#D9DCE3`。

来源蓝不承担普通装饰；紫色／深蓝分支色仅在确有对应语义时启用，完整取值见配色卡。

配色卡：[CLR-003 · 深石油蓝](skills/my-report-taste/references/CLR-003.md)

![CLR-003 配色：深石油蓝背景层次、蓝灰表面和浅色正文](examples/style-gallery/palettes/CLR-003.svg)

- 背景锚点 `#071F29` → `#173F4B`，边缘 `#01080C`；表面 `#1B313A`／`#243B45`。
- 正文 `#E7E9EA`；辅助文字 `#A5AFB2`；线条 `#536168`；低饱和焦点 `#C5CBC9`。

这些是柔和背景明暗层的取值，不是要铺成分段渐变条。默认不加金色；`#C9A84A` 仅为有明确唯一焦点时的条件候选。

配色卡：[CLR-006 · 鲜绿与薄荷浅阶](skills/my-report-taste/references/CLR-006.md)

![CLR-006 配色：鲜绿主色、薄荷浅阶和白色画布](examples/style-gallery/palettes/CLR-006.svg)

- 主绿 `#00A273`；深绿 `#008C63`；中绿 `#31B58D`；浅绿 `#9FDBCA`；薄荷底 `#E5F6F1`。
- 画布 `#FFFFFF`；正文 `#171A18`；辅助文字 `#5F6763`；线条 `#CEDBD6`。

橙色 `#F07F3C` 仅用于异常；黄色 `#F2D84C` 仅在同图存在独立第二指标时启用，都不是日常装饰色。

配色卡：[CLR-007 · 深蓝与沙金](skills/my-report-taste/references/CLR-007.md)

![CLR-007 配色：深蓝主证据、可选沙金第二语义和白色画布](examples/style-gallery/palettes/CLR-007.svg)

- 主蓝 `#284B7D`；中蓝 `#5F86B8`；浅蓝 `#CBD9ED`；第二语义沙金 `#E8CDA9`。
- 画布 `#FFFFFF`；正文 `#252525`；辅助文字 `#8E8E8E`；线条 `#D8DADD`。

色卡中的 `Second role *` 表示**有第二语义才用沙金**，不做蓝金各半，也不把沙金当风险色。辅助灰只用于短标签，投影前须复核对比度。

配色卡：[CLR-008 · 黑白灰](skills/my-report-taste/references/CLR-008.md)

![CLR-008 配色：近黑、深灰、白色与冷中性灰](examples/style-gallery/palettes/CLR-008.svg)

- 正文／关键系列 `#222222`；深灰表面 `#555555`；辅助文字 `#707070`。
- 画布 `#FFFFFF` 或 `#F7F7F7`；线条 `#D0D0D0`。

没有固定的彩色强调色。照片、截图保留原色，但其颜色不自动扩展为全局主题。

私人的偏好可以放在项目 `.report-taste/profile.md`，不会被本仓库默认打包。

## 检查工具

以下命令在仓库根目录运行：

```bash
python3 skills/my-report-taste/scripts/doctor.py
python3 skills/my-report-taste/scripts/library.py route "学术 Oral" --template
python3 skills/my-report-taste/scripts/library.py route --content explain --template
python3 skills/my-report-taste/scripts/library.py route --content progress --visual author-light --template-state absent
python3 skills/my-report-taste/scripts/library.py route --content compare --visual technical-review-dark --template-state absent
python3 skills/my-report-taste/scripts/library.py route --card NAR-001 --card GRD-010 --template
python3 skills/my-report-taste/scripts/library.py validate --strict
python3 -m unittest discover -s skills/my-report-taste/tests -p 'test_*.py'
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/check_public_release.py
```

内容路由、计划比对和讲稿检查仅需 Python 标准库。验色另需 Pillow；PPTX → PDF 另需 LibreOffice，PDF 结构／字体检查另需 Poppler。详见[依赖与验证边界](docs/installation.md)。GitHub Actions 配置运行机械检查，不代表已经验证视觉质量或投影兼容。

文本路由只返回未激活的候选；参数表达代理已经核对的选择，不替用户作决定。旧的九个预设 ID 和 `--preset` 保持可用。[路由迁移说明](skills/my-report-taste/references/routing.md) · [0.3.0 变更与本地验证](docs/release-notes-v0.3.0.md)

## 许可与分发

本项目自己的代码、说明和合成示例使用 [MIT License](LICENSE)。第三方原始 PPT/PDF、品牌素材、私人反馈和字体文件未随发行版分发。外部来源链接不意味着资产获得 MIT 授权；具体边界见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

希望改进项目？请阅读 [贡献说明](CONTRIBUTING.md)，提供最小的脱敏案例，不要提交私人汇报或凭据。
