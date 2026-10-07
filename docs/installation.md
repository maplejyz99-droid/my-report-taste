# 安装与运行依赖

## 本地安装

在下载或 clone 的仓库根目录运行：

```bash
python3 tools/install.py
```

安装目录为 `~/.agents/skills/my-report-taste`。脚本不登录账号、不修改 Codex 全局配置、不启动渲染器，也不覆盖已有安装。检测到旧 `~/.codex/skills/my-report-taste` 时，同样保留并提示，避免重复同名 skill。

项目级安装：

```bash
python3 tools/install.py --dest /path/to/project/.agents/skills
```

`--dest` 指父级 skills 目录，不是 skill 目录本身。升级前先备份自己的偏好与收藏，在新目录检验新版，再自行迁移；没有提供隐式覆盖的 force 选项。

Codex 官方文档描述了 `.agents/skills` 的项目／用户发现路径，以及显式调用和刷新方式。若安装后没有显示，可重启 Codex。这里只承诺本地文件布局符合该机制，不代表已在所有版本、操作系统或其他代理产品中验证。[官方 Build skills 文档](https://learn.chatgpt.com/docs/build-skills)

## 分层依赖

- Python 3.10+：目录检索、路由、计划/PPTX 结构比对、讲稿检查、安装与打包。无需 API key。
- Pillow：仅图像配色检查需要；在自己的虚拟环境安装 `skills/my-report-taste/requirements.txt`。
- LibreOffice：可选的 PPTX → PDF 导出。使用 `--soffice`、`SOFFICE` 或 PATH 指定；不要假设所有机器都有 Codex 内置运行时。
- Poppler：可选 PDF 页数、字体与文本检查需要 `pdfinfo`、`pdffonts`、`pdftotext`；栅格化预览可用 `pdftoppm`。
- 幻灯片制作工具：根据宿主环境选用。该 skill 不内置 PowerPoint、HTML 框架或付费渲染服务。

公开包不附字体。使用目标设备已有字体，或从字体官方项目下载并遵守许可。不能因为文档列出某字体，就假设目标机器已安装；使用 PDF 交付时仍需检查字体嵌入与实际渲染。

## 可直接运行的检查

```bash
python3 skills/my-report-taste/scripts/doctor.py
python3 skills/my-report-taste/scripts/library.py validate --strict
python3 skills/my-report-taste/scripts/verify_deck_plan.py examples/synthetic-study/slide-plan.md
python3 skills/my-report-taste/scripts/check_speaker_script.py examples/synthetic-study/script-en.md --language en --paired examples/synthetic-study/script-zh.md --paired-language zh --minutes 3
```

讲稿工具输出 WARN 表示需要人工处理的提示，ERROR 表示结构或输入错误。零退出码只表示没有结构错误，不等于讲稿事实、翻译、时长或成品画面均通过。

`doctor.py` 默认只发现 Python、可选模块和 PATH 工具，不启动浏览器或 Office。需要确认当前项目能否解析 Artifact Tool 时，显式添加 `--probe-node --project-dir .`；这会执行一个最长 5 秒的 Node 内置探测，不导入该包。工具存在或模块可解析都不是导出、字体和视觉测试通过。

## 最小可运行制作路径

只需 Python 标准库，无 API key 或专有宿主依赖：

```bash
python3 examples/portable-report/build_report.py --out dist/portable-report
```

在浏览器打开输出的 `report.html`，或查看 `report.md`；输出目录存在时拒绝覆盖。[完整说明](../examples/portable-report/README.md)。这是独立阅读报告，不是 PPTX 构建器；示例文件位于源码仓库，不随 skill 安装器复制。

已有 PPTX 示例可直接下载并运行结构检查；原 gallery 生成链路仍需要宿主 Artifact Tool，其完整发布后处理尚未移植。没有该宿主时，内容计划、讲稿检查和本节报告生成仍可使用，不宣称能原样重建九张 PPT 预览。

## 已知边界

路由文本只检索候选；显式选择通过 `--preset / --card`，模板状态通过 `--template-state` 声明。代理仍负责理解否定、比较和输入文件，脚本不替用户决定。旧调用迁移见 [routing.md](../skills/my-report-taste/references/routing.md)。讲稿计数对数字、缩写和数学读法仅作近似。PPTX 文本与备注存在不证明没有遮挡，PDF 字体检查通过不证明投影可读。

首次发行的实际验证范围见 [发布验证](release-verification.md)。没有测过的平台或渲染器不会标为支持已验证。
