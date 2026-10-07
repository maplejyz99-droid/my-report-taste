# 内容任务与呈现选择

关键词只检索候选，不替用户作决定。代理结合当前请求、已有大纲、实际模板和 [taste-profile.md](taste-profile.md) 确定适用项，再声明选择；不要求用户学习命令或重复确认已有偏好。

## 独立选择

- `--content explain|progress|compare`：只选内容任务，规则见 [content-modes.md](content-modes.md)。不选配色，不强设推荐立场。
- `--visual <预设 ID>`：只借用该组合的呈现规则；不加载叙事卡和专业内容工作流，不改变内容任务或输出媒介。布局卡内来源章节／内容顺序不生效。
- `--preset <预设 ID>`：明确选完整参考组合，包括其叙事／证据／外观。仍按材料和当前任务取舍，不恢复固定页型配额。
- `--card <卡片 ID>`：仅选指定维度，可重复；`NAR-001` 单选不带 `GRD-010 / CLR-010`。
- `--content` 可与一种呈现选择组合；`--visual / --preset / --card` 三者互斥。
- `--template-state provided|absent|unknown`：实际模板状态，默认 unknown。`--template` 是 provided 简写；与状态参数互斥。提供模板时抑制冲突配色及其 gate，保留兼容规则。文本提到“官方模板”不证明文件已提供。

示例：

```bash
python3 scripts/library.py route "学术 Oral，暂未选外观" --json
python3 scripts/library.py route --content explain --template
python3 scripts/library.py route --content progress --visual author-light --template-state absent
python3 scripts/library.py route --content compare --visual technical-review-dark --template-state absent
python3 scripts/library.py route --card NAR-001 --template
python3 scripts/library.py route --preset academic-oral-wine --template-state absent
```

未声明选择时，候选的 main、auxiliary、palette、contracts、references 和 gate_refs 不激活；建议配置只在 _candidate_config。已声明的内容与呈现分别输出，不因更换外观重推内容任务。单选内容不关闭当前使用者已确认的偏好：代理可以另行采用本地档案中的外观，但公开版不预先确认任何颜色，也不得让颜色决定叙事。

## 九种兼容预设

- `author-light`（别名 `research-progress-light`）：明亮蓝与浅色编辑式页面。
- `academic-oral-wine`：酒红学术呈现；完整组合额外包含 `NAR-001`。
- `experiment-review`：大幅工程证据与数据标注。
- `technical-review-light`：浅色技术关系表达。
- `technical-review-dark`：深色聚焦与连续比较表。
- `project-green`：白色内容中心、绿色导航与重点。
- `project-summary-dual-semantics`：主证据与确有需要的第二语义。
- `neutral-evidence-review`：无彩系统与真实素材。
- `dense-reading-report`：独立阅读型密度；不是颜色方案。远距投影任务不要借此启用阅读报告字号，输出格式仍由任务决定。

既有九个预设 ID 保留。旧内容 ID `academic-paper-oral` 兼容映射到 explain，`research-content` 映射到 progress；它们不是新增的第四、第五类任务。论文专业工作流按源材料另行加载。

早期的 `route "研究进展"` 会直接返回蓝色配置，现在只返回候选；已确定任务的调用应使用显式参数。`NAR-001` 是叙事卡而非整套酒红的别名；完整复用用 --preset，只改外观用 --visual。候选排序与参数声明不是授权记录，仍须核对用户原话。
