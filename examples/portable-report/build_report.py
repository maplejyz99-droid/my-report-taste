#!/usr/bin/env python3
"""Build an offline reading report with Python 3.10+ only; not a PPTX renderer."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from pathlib import Path

DEFAULT_SOURCE = Path(__file__).resolve().parents[1] / "synthetic-study/source.json"


def load_source(path: Path) -> tuple[dict, bytes]:
    if path.stat().st_size > 128 * 1024:
        raise ValueError("Source exceeds 128 KiB")
    raw = path.read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("synthetic") is not True:
        raise ValueError("This demonstration accepts synthetic fixtures only")
    rows = data.get("rows")
    if not isinstance(rows, list) or len(rows) != 3:
        raise ValueError("Exactly three fixture settings are required")
    if data.get("metrics") != {"accuracy": "percent", "latency": "milliseconds per query"}:
        raise ValueError("Unsupported metric units")
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("name"), str) or not row["name"]:
            raise ValueError("Each row needs a setting name")
        for key in ("accuracy", "latency"):
            value = row.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("Metrics must be finite numbers")
        if not 0 <= row["accuracy"] <= 100 or row["latency"] <= 0:
            raise ValueError("Accuracy must be 0–100%; latency must be positive")
    for key in ("id", "question", "warning", "exclusions"):
        if not isinstance(data.get(key), str) or not data[key]:
            raise ValueError(f"Missing source string: {key}")
    for key in ("method", "unmeasured"):
        if not isinstance(data.get(key), list) or not data[key] or not all(isinstance(v, str) for v in data[key]):
            raise ValueError(f"Missing source list: {key}")
    return data, raw


def md_escape(value: str) -> str:
    return html.escape(value).replace("|", "\\|").replace("\n", " ").replace("`", "\\`")


def build(source: Path, out: Path) -> dict:
    data, raw = load_source(source)
    baseline, compact, large = data["rows"]
    delta = compact["accuracy"] - baseline["accuracy"]
    saved = baseline["latency"] - compact["latency"]
    relative = saved / baseline["latency"] * 100
    tradeoff = large["latency"] - compact["latency"]
    gain = large["accuracy"] - compact["accuracy"]
    source_hash = hashlib.sha256(raw).hexdigest()
    summary = (f'{compact["name"]} 与 {baseline["name"]} 相比，准确率变化 {delta:+.1f} 个百分点；'
               f'每次查询延迟变化 {-saved:+g} ms（相对变化 {-relative:+.1f}%）。')
    comparison = (f'{large["name"]} 与 {compact["name"]} 相比，准确率变化 {gain:+.1f} 个百分点，'
                  f'延迟变化 {tradeoff:+g} ms。')
    rows_md = '\n'.join(f'| {md_escape(r["name"])} | {r["accuracy"]:.1f} | {r["latency"]:g} |' for r in data["rows"])
    rows_html = '\n'.join(f'<tr><th scope="row">{html.escape(r["name"])}</th><td>{r["accuracy"]:.1f}</td><td>{r["latency"]:g}</td></tr>' for r in data["rows"])
    scope_md = '\n'.join(f'- {md_escape(v)}' for v in data["unmeasured"])
    scope_html = ''.join(f'<li>{html.escape(v)}</li>' for v in data["unmeasured"])
    markdown = f'''# 候选筛选的准确率与延迟

教学合成数据；不代表真实实验。{md_escape(data["warning"])}

## 研究问题

{md_escape(data["question"])}

## 完整对照

| 设置 | 准确率（%） | 延迟（ms/query） |
| --- | ---: | ---: |
{rows_md}

## 证据支持的比较

{md_escape(summary)}

{md_escape(comparison)}

准确率差以百分点计算；相对延迟差使用第一行设置的延迟为分母，二者不能混称为百分比提升。

## 方法位置

{' → '.join(md_escape(v) for v in data["method"])}

## 还没有测量

{scope_md}

{md_escape(data["exclusions"])}

来源：{md_escape(data["id"])}，随输出附 source.json。SHA-256：`{source_hash}`。
'''
    document = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>候选筛选的准确率与延迟</title><style>
*{{box-sizing:border-box}} body{{margin:0;background:#fff;color:#242c36;font-family:Arial,"Microsoft YaHei",sans-serif;line-height:1.65}}
main{{max-width:960px;margin:0 auto;padding:48px 32px}} header{{border-bottom:2px solid #24618c;padding-bottom:22px}}
h1{{font-size:32px;line-height:1.25;margin:8px 0 20px}} h2{{font-size:22px;margin:32px 0 12px}}
p,li,td,th{{font-size:18px}} .label{{color:#24618c;font-size:14px;font-weight:bold}} .note{{font-size:15px;color:#586573}}
table{{border-collapse:collapse;width:100%;table-layout:fixed}} th,td{{padding:12px 8px;border-bottom:1px solid #d7dee5;text-align:right;overflow-wrap:anywhere}}
th:first-child{{text-align:left;width:46%}} thead{{background:#eff4f8}} footer{{border-top:1px solid #d7dee5;margin-top:32px;padding-top:16px;overflow-wrap:anywhere}}
@media(max-width:600px){{main{{padding:24px 16px}}h1{{font-size:28px}}td,th{{font-size:15px;padding:8px 4px}}}}
@media print{{main{{padding:0;max-width:none}}h2{{break-after:avoid}}table{{break-inside:avoid}}}}
</style></head><body><main>
<header><div class="label">研究证据示例 · SYNTHETIC TEACHING DATA</div><h1>候选筛选的准确率与延迟</h1>
<p>教学合成数据，不代表真实实验。</p><p class="note">{html.escape(data["warning"])}</p></header>
<h2>研究问题</h2><p>{html.escape(data["question"])}</p>
<h2>完整对照</h2><table><thead><tr><th scope="col">设置</th><th scope="col">准确率（%）</th><th scope="col">延迟（ms/query）</th></tr></thead><tbody>{rows_html}</tbody></table>
<h2>证据支持的比较</h2><p>{html.escape(summary)}</p><p>{html.escape(comparison)}</p>
<p class="note">准确率差以百分点计算；相对延迟差使用第一行设置的延迟为分母，二者不能混称为百分比提升。</p>
<h2>方法位置</h2><p>{' → '.join(html.escape(v) for v in data["method"])}</p>
<h2>还没有测量</h2><ul>{scope_html}</ul><p class="note">{html.escape(data["exclusions"])}</p>
<footer class="note">来源：{html.escape(data["id"])}，随输出附 source.json。<br>SHA-256：{source_hash}</footer>
</main></body></html>'''
    # Validate all inputs before creating a new output directory; never overwrite.
    out.mkdir(parents=True, exist_ok=False)
    (out / "source.json").write_bytes(raw)
    (out / "report.md").write_text(markdown, encoding="utf-8")
    (out / "report.html").write_text(document, encoding="utf-8")
    return {"outputs": ["report.md", "report.html", "source.json"], "source_sha256": source_hash,
            "rendered": False, "skill_effectiveness_tested": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build(args.source, args.out)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Build failed: {exc}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
