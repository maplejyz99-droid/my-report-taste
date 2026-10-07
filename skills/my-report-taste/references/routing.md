# 候选检索与明确选择

`route` 不解析完整用户意图，也不从提到“官方模板”推断已经有模板。由代理结合当前指令、提供的文件和已确认偏好确定状态，再交给脚本校验。无需让用户重复确认清楚的指令。

## 仅检索

```bash
python3 scripts/library.py route "比较 author-light 和 academic-oral-wine，暂时不选择" --json
```

视觉结果标为 `_selection: candidate`：`main / auxiliary / palette / contracts / references / gate_refs` 均不激活，建议配置只在 `_candidate_config` 中。工作流标为 `workflow-candidate`，不选颜色。关键词匹配和有限否定处理只改善候选排序，不构成使用授权；即使输入“使用 author-light”，仍只返回候选。

## 声明已经确定的状态

```bash
python3 scripts/library.py route "研究进展" --preset author-light --template-state absent
python3 scripts/library.py route "学术 Oral" --preset academic-oral-wine --template
python3 scripts/library.py route "学术 Oral" --card NAR-001 --card GRD-010 --template
```

- `--preset` 选择整套预设；`author-light` 是 `research-progress-light` 的公开别名。
- `--card` 可重复，只选择这些卡。`NAR-001` 不再作为酒红整套预设的命令别名；单独选择它不加入 GRD 或 CLR 卡。需要完整组合时用 `--preset academic-oral-wine`。
- `--preset` 和 `--card` 互斥，未知 ID 报错。字段是调用者声明，不是脚本替用户作出的决定，也不是授权记录。
- `--template-state` 接受 `provided / absent / unknown`，默认 `unknown`。`--template` 是 `provided` 的简写，二者互斥。只有明确提供的状态影响配色；关键词不改变状态。
- `provided` 保留既有模板并抑制所选配色卡及其 gate；叙事、证据与兼容密度仍可使用。`absent` 表示确定没有模板；`unknown` 表示未确定，不能写成“已核验无模板”。

不要把自由文本含混之处随意填入参数。若用户只比较、不选择，不传选择参数；若用户仅选叙事，不把整套预设传入脚本。当前用户请求与参数冲突时先纠正参数，不能拿脚本输出覆盖用户原话。

## 从早期版本迁移

以前 `route "author-light"` 会直接返回带配色的路线。现在它返回不激活的候选；已经确认选择的自动化调用应改为 `route --preset author-light`。以前自然语言中的“官方模板”会抑制配色，现在应在检查输入后显式传 `--template`。JSON 仍为列表，新增 `_selection` 和 `_template_state`；候选配置移入 `_candidate_config`。不要把列表第一项默认为用户选择。
