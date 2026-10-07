# My Report Taste

**把你认可的汇报方式变成可复用的工作流，而不是反复换一套 PPT 皮肤。**

[English](README.en.md) · [风格预览](#风格预览) · [安装](docs/installation.md) · [定制自己的偏好](docs/customization.md) · [完整示例](examples/synthetic-study/README.md)

这是一个面向 Codex 的个人汇报品味 skill：组织内容、证据、叙事与密度，选择可选视觉预设，核对成品，再整理逐页中英文讲稿。支持 PPT、PDF、HTML 幻灯片和汇报型 Markdown；实际文件生成与渲染由使用环境提供。

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

## 先看内容怎样组织

同一份散乱笔记：Baseline 84% / 120 ms，Compact 86% / 85 ms，Large 86.5% / 160 ms。编辑后的页面保留全部设置、单位与合成数据身份，区分“增加 2.0 个百分点”和“延迟相对减少 29.2%”，并说明尚未测量什么。

[修改前—组织后案例](examples/synthetic-study/editing-case.md)展示这些取舍，也列出“只放大表格”时应保留的结论与页面。它是教学示例，不是已完成的有／无 skill 对照。

![合成示例结果页：完整保留准确率与延迟对照，明确标注合成数据](examples/synthetic-study/preview.png)

[完整五页 PPTX、内容计划与双语讲稿](examples/synthetic-study/README.md) · [仅需 Python 的 HTML／Markdown 重建路径](examples/portable-report/README.md) · [任务级评测方案与未验证项](docs/evaluation.md)

## 风格预览

公开版保留 35 张文字模式卡，但没有替新使用者确认任何偏好。卡片中的 approved／confirmed 是作者示例库的评价；官方模板与当前任务始终优先。

下面是 **9 个可选组合，每个组合一张代表性内容页**。它们组合了场景、内容组织、密度与视觉规则，不是 9 套互不相关的配色皮肤。全部使用同一份原创合成数据，从实际可编辑页面导出；点击图片可查看原尺寸。

单页预览只能展示页面语法，不能证明完整叙事或跨页节奏。例如酒红学术预设采用 `NAR-001 + GRD-010 + CLR-010`，不是把 `NAR-001` 简化成一种颜色。高密度报告保留自己的阅读比例。

[预设说明](skills/my-report-taste/references/author-presets.md) · [图片、可编辑单页与构建源代码](examples/style-gallery/README.md)

### 01 · 明亮蓝研究汇报

`author-light` — 研究进展与组会：先看关键变化，再核对完整比较表。

![明亮蓝研究汇报：原创合成内容页预览](examples/style-gallery/pages/author-light.png)

> 使用 $my-report-taste，选择 `author-light` 预设。先整理内容计划，再制作页面。

### 02 · 酒红学术报告

`academic-oral-wine` — 论文讲解与研究报告：酒红标题、正式证据和可见来源；此图只展示结果页语法。

![酒红学术报告：原创合成内容页预览](examples/style-gallery/pages/academic-oral-wine.png)

> 使用 $my-report-taste，选择 `academic-oral-wine` 预设。先整理内容计划，再制作页面。

### 03 · 实验与性能复盘

`experiment-review` — 实验与性能复盘：主要面积交给数据图、直接数值和比较口径。

![实验与性能复盘：原创合成内容页预览](examples/style-gallery/pages/experiment-review.png)

> 使用 $my-report-taste，选择 `experiment-review` 预设。先整理内容计划，再制作页面。

### 04 · 浅色技术架构

`technical-review-light` — 技术方案与架构讲解：用节点层级和清楚的方向解释输入输出。

![浅色技术架构：原创合成内容页预览](examples/style-gallery/pages/technical-review-light.png)

> 使用 $my-report-taste，选择 `technical-review-light` 预设。先整理内容计划，再制作页面。

### 05 · 深色技术评审

`technical-review-dark` — 短篇技术评审：低对比石油蓝背景、共享表面与连续比较表。

![深色技术评审：原创合成内容页预览](examples/style-gallery/pages/technical-review-dark.png)

> 使用 $my-report-taste，选择 `technical-review-dark` 预设。先整理内容计划，再制作页面。

### 06 · 鲜绿项目汇报

`project-green` — 项目阶段汇报：白色内容页、鲜绿焦点，突出当前里程碑和下一项证据。

![鲜绿项目汇报：原创合成内容页预览](examples/style-gallery/pages/project-green.png)

> 使用 $my-report-taste，选择 `project-green` 预设。先整理内容计划，再制作页面。

### 07 · 深蓝与沙金项目总结

`project-summary-dual-semantics` — 阶段总结：深蓝表达已有证据，少量沙金标记下一类证据需求。

![深蓝与沙金项目总结：原创合成内容页预览](examples/style-gallery/pages/project-summary-dual-semantics.png)

> 使用 $my-report-taste，选择 `project-summary-dual-semantics` 预设。先整理内容计划，再制作页面。

### 08 · 无彩证据复盘

`neutral-evidence-review` — 源码、截图或原始材料复盘：页面系统保持中性，让证据本身可读。

![无彩证据复盘：原创合成内容页预览](examples/style-gallery/pages/neutral-evidence-review.png)

> 使用 $my-report-taste，选择 `neutral-evidence-review` 预设。先整理内容计划，再制作页面。

### 09 · 高密度阅读报告

`dense-reading-report` — 会后精读与综合报告：横向 A 系列比例，同页保留数据、机制、计算口径和边界；不作为远距投影默认。

![高密度阅读报告：原创合成内容页预览](examples/style-gallery/pages/dense-reading-report.png)

> 使用 $my-report-taste，选择 `dense-reading-report` 预设。先整理内容计划，再制作页面。

私人的偏好可以放在项目 `.report-taste/profile.md`，不会被本仓库默认打包。

## 检查工具

以下命令在仓库根目录运行：

```bash
python3 skills/my-report-taste/scripts/doctor.py
python3 skills/my-report-taste/scripts/library.py route "学术 Oral" --template
python3 skills/my-report-taste/scripts/library.py route "研究进展" --preset author-light --template-state absent
python3 skills/my-report-taste/scripts/library.py route --card NAR-001 --card GRD-010 --template
python3 skills/my-report-taste/scripts/library.py validate --strict
python3 -m unittest discover -s skills/my-report-taste/tests -p 'test_*.py'
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/check_public_release.py
```

内容路由、计划比对和讲稿检查仅需 Python 标准库。验色另需 Pillow；PPTX → PDF 另需 LibreOffice，PDF 结构／字体检查另需 Poppler。详见[依赖与验证边界](docs/installation.md)。GitHub Actions 配置运行机械检查，不代表已经验证视觉质量或投影兼容。

文本路由现在只返回候选；参数表达代理已经核对的选择，不替用户作决定。[路由迁移说明](skills/my-report-taste/references/routing.md) · [0.2.0 源码更新](docs/release-notes-v0.2.0.md)

## 许可与分发

本项目自己的代码、说明和合成示例使用 [MIT License](LICENSE)。第三方原始 PPT/PDF、品牌素材、私人反馈和字体文件未随发行版分发。外部来源链接不意味着资产获得 MIT 授权；具体边界见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

希望改进项目？请阅读 [贡献说明](CONTRIBUTING.md)，提供最小的脱敏案例，不要提交私人汇报或凭据。
