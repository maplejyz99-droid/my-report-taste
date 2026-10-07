# PPTX → PDF 字体安全导出

## 已验证故障

PPTX 经演示文稿渲染器显示正确，但用隔离的 LibreOffice 用户配置直接导出时，中文字体被静默替换为不相关字体，出现缺字或方框。导出进程返回成功，说明“命令成功”不能替代字体验证。

根因是隔离配置未获得可用 Fontconfig 字体目录/缓存。修复时保留隔离用户配置，同时显式提供系统字体、用户字体、任务字体目录和可写缓存；不要重定义 `HOME`。

## 推荐命令

```bash
python3 scripts/export_pptx_pdf_fontsafe.py INPUT.pptx \
  --output-dir OUTPUT_DIR \
  --font-dir /path/to/your/fonts
```

脚本按 `--soffice`、`SOFFICE` 环境变量、系统 `PATH`、Codex runtime fallback 的顺序查找 LibreOffice，并为 macOS 与 Linux 加入常见系统字体目录。它会创建临时 LibreOffice profile、Fontconfig 文件和字体缓存；只负责安全导出，成品仍须验收。

## 自动验收

```bash
python3 scripts/verify_pdf.py OUTPUT.pdf --source-pptx INPUT.pptx
```

脚本默认执行：

- 从 `presentation.xml` 按真实顺序统计可见页，排除 `show="0"` 的隐藏幻灯片，再与 PDF 页数比较。
- 从可见幻灯片的实际文本 run 提取显式 Latin／East Asian 字体；继续读取 layout、master、theme 与可选 `fontTable.xml`，把继承或声明字体列为候选而非一律硬失败。
- 解析 `pdffonts`，检查字体嵌入与 Unicode map；比较前移除 PDF 子集前缀。
- PPTX 含中文时自动逐页比较源文本与 `pdftotext` 的 CJK 覆盖；图片中的中文不进入源文本，因此不会被错误要求提取。
- 将页数不符、未嵌入字体、显式期望字体缺失和严重中文丢失列为 ERROR；主题占位符、额外候选字体和局部 Unicode 风险列为 WARNING。

需要时可补充或覆盖自动推断：

```bash
python3 scripts/verify_pdf.py OUTPUT.pdf --source-pptx INPUT.pptx \
  --expect-font "Source Han Sans CN" \
  --allow-font Arial \
  --deny-font "Noto Sans CJK JP" \
  --font-alias "Source Han Sans CN=SourceHanSansCN"
```

人工验收仍包括：

- 全部页面栅格化后检查字形、换行、溢出、裁切、透明度和图表标签。
- 生成缩略图总览，确认视觉节奏与页面骨架没有导出后漂移。

## 文件晋级规则

1. 导出到 staging 目录。
2. 验证字体、文本和页面渲染。
3. 失败文件保留在 `diagnostics/`，记录替代字体与故障原因。
4. 只有全部通过后才复制/移动为最终文件名。

禁止未经验证的 Office 导出直接覆盖已通过验收的 PDF。
