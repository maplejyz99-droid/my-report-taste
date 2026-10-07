# 0.3.0：内容任务与呈现独立选择

本次更新 main 源码与 VERSION 为 0.3.0，不改写旧版本 tag、Release 附件或发布记录。源码更新不等于创建了 v0.3.0 GitHub Release。

## 行为变化

- 内容任务收敛为 explain（研究／技术讲解）、progress（进展／结果汇报）、compare（方案比较／选择）。它们指导取舍，不是固定目录。
- 新增 `--content` 与 `--visual`；前者不选颜色或推荐立场，后者仅借呈现，不加载叙事卡或专业内容工作流，也不改变目标媒介。
- 保留九个预设 ID、`author-light` 别名、完整选择 `--preset` 与独立卡片 `--card`。旧内容名称 `academic-paper-oral`、`research-content` 可通过 `--content` 分别映射至 explain、progress。
- 自由文本返回未激活的候选，包括 workflow-candidate；建议配置保存在 `_candidate_config`。需要启用时由调用者根据真实请求显式声明，不能把第一项或参数本身当成用户授权。
- `--content` 可与一种呈现选择组合；`--visual / --preset / --card` 互斥。显式选择不因检索 limit 截断。
- 已提供的官方模板仍优先；其配色不被个人预设覆盖。

[接口与示例](../skills/my-report-taste/references/routing.md) · [三类内容任务](../skills/my-report-taste/references/content-modes.md)

## 内容编辑与文档

去除从参考稿迁移来的固定失败机制数量、章节总结配额、页型种数和必有未来工作页等要求。保留事实、证据、来源、重要条件和可读性检查。结果页可使用判断标题，定义／方法／设置页可以保留具体名称；同组比较不必每页变换布局。

中英文 README 说明三层关系：内容任务、证据与密度、视觉外观。九张预览保留，示例调用改为只借呈现；需要完整参考时仍可用 `--preset`。绿色预览中的里程碑、蓝沙金中的第二语义等，不再暗示新稿必须增加这些章节。

公开版仍不替新使用者确认偏好；私人资料、源素材和本地工作记录未迁入。现有 PNG／PPTX、原始示例数据、目录元数据、字体与安装防覆盖机制不因本次更新改变。

## 验证状态

以下为发布前的本地检查记录。2026-10-07，macOS / Python 3.13.5 实际运行：

- skill 单元测试：71 项通过，包含三类内容与九种呈现的组合不变性、旧 ID、单卡选择、模板优先及冲突参数。
- 分发与示例测试：22 项通过，包含临时安装后执行新版路由、拒绝覆盖个人库和 ZIP 可重复构建。
- 严格库校验：35 张卡片、12 条路由、31 个 gate、0 项外部分发资产，0 警告。
- skill 结构检查通过；分发检查覆盖 135 个选中文件、相对链接、白名单与有限隐私模式。它不是完整秘密扫描或版权审计。
- 原五页示例的内容计划与 PPTX 比对通过，0 警告；20 个已有 PNG／PPTX 等二进制文件哈希未变。
- 中英文讲稿检查无结构错误，但保留 S03、S05 的两条数字线索提示。人工核对两种语言的原数值、差值与单位一致；没有为消除提示改写旧示例，未进行真人试讲。
- 标准库 HTML／Markdown 示例构建成功；未渲染。目录、安装器、打包工具和 CI 配置保持不变。

单元测试与库校验不等于内容优秀、投影可读或“没有 AI 味”。本次不重新渲染旧预览，不把之前的视觉检查说成针对新版重新运行；上述本地记录也不代表已验证跨平台兼容。远程 CI 结果以对应提交的 [GitHub Actions 记录](https://github.com/maplejyz99-droid/my-report-taste/actions) 为准。

在仓库根目录可复核：

```bash
python3 skills/my-report-taste/scripts/library.py validate --strict
python3 -m unittest discover -s skills/my-report-taste/tests -p 'test_*.py'
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/check_public_release.py
python3 tools/package_release.py
```

公开的四项有／无 skill 任务对照仍未执行，状态见 [evaluation.md](evaluation.md)；本次路由与安装回归不是该 A/B 评测。
