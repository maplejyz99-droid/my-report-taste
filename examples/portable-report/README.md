# 无专有运行时的最小报告 / Portable report

Python 3.10+ 标准库即可把现有 [合成数据](../synthetic-study/source.json) 生成为中文 HTML 阅读报告和 Markdown。不需要 Node、API key、字体下载或 `@oai/artifact-tool`。这是确定性格式示例，不是代理评测、论文理解实验，也不是九张 PPT 预览的复刻器。

## 从仓库根目录运行

```bash
python3 skills/my-report-taste/scripts/doctor.py
python3 examples/portable-report/build_report.py --out dist/portable-report
```

输出：`report.html`、`report.md`、原始 `source.json`。直接用浏览器打开 HTML，不需要启动服务。报告包含研究问题、全部三行比较、百分点与相对延迟计算、方法位置和未测量条件；所有数值都来自同一份 source。输出目录已存在时拒绝覆盖；重跑请使用新目录。

自动检查：

```bash
python3 -m unittest discover -s tests -p 'test_portable_report.py'
```

打开后仍需检查实际字体、中文换行与表格。命令打印的 `rendered: false` 表示构建器没有打开浏览器，不能把生成成功当作视觉通过。本轮浏览器受本地文件访问策略限制，实际视觉核验尚未完成，详见 [本轮验证](../../docs/validation-routing-portability.md)。浏览器打印 PDF 是可选后续操作，本例不声称已验证打印分页或字体嵌入。

## 与 PPTX 示例的区别

- 这条路径：标准库生成可独立阅读的 HTML／Markdown，普通 Python 环境可运行。
- [五页 PPTX 示例](../synthetic-study/README.md)和[九种风格](../style-gallery/README.md)：可以直接下载成品；其构建器需要宿主提供 Artifact Tool。
- 现有 gallery 构建器只导出草稿。已发布成品还经过宿主最终化和 PPTX 重新导入检查；该完整后处理尚未作为可移植命令公开，不能声称运行草稿构建器就复现了同样的验收。

English: run the commands above to generate an offline HTML/Markdown reading report using only Python's standard library. Outputs deliberately use Chinese to exercise real line wrapping. No presentation engine or model is invoked. Existing outputs are never overwritten. Generation, browser inspection and skill-effectiveness evaluation are separate checks.
