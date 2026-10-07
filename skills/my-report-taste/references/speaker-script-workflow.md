# 逐页讲稿、双语对齐与主讲移交

用于用户要求讲稿、口述稿、中英文版本、快讲版或移交他人主讲的任务。遵守用户指定格式；不因写讲稿而重做 deck、重开完整论文研究或擅自写入 PPTX 备注。

## 1. 锁定实际版本

- 以当前交付 deck 的文件名、页序、标题和实际图表为准，不从过期大纲猜页面。可复用可信的 slide-plan；没有稳定 ID 时按当前页序建立 S01、S02 等对应关系。
- 开头记录 deck 文件名／版本、语言、目标时长是否含问答，以及主讲范围。源稿改页后只同步受影响页及必要转场。
- 分清 main、optional、backup；备份问答不计入主讲时长。选择 optional 后重新计算，并给跳过后的转场。
- 未能检查的源文件、最新用户改动或页面内容明确标为未核验；不冒称已与最终版一致。

## 2. 写可说出口的讲法

正文包含本页主张、读图／公式的顺序、关键证据及通往下一页的转场，不只是复述 bullet。信息取舍服从页内实际证据，不增补未经论文或作者支持的机制。

- 把口述正文与 Presenter notes 分开。后者放指图动作、提醒、来源、备用解释及待确认信息；“不要猜测”等内部指令不能混进对外讲稿。
- 图表操作提示必须与实际页面一致；未查看布局时不猜“右下角”或箭头方向。没有动画就不写“点击后出现”。
- 用自然的作者式语言介绍贡献，不反复插入泛化免责声明。影响结论的具体限制仍贴近相关主张，不能全部藏进问答。
- 公式先说对象、操作和作用，再解释必要变量；不要机械念每个符号。核对梯度、监督和信息流的区别，例如某个张量 stop-gradient 不代表共享网络全部冻结。
- “我们的工作”仅用于该论文作者方汇报；第三方论文讲解不要混淆归属。

## 3. 双语按页对齐，不逐字翻译

- 两份稿使用相同的页 ID、顺序和 main／optional／backup 分类。英文自然可讲，中文自然解释；术语必要时首次给中英对应。
- 逐页人工核对主张、比较对象、数据集、设置、数值、单位、提升口径和结论强度。absolute percentage points 与 relative percent 不可互换。
- 核查每页读图动作与转场是否一致；不得一份稿缺少反例，另一份却改变机制。
- 两种语言分别估时；不能复制英文秒数作为中文已验证时长。页码一致、数字一致都不能证明语义等价。

## 4. 按真实正文核算时长

计数仅包含实际口述的 Script／Answer 和 Transition；标题、来源、操作提示、备用问答不计入主讲。中文按汉字数估计，拉丁词另计；英文按词数估计。公式应写成实际口述解释，不能把 LaTeX 命令数当成说话词数。

数字、缩写和单位需按实际读法人工复核；机器分词可能把小数拆成多个词元，既不是实际英语词数，也不是中文逐字读数时长。重要数字较多时，写出口述读法或增加相应预算。

没有试讲数据时，可暂用英文 130–150 词／分钟、中文 200–260 字／分钟作为工作估值，另加指图、停顿、换页时间。它们不是会议规定或经验证的个人语速；技术解释密集时应下调语速或增加逐页预算。优先使用主讲人的真实试讲数据。

同时核对三个数：逐页预算之和、由正文估算的范围、整场目标时长。不能宣称“12 分钟”却给出 15 分钟正文或相互矛盾的逐页秒数。自动检查超时提示是编辑信号，不是强行加速演讲的依据。

需要快讲版时写出真正的 Short script 与 Short transition，删减次要细节并保持论证和跳页衔接。只写“这页快讲”不算短稿；缺失短稿仍按完整正文计时并提示。用于统计的 Markdown 可采用：

```markdown
# Oral script
Deck: talk-v2.pptx

## S01 — Research problem
- role: main
- target_seconds: 40

### Script
Actual spoken sentences, with the necessary explanation.

### Transition
The spoken transition to the next selected page.

### Short script
An actual shorter version, not an instruction to hurry.

### Short transition
A shorter spoken transition.

### Presenter notes
Actions, sources and internal reminders; not spoken.
```

`role` 为 main、optional 或 backup；backup 可用 `### Answer`。`target_seconds` 是该页当前完整讲法预算，不是自动测得的秒数。若已有不同格式，保持交付格式，可做临时规范化副本检查，不为工具重排用户文件。工具不读取 PPTX；版本与页面内容仍须实际核对。

```bash
python3 scripts/check_speaker_script.py script-en.md --language en --paired script-zh.md --paired-language zh --minutes 15
python3 scripts/check_speaker_script.py script-en.md --language en --short --minutes 10 --pause-seconds 4
```

工具检查页结构、所选正文计数、语言各自估时、预算与双语页序／角色／数字线索，输出 JSON。它不验证事实、术语、机制、翻译语义、投影布局或真人试讲。短版不与完整页预算比较，仍检查整体目标；选择 optional 后的跳页转场需人工复核。

## 5. 交付与验证边界

- 按要求分别交付中文、英文，注明对应 deck、主讲与备份范围，保留自然转场及必要的读图提示。
- 报告实际口述词／字数、假定语速、停顿假设与估计范围；不只报一个看似精确的分钟数。可沿用当前项目的 verification.md，不强制额外产生验收文档。
- 自动结构检查、逐页语义核对、实际试讲分别报告。未真人试讲或未在目标设备检查时明确未验证，不将“通读一遍”写成兼容与时长均通过。
- 无需交付问答时不额外制造 Q&A；已有未知问题且作者不要求回答时，不以此阻塞讲稿移交。
