# 0.2.0 源码更新

本次更新 main 源码与 VERSION；不修改 v0.1.0 tag 或其 Release 附件，也不表示已经创建 v0.2.0 GitHub Release。

## 行为变化

- 文本路由返回不激活的候选；选择整套使用 `--preset`，按维度使用重复的 `--card`。
- 模板状态不再由关键词推断，用 `--template-state provided/absent/unknown`；保留 `--template` 简写。
- 单选 `NAR-001` 不捆绑密度、酒红配色或其他预设卡。
- 增加前后否定、改选、比较不选用、独立维度选择与 CLI 参数回归测试。

旧自动化不能再把第一条文本检索结果当成已选配置。详细迁移见 [routing.md](../skills/my-report-taste/references/routing.md)。明确参数仍由调用者核对，不能替用户授权。

## 新增与保留

- 只读 `doctor.py`：区分基础检查、工具发现与未验证的渲染能力，不自动安装依赖。
- Python 标准库生成中文 HTML／Markdown 阅读报告；不承诺重建现有九张 PPTX。
- README 先展示内容组织案例，再展示完整保留的九种风格。
- 四项合成材料任务级预检与评测协议；尚未执行代理 A/B，未声称减少返工或 token。
- 现有个人偏好、全部 PPTX/PNG 成品和旧发布验证记录不变。

[本轮验证及已知限制](validation-routing-portability.md)
