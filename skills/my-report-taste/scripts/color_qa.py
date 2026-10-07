#!/usr/bin/env python3
"""Diagnose significant page hues with material-aware or strict UI policies."""

from __future__ import annotations

import argparse
import colorsys
import fnmatch
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - depends on the caller environment
    raise SystemExit(
        "Pillow is required for color_qa.py. Install it with: python3 -m pip install Pillow"
    ) from exc


POLICIES = {"strict-ui", "material-aware"}
Mask = tuple[float, float, float, float]


@dataclass
class AuditResult:
    path: str
    policy: str
    status: str
    considered_pixels: int
    saturated_share: float
    significant_hues: list[dict[str, float | int]]
    masks: list[list[float]]
    message: str


def parse_mask(raw: str) -> Mask:
    try:
        values = tuple(float(value.strip()) for value in raw.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("mask must be x,y,width,height using numbers in [0,1]") from exc
    if len(values) != 4:
        raise argparse.ArgumentTypeError("mask must contain exactly four values: x,y,width,height")
    x, y, width, height = values
    if min(values) < 0 or max(values) > 1 or width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("mask values must be in [0,1] and width/height must be positive")
    if x + width > 1 or y + height > 1:
        raise argparse.ArgumentTypeError("mask rectangle must stay inside the normalized page")
    return x, y, width, height


def load_policy_rules(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Policy file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in policy file {path}: {exc}")
    rules = data.get("rules") if isinstance(data, dict) else None
    if not isinstance(rules, list):
        raise SystemExit("Policy file must contain a 'rules' list")
    output = []
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict) or not isinstance(rule.get("pattern"), str):
            raise SystemExit(f"rules[{index}] must contain a string 'pattern'")
        policy = rule.get("policy")
        if policy is not None and policy not in POLICIES:
            raise SystemExit(f"rules[{index}].policy must be strict-ui or material-aware")
        masks = rule.get("masks", [])
        if not isinstance(masks, list):
            raise SystemExit(f"rules[{index}].masks must be a list")
        parsed_masks: list[Mask] = []
        for mask_index, mask in enumerate(masks):
            if isinstance(mask, str):
                parsed_masks.append(parse_mask(mask))
            elif isinstance(mask, list) and len(mask) == 4:
                parsed_masks.append(parse_mask(",".join(str(item) for item in mask)))
            else:
                raise SystemExit(f"rules[{index}].masks[{mask_index}] must contain four numbers")
        output.append({"pattern": rule["pattern"], "policy": policy, "masks": parsed_masks})
    return output


def resolve_page_policy(
    path: Path,
    default_policy: str,
    global_masks: list[Mask],
    rules: list[dict[str, Any]],
) -> tuple[str, list[Mask]]:
    policy = default_policy
    masks = list(global_masks)
    candidates = (path.name, path.as_posix())
    for rule in rules:
        if any(fnmatch.fnmatch(candidate, rule["pattern"]) for candidate in candidates):
            if rule.get("policy"):
                policy = str(rule["policy"])
            masks.extend(rule.get("masks", []))
    return policy, masks


def masked(x: int, y: int, width: int, height: int, masks: list[Mask]) -> bool:
    x_norm = (x + 0.5) / width
    y_norm = (y + 0.5) / height
    return any(
        left <= x_norm < left + mask_width and top <= y_norm < top + mask_height
        for left, top, mask_width, mask_height in masks
    )


def audit(
    path: Path,
    *,
    policy: str,
    masks: list[Mask],
    bin_width: int,
    significant_share: float,
    max_significant_hues: int,
    saturation_floor: float,
    value_floor: float,
) -> AuditResult:
    if not path.is_file():
        raise FileNotFoundError(path)
    with Image.open(path) as source:
        image = source.convert("RGB")
    image.thumbnail((720, 720))
    hue_bins: dict[int, int] = {}
    saturated = 0
    considered = 0

    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            if masked(x, y, image.width, image.height, masks):
                continue
            considered += 1
            r, g, b = pixels[x, y]
            hue, saturation, value = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if saturation < saturation_floor or value < value_floor:
                continue
            saturated += 1
            key = int((hue * 360) // bin_width) * bin_width
            hue_bins[key] = hue_bins.get(key, 0) + 1

    if considered == 0:
        raise ValueError("all pixels were excluded by masks")
    significant = [
        {"start": key, "end": min(key + bin_width, 360), "share": count / considered * 100}
        for key, count in hue_bins.items()
        if count / considered * 100 >= significant_share
    ]
    significant.sort(key=lambda row: float(row["share"]), reverse=True)
    too_many = len(significant) > max_significant_hues
    if too_many and policy == "strict-ui":
        status = "FAIL"
        message = f"strict UI page has {len(significant)} significant hue families"
    elif too_many:
        status = "WARNING"
        message = "material-aware page exceeds the hue heuristic; inspect evidence colors manually"
    else:
        status = "OK"
        message = "hue heuristic is within the configured budget"
    return AuditResult(
        path=str(path),
        policy=policy,
        status=status,
        considered_pixels=considered,
        saturated_share=saturated / considered * 100,
        significant_hues=significant,
        masks=[list(mask) for mask in masks],
        message=message,
    )


def print_result(result: AuditResult) -> None:
    hues = ", ".join(
        f"H{int(row['start']):03d}-{int(row['end']):03d}:{float(row['share']):.2f}%"
        for row in result.significant_hues
    )
    suffix = f" {hues}" if hues else ""
    print(
        f"{result.status} | {result.policy} | {result.path} | "
        f"saturated={result.saturated_share:.2f}% | "
        f"significant_hues={len(result.significant_hues)} | {result.message}{suffix}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument("--policy", choices=sorted(POLICIES), default="material-aware")
    parser.add_argument("--policy-file", type=Path)
    parser.add_argument(
        "--mask",
        action="append",
        type=parse_mask,
        default=[],
        metavar="X,Y,W,H",
        help="Exclude a normalized page rectangle; may be repeated",
    )
    parser.add_argument("--bin-width", type=int, default=45)
    parser.add_argument("--significant-share", type=float, default=0.75)
    parser.add_argument("--max-significant-hues", type=int, default=2)
    parser.add_argument("--saturation-floor", type=float, default=0.34)
    parser.add_argument("--value-floor", type=float, default=0.18)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    if not 1 <= args.bin_width <= 180:
        parser.error("--bin-width must be between 1 and 180")
    if not 0 <= args.significant_share <= 100:
        parser.error("--significant-share must be between 0 and 100")
    if args.max_significant_hues < 0:
        parser.error("--max-significant-hues must be non-negative")
    if not 0 <= args.saturation_floor <= 1 or not 0 <= args.value_floor <= 1:
        parser.error("saturation and value floors must be between 0 and 1")

    rules = load_policy_rules(args.policy_file)
    results: list[AuditResult] = []
    errors: list[str] = []
    for path in args.images:
        policy, masks = resolve_page_policy(path, args.policy, args.mask, rules)
        try:
            results.append(
                audit(
                    path,
                    policy=policy,
                    masks=masks,
                    bin_width=args.bin_width,
                    significant_share=args.significant_share,
                    max_significant_hues=args.max_significant_hues,
                    saturation_floor=args.saturation_floor,
                    value_floor=args.value_floor,
                )
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            errors.append(f"{path}: {exc}")

    if args.as_json:
        print(
            json.dumps(
                {"results": [asdict(result) for result in results], "errors": errors},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for result in results:
            print_result(result)
        for error in errors:
            print(f"ERROR | {error}", file=sys.stderr)

    failed = bool(errors) or any(result.status == "FAIL" for result in results)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
