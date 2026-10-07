# 可选作者预设

这些组合展示如何将叙事、证据密度与视觉分别组织。只有用户明确选择时启用，不替代官方模板，不声明来源方背书或资产授权。原始参考文件、个人原话及量化审阅日志不随公开版分发。

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

确认选择后使用 `route --preset <预设 ID>`；仅选某一维度使用 `route --card <卡片 ID>`，可以重复 `--card`。自由文本命中不启用整套。模板状态与迁移方式见 [routing.md](routing.md)。
