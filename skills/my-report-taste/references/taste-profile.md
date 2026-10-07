# 当前使用者的偏好入口

公开版初始状态：没有替当前使用者确认任何颜色、字体、密度或叙事预设。

优先级：当前任务与官方模板 → 项目 `.report-taste/profile.md` → skill 内 `references/local-profile.md` → 明确选择的作者预设。检查项目文件时仅限当前项目，不扫描其他项目或用户目录。

只有明确“收藏／记住／更新偏好”的请求才写入长期设置。临时选色只影响当前成品。把来源事实、用户确认、合理推断和未知项分开记录。

本库卡片的状态字段属于作者示例记录，不能视为使用者的选择。内容按 explain／progress／compare 三类任务取舍，九个预设不各自创建一条内容路线。路由文本检索只返回候选；核对后用 `--content` 选内容、`--visual author-light` 仅借呈现、`--preset author-light` 启用完整组合，或 `--card NAR-001` 只启用叙事卡。选择配色后仍以官方模板为先。参数边界见 [routing.md](routing.md)。

可选组合见 [author-presets.md](author-presets.md)。本地偏好文件可使用下面的结构，按实际需要填写，不必一次回答所有项目：

```markdown
# My presentation preferences
## Confirmed
- 场景与受众：
- 证据与密度：
- 字体与颜色：
## Avoid
## Context-specific choices
## Unknown / still trying
```

公开仓库忽略本地偏好文件；不要把私人反馈或未公开结果提交为通用示例。示例配方不是普适的美学规则，使用者可以接受、修改或完全不采用。
