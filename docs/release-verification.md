# v0.1.0 发布验证

日期：2026-10-07。本记录区分已经观察的结果与尚未测试的平台。

## 已观察的结果

- Skill 基础校验通过：名称、frontmatter 和入口格式有效。
- 库严格校验通过：35 张卡片、11 条路线、31 个检查标记、0 个原始参考资产，无警告。
- 原有 45 项单元测试通过，覆盖路由、计划比对、讲稿结构与计时边界。
- 9 项发行测试通过，覆盖隔离安装、拒绝覆盖、旧安装保护、私人文件排除、符号链接拒绝、扫描提示脱敏、重复打包一致性及合成表格与 JSON 一致性。
- 最终 PPTX 与计划比对通过：5 页、标题、页 ID 和 main／backup 角色一致，0 个警告。
- 89 个分发文件通过必备文件、相对 Markdown 链接、有限隐私模式与 PPTX XML 扫描。该数字不包括缓存、私人偏好、构建临时文件或 Git 历史。
- ZIP 解包后在临时目录实际安装成功，已安装副本的严格库校验通过；未触及现有个人库。
- GitHub 首次内容提交的 [自动检查](https://github.com/maplejyz99-droid/my-report-taste/actions/runs/37598645717) 已通过，运行环境为 Ubuntu、Python 3.10。它覆盖机械检查，不扩展为 Office 或视觉兼容性声明。
- 公开仓库首次内容提交的 89 个文件与本地分发清单逐一比较 Git blob 指纹，一致，无多余文件。
- 合成示例的 PPTX 结构与全部 5 页渲染已检查，详情见 [示例核验](../examples/synthetic-study/verification.md)。

## 发行前复核命令

在仓库根目录运行；命令输出才是当前目录的实际结果：

```bash
python3 skills/my-report-taste/scripts/library.py validate --strict
python3 -m unittest discover -s skills/my-report-taste/tests -p 'test_*.py'
python3 -m unittest discover -s tests -p 'test_*.py'
python3 skills/my-report-taste/scripts/verify_deck_plan.py examples/synthetic-study/slide-plan.md examples/synthetic-study/demo.pptx
python3 skills/my-report-taste/scripts/check_speaker_script.py examples/synthetic-study/script-en.md --language en --paired examples/synthetic-study/script-zh.md --paired-language zh --minutes 3
python3 tools/check_public_release.py
python3 tools/package_release.py
```

## 验证边界

本机运行环境为 macOS、Python 3.13；上述 CI 运行了 Ubuntu、Python 3.10 的机械检查。没有将 Windows、所有 Office 版本或其他代理产品标为兼容性已验证。GitHub Actions 不证明视觉品质、科学正确性或真人讲述效果。

公开包仅包含工作流、抽象文字模式卡、代码、文档和原创合成示例。没有复制原始参考 PPT/PDF、品牌图片、字体文件、私人反馈、聊天记录或原工作区 Git 历史。

隐私工具只检查有限模式、打包白名单、相对链接及 PPTX XML，不是完整秘密扫描、版权审计或任意二进制元数据审计。它不会声称任何文件在任何情况下都可以安全发布。外部来源链接的在线可达性未逐个重验。

安装脚本不会覆盖已有同名 skill，也不会替换个人收藏。测试中的安装目标为临时隔离目录，不是作者正在使用的 skill。
