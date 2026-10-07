# 可选作者预设

这些是九个便捷组合，不是九条内容路线。内容任务仅分研究／技术讲解、进展／结果汇报、方案比较／选择，见 [content-modes.md](content-modes.md)。组合中的布局、证据表达和颜色可以单独借用；当前用户请求与官方模板优先，不声明来源方背书或资产授权。原始参考文件、个人原话及量化审阅日志不随公开版分发。

- `author-light` / `research-progress-light`：明亮蓝、浅色内容页、明确证据层级；`GRD-002 + CLR-002`。
- `academic-oral-wine`：学术叙事与角色自适应密度；`NAR-001 + GRD-010 + CLR-010`。`NAR-001` 是其中的叙事卡，不是整套预设的选择别名；可单独采用与会议模板兼容的内容规则。
- `experiment-review`：大幅工程证据与直接数据标注；`GRD-005 + DAT-001 + DAT-004 + CLR-002`。
- `technical-review-light`：浅色技术结构；`GRD-002 + PRC-001 + CLR-002`。
- `technical-review-dark`：深色技术结构；`GRD-003 + CMP-001 + CLR-003`。
- `project-green`：白内容与鲜绿焦点；`GRD-006 + CLR-006`。
- `project-summary-dual-semantics`：主证据与第二语义分层；`GRD-007 + CLR-007`。
- `neutral-evidence-review`：系统退为中性，保留原始素材颜色；`GRD-008 + CLR-008`。
- `dense-reading-report`：适合独立阅读而非远距投影的综合证据页；`GRD-004 + OTH-003`。

卡片中的 negative／rejected 表示作者曾不采用该方向，不等于对所有使用者禁止。想研究这些反例可用 `search --include-rejected`，不将其自动混入正向制作。

仅借呈现使用 `route --visual <预设 ID>`，不加载叙事卡、专业内容工作流或预设输出媒介；来源章节与业务角色不成为必选目录。例如 project-green 不要求里程碑页，双语义配色不要求未来工作，dense-reading-report 不自动将 PPT 改成阅读报告。

明确选择完整参考时使用 `route --preset <预设 ID>`；仅选某一维度使用可重复的 `--card <卡片 ID>`。两者都以真实材料为准，不强凑章节或页型。可与 `--content explain|progress|compare` 组合；自由文本命中不启用整套。模板状态与迁移方式见 [routing.md](routing.md)。
