# 汇报品味收藏规范

## 来源类型

每条收藏选择一个 `kind`：

- `owned-artifact`：用户拥有或有权使用的 PPT、PDF、Markdown 或报告。
- `editable-template`：具有可编辑源文件且许可允许复用的模板。
- `web-reference`：网页中的公开汇报、案例、模板或交互演示。
- `external-artifact`：外部 PDF、PPT、论文附录、年报等完整文件。
- `image-reference`：截图、图片或静态设计稿。
- `video-reference`：视频、录屏、GIF 或动效参考。
- `generated-output`：由 Codex 或其他工具生成、经用户反馈的成品。

每条收藏声明一个或多个 `formats`：`md`、`pdf`、`ppt`、`pptx`、`keynote`、`html-deck`、`image`、`video` 或 `mixed`。

公开版说明：预置条目的状态属于 `author-example-not-user-preference`，只是示例作者的评价，不代表当前安装者确认。下述状态定义仅对明确要求建立的个人库生效；不要把预置条目自动迁移成新用户的偏好。

## 功能分类

`category` 说明将来复用的位置：

- `cover`：封面与开场。
- `agenda`：目录、路线图与议程。
- `section-divider`：章节分隔与转场。
- `key-message`：单一核心观点、引语或大数字。
- `data`：图表、指标、表格与数据注释。
- `comparison`：方案、实验、前后或竞品对比。
- `process`：流程、系统关系和依赖。
- `timeline`：时间线、里程碑与计划。
- `method`：研究方法、算法、架构与实验设置。
- `result`：发现、结果、证据与解释。
- `summary`：总结、决策与下一步。
- `appendix`：附录、引用和补充证据。
- `typography`：字体、字号与文字层级。
- `color`：色彩角色与强调方式。
- `grid`：网格、留白、对齐与版面骨架。
- `pagination`：分页、切片、页码与导航。
- `narrative`：跨页叙事结构与汇报节奏。
- `other`：暂时无法稳定归类的模式。

更细的行业、气质、机制和场景放入 `tags`，不要不断增加首层分类。

## 组件多维分类

制作页面地图时，除首要 `category` 外，再为每页记录六个规划维度。它们用于检索和组装，不新增为 `catalog.json` 必填字段；除页面职责外，其余维度写入 `tags`：

1. `page_role`：这页在叙事中做什么，例如封面、背景、问题、方法、结果、比较、总结、路线图或附录。对应 Slideland 的 `Page` 维度，也映射到本规范的首要 `category`。
2. `visual_form`：证据用什么形式表达。定量信息优先使用 `graph:*`，关系信息优先使用 `diagram:*`，例如 `graph:horizontal-bar`、`diagram:matrix`、`diagram:steps`、`diagram:formula`。
3. `asset_form`：是否需要照片、插画、截图、图标或地图底图，例如 `asset:photo`、`asset:ui-screenshot`。素材必须承担证据、识别或情境职责；没有职责时写 `asset:none`。
4. `style_facets`：页面采用什么视觉语言，例如 `color:blue`、`taste:clear`、`taste:trust`。颜色与气质是样式过滤器，不是内容组件。
5. `context_facets`：页面属于什么行业与材料类型，例如 `industry:ai`、`material:presentation`、`material:financial-results`。语境用于约束信息密度、术语、合规和证据，不直接决定版式。
6. `motion_form`：页面状态如何变化，例如 `motion:camera-zoom`、`motion:count-up`、`motion:path-draw`、`motion:orbit-expand` 或 `motion:none`。动效必须服务页面职责或视觉形式，并有可读的静态终态。

同一页必须先确定 `page_role`，再选择一个主要 `visual_form`；素材与动效都是辅助层，不能反向决定页面内容。完整操作规则见 `OTH-001`。

## 状态与偏好

状态 `status`：

- `candidate`：已记录但尚未确认。
- `approved`：用户明确要求收藏或确认喜欢。
- `validated`：在真实汇报中使用并获得确认。
- `rejected`：用户明确否定；保留反模式原因。
- `deprecated`：来源失效、许可变化或已被替代。

偏好 `preference`：

- `confirmed`：用户直接确认。
- `hypothesis`：由单一样例或策展推导，仍待确认。
- `negative`：用户明确不希望复用。

常见转换为 `candidate → approved → validated`。不得把自主策展的候选自动设为 `confirmed`。

## ID 前缀

优先使用：`COV`、`AGD`、`SEC`、`MSG`、`DAT`、`CMP`、`PRC`、`TML`、`MTH`、`RES`、`SUM`、`APP`、`TYP`、`CLR`、`GRD`、`PAG`、`NAR` 或 `OTH`。完整 ID 形如 `DAT-001`。

## 模式卡结构

每个 `references/<ID>.md` 使用以下结构：

```markdown
# <ID>：<标题>

## 元数据

- 类型：
- 分类：
- 状态：
- 偏好层级：
- 格式：
- 来源：
- 采集日期：
- 用户信号：
- 复用模式：
- 许可：

## 用户明确偏好

## 来源与定位

## 已验证事实

## 设计推断

## 内容与叙事规则

## 视觉与版式配方

## 媒介适配

## 反模式与边界

## 验收标准
```

没有证据的章节写“未知”，不得补造。页码、幻灯片号、截图区域、时间码或网页组件名称写入“来源与定位”。

### 稳定 Gate ID

被场景路由引用的验收条目在原有验收文字前增加稳定 ID，例如：

```markdown
- `gate:clr-010.wine-title-required` 随机抽取普通内容页时，上方主标题首先被感知为酒红。
```

- ID 使用 `<card-id 小写>.<语义 slug>`，同一 Skill 内全局唯一。
- 路由只保存 `gate_refs`，不得复制验收正文；正文仍以模式卡为唯一事实来源。
- 修改验收措辞不更换 gate ID；只有门禁含义发生实质变化时才新增 ID 并迁移引用。
- `library.py validate` 检查 gate ID 前缀、唯一性和路由悬空引用；正式晋级或提交前使用 `library.py validate --strict`，让 WARNING 也成为失败。

## catalog.json 字段

每个条目必须包含：

- `id`：大写前缀与三位流水号。
- `title`：简短、可搜索标题。
- `kind`：来源类型。
- `category`：首要功能分类。
- `status`：状态。
- `preference`：偏好层级。
- `source_url`：公开 URL；纯本地来源可为空字符串。
- `source_locator`：页码、幻灯片号、区域、时间码或组件定位。
- `collected_at`：`YYYY-MM-DD` 日期。
- `formats`：格式数组。
- `use_cases`：适用场景数组，例如“组会”“项目周报”“论文答辩”。
- `tags`：内容职责、视觉气质、行业和机制标签。
- `pattern_file`：模式卡相对路径。
- `asset_paths`：有权保存的资产相对路径。
- `reuse_mode`：`reuse-owned-asset`、`use-template-with-license`、`recreate-principles-only`、`visual-reference-only` 或 `adapt-generated-output`。
- `license`：包含 `name`、`source` 和 `policy`。

所有文件路径必须相对 Skill 根目录，禁止绝对路径和 `..` 路径穿越。

目录根级 `shared_assets` 用于登记不属于单一卡片的共享资产。每项包含相对 `path` 与非空 `purpose`；单卡资产仍放在该条目的 `asset_paths`。所有 `assets/` 文件必须被两者之一登记，否则 `validate` 判为孤儿资产。

## routes.json

`references/routes.json` 是已确认个人场景的机器可读路由，不替代模式卡。每条路线包含：

- `id`、`title`、`description`：稳定路由标识与简短用途。
- `priority`：同分时的确定性优先级；数值越大越靠前，不参与相关性分数。
- `triggers`、`use_cases`：用于自然语言召回的场景词。
- `type`：可选，默认 `visual`；`workflow` 只选择内容流程，不选择视觉卡。
- `requires_explicit`：可选布尔值；为 true 时，只在用户明确提及路线 ID、触发词或所选卡片 ID 时召回，不从宽泛用途推断用户已选风格。
- `main`：视觉路线选择一个主参考系统。
- `auxiliary`：最多两个辅助模式。
- `palette`：场景配色卡；没有固定配色时可为空。
- `contracts`、`references`：本路线必须读取的媒介契约与专项流程。
- `gate_refs`：模式卡中稳定 gate ID 的引用。

路由不得引用不存在、已拒绝或已废弃的正向卡片。规则正文只写在模式卡，路由只负责确定组合。

`workflow` 路线的 `main / auxiliary / palette / gate_refs` 必须为空，`references` 必须包含专项流程。普通“学术 Oral”属于工作流选择，明确指定学术酒红路线才叠加视觉组合。

`library.py route "<完整请求>" --template` 在有提供的模板时返回 `_visual_policy: preserve-provided-template`，清空本次输出的 palette 及其配色 gate，保留 `_configured_palette` 供追溯；不修改路由原定义。自动关键词识别只作辅助，不替代 agent 对否定、歧义、模板冲突和用户原话的判断。

## 许可与隐私

- 未知许可的网页、截图和外部文件使用 `recreate-principles-only` 或 `visual-reference-only`。
- 保存模板、字体、图标或代码前核验许可；保留来源与署名要求。
- 用户自己的敏感汇报可记录抽象模式，但未经明确要求不得把完整文件长期复制进 Skill。
- 入库前忽略账号信息、评论者身份、未公开实验结果和无关浏览内容。
