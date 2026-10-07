# 合成研究示例

这不是论文，不是真实实验，也不是通用模板。它展示如何把一个小型证据集整理成短汇报，并保留可检查的内容对应关系。

## 建议阅读顺序

1. [任务简报](brief.md) 与 [原始合成数据](source.json)：确认问题、单位和不能声称的内容。
2. [逐页计划](slide-plan.md)：4 页主讲、1 页备份；每页有主张、证据和衔接。
3. [可编辑 PPTX](demo.pptx)：5 页静态示例，表格和文字为原生对象。
4. [英文讲稿](script-en.md) 与 [中文讲稿](script-zh.md)：相同页 ID、角色；每张主讲页都有实际缩写的短稿。
5. [验证记录](verification.md)：说明实际运行的检查、人工核对及未验证事项。

本示例选择 `author-light`，不是要求所有安装者采用它。每页明确标注合成数据，没有品牌图片或论文截图。

## 无额外依赖即可复现的检查

在仓库根目录运行：

```bash
python3 skills/my-report-taste/scripts/verify_deck_plan.py examples/synthetic-study/slide-plan.md examples/synthetic-study/demo.pptx
python3 skills/my-report-taste/scripts/check_speaker_script.py examples/synthetic-study/script-en.md --language en --paired examples/synthetic-study/script-zh.md --paired-language zh --minutes 3
python3 skills/my-report-taste/scripts/check_speaker_script.py examples/synthetic-study/script-en.md --language en --short --minutes 3
```

跨语言数字提示可能不同：英文用 `percent`，中文用 `%`。这是人工核对提示，不要为了使检查全绿而破坏自然讲法。检查记录明确说明处理方式。

## 重新生成 PPTX

[build_deck.mjs](build_deck.mjs) 保留创建源代码，读取同目录的 JSON 和页面标题。它需要宿主环境已经提供 `@oai/artifact-tool` 与 Node.js，不属于本项目自带或标准库依赖；不能据此声称在任意新机器上可直接构建 PPTX。

依赖可用时运行：

```bash
node examples/synthetic-study/build_deck.mjs /path/to/new-draft.pptx Arial
```

输出仅为 draft；重新核对字体可用性、页面计划和所有页的实际渲染。没有该库时，仍可打开已交付 PPTX、运行上述标准库检查，或用自己的制作工具复用 JSON 与计划。数据检查可复现不等于视觉结果在所有 Office 版本相同。
