# My Report Taste

**把你认可的汇报方式变成可复用的工作流，而不是反复换一套 PPT 皮肤。**

[English](README.en.md) · [安装](docs/installation.md) · [定制自己的偏好](docs/customization.md) · [完整示例](examples/synthetic-study/README.md)

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

## 默认中性，风格可选

公开版保留 35 张文字模式卡，但没有替新使用者确认任何偏好。卡片中的 approved／confirmed 是作者示例库的评价。所有视觉组合都需要明确选择；官方模板始终优先。

- `author-light`：明亮蓝研究汇报。
- `NAR-001`：学术叙事，配合角色自适应密度；兼容时可采用酒红视觉。
- 其他方向：深色技术评审、鲜绿项目汇报、无彩证据页、独立阅读报告。

见[预设入口](skills/my-report-taste/references/author-presets.md)。私人的偏好可以放在项目 `.report-taste/profile.md`，不会被本仓库默认打包。

## 一个不需要私人论文的完整示例

[合成研究示例](examples/synthetic-study/README.md)包含原始数据、任务简报、逐页计划、演示成品、双语讲稿和验证说明。所有数据都明确标记为教学用合成值，不代表真实实验发现；没有复用私人论文、会议 Logo 或外部图表。

![合成示例结果页：完整保留准确率与延迟对照，明确标注合成数据](examples/synthetic-study/preview.png)

## 检查工具

以下命令在仓库根目录运行：

```bash
python3 skills/my-report-taste/scripts/library.py route "学术 Oral 官方模板"
python3 skills/my-report-taste/scripts/library.py route "author-light 研究进展"
python3 skills/my-report-taste/scripts/library.py validate --strict
python3 -m unittest discover -s skills/my-report-taste/tests -p 'test_*.py'
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/check_public_release.py
```

内容路由、计划比对和讲稿检查仅需 Python 标准库。验色另需 Pillow；PPTX → PDF 另需 LibreOffice，PDF 结构／字体检查另需 Poppler。详见[依赖与验证边界](docs/installation.md)。GitHub Actions 配置运行机械检查，不代表已经验证视觉质量或投影兼容。

## 许可与分发

本项目自己的代码、说明和合成示例使用 [MIT License](LICENSE)。第三方原始 PPT/PDF、品牌素材、私人反馈和字体文件未随发行版分发。外部来源链接不意味着资产获得 MIT 授权；具体边界见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

希望改进项目？请阅读 [贡献说明](CONTRIBUTING.md)，提供最小的脱敏案例，不要提交私人汇报或凭据。
