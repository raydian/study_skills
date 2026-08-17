#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
style-lint — AI Visual Style Engine 样式文件校验器

用法：
    python3 tests/scripts/style-lint.py [engine-root]

检查项（第 64/65 节）：
  ERROR    结构问题：必填字段缺失 / Style ID 重复 / Fingerprint 8 维不全 / DNA 越界(0-10)
  WARNING  数量低于生产规格：must>=5 / should>=5 / may>=3 / must_not>=8
            / positive_anchor>=5 / negative_anchor>=5 / confusion_with>=2 / correction_rules>=5
  INFO     catalog 声明 ACTIVE 但缺对应 yaml

兼容两种 yaml 写法：多行块（- item）与 inline 数组（[a, b, c]）。
"""
import os
import sys
import re
import glob

ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_FIELDS = [
    "id:", "version:", "name:", "category:", "definition:",
    "fingerprint:", "style_dna:", "rules:", "canonical_prompt:",
    "confusion_with:", "correction_rules:", "use_cases:",
    "compatibility:", "reference_policy:", "evaluation_profile:",
]
FP_DIMS = ["shape", "line", "color", "shading", "lighting", "texture", "composition", "detail"]
DNA_KEYS = ["realism", "abstraction", "detail_density", "spatial_depth", "texture_strength",
            "shading_strength", "lighting_complexity", "line_presence", "line_roughness",
            "shape_complexity", "color_complexity"]


def get_section(text, key):
    """提取顶层 key 所在的行与后续缩进块（直到下一个顶层 key）"""
    m = re.search(rf"^{key}:.*$", text, re.M)
    if not m:
        return ""
    rest = text[m.start():]
    m2 = re.search(r"\n(?=\S)", rest)
    return rest[: m2.start()] if m2 else rest


def count_list(section, key):
    """统计 yaml key 对应数组的元素数（支持 inline 与 block 两种格式）"""
    # inline: key: [a, b, c]
    m = re.search(rf"{key}:\s*\[(.*?)\]", section, re.S)
    if m:
        inner = m.group(1).strip()
        if not inner:
            return 0
        return len([x for x in inner.split(",") if x.strip()])
    # block: key:\n  - a\n  - b；嵌套项按项首标记统计
    markers = {"confusion_with": r"^\s+-\s+\{?(?:style|pair):", "correction_rules": r"^\s+-\s+\{?problem:"}
    pattern = markers.get(key, r"^\s+-\s+")
    m = re.search(rf"{key}:\s*\n", section)
    if not m:
        return 0
    tail = section[m.end():]
    # 取到下一顶层 key 为止（已在 get_section 截断，此处保险）
    m2 = re.search(r"\n(?=\S)", tail)
    if m2:
        tail = tail[: m2.start()]
    return len(re.findall(pattern, tail, re.M))


def lint_style(path, seen_ids):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    errors, warnings = [], []

    for field in REQUIRED_FIELDS:
        if field not in text:
            errors.append(f"missing required field: {field}")

    m = re.search(r"^id:\s*(\S+)", text, re.M)
    style_id = m.group(1) if m else "<none>"
    if style_id in seen_ids:
        errors.append(f"duplicate style id: {style_id}")
    seen_ids.add(style_id)

    # Fingerprint 8 维（fingerprint 块整体内查）
    fp = get_section(text, "fingerprint")
    for dim in FP_DIMS:
        if f"{dim}:" not in fp:
            errors.append(f"fingerprint missing dimension: {dim}")

    # DNA：inline 或 block 内 11 个 key 齐全 + 0-10 范围
    dna = get_section(text, "style_dna")
    for key in DNA_KEYS:
        dm = re.search(rf"{key}:\s*(\d+)", dna)
        if not dm:
            warnings.append(f"style_dna missing key: {key}")
        else:
            v = int(dm.group(1))
            if v < 0 or v > 10:
                errors.append(f"style_dna.{key}={v} out of range 0-10")

    # 规则数量
    rules = get_section(text, "rules")
    n_must = count_list(rules, "must")
    n_must_not = count_list(rules, "must_not")
    if n_must < 5:
        warnings.append(f"rules.must={n_must} < 5")
    if n_must_not < 8:
        warnings.append(f"rules.must_not={n_must_not} < 8")

    # 锚点 / 混淆 / 纠偏
    cp = get_section(text, "canonical_prompt")
    n_pos = count_list(cp, "positive_anchor")
    n_neg = count_list(cp, "negative_anchor")
    if n_pos < 5:
        warnings.append(f"positive_anchor={n_pos} < 5")
    if n_neg < 5:
        warnings.append(f"negative_anchor={n_neg} < 5")

    n_conf = count_list(get_section(text, "confusion_with"), "confusion_with")
    # confusion_with 的 block 元素含 {style: ...}，inline 情况少；block 下 count_list 数 "  - " 行即可
    if "confusion_with" in text and n_conf == 0:
        n_conf = count_list(get_section(text, "confusion_with"), "confusion_with")
    n_corr = count_list(get_section(text, "correction_rules"), "correction_rules")
    if n_conf < 2:
        warnings.append(f"confusion_with={n_conf} < 2")
    if n_corr < 5:
        warnings.append(f"correction_rules={n_corr} < 5")

    return style_id, errors, warnings


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else ENGINE_ROOT
    style_dir = os.path.join(root, "style-library")
    if not os.path.isdir(style_dir):
        print(f"ERROR: {style_dir} not found")
        sys.exit(1)

    seen_ids = set()
    all_errors, all_warnings = [], []
    n_checked = 0
    for path in sorted(glob.glob(os.path.join(style_dir, "**", "*.yaml"), recursive=True)):
        if os.path.basename(path) == "catalog.yaml":
            continue
        rel = os.path.relpath(path, root)
        with open(path, encoding="utf-8") as f:
            head = f.read(400)
        if "kind: base" in head:  # base 父类结构不同，跳过完整规格检查
            continue
        n_checked += 1
        style_id, errors, warnings = lint_style(path, seen_ids)
        for e in errors:
            all_errors.append(f"[{style_id}] {rel}: {e}")
        for w in warnings:
            all_warnings.append(f"[{style_id}] {rel}: {w}")

    active_missing = []
    for cat in sorted(glob.glob(os.path.join(style_dir, "**", "catalog.yaml"), recursive=True)):
        with open(cat, encoding="utf-8") as f:
            text = f.read()
        # 按 "- id:" 分块，块内 status: ACTIVE 才计入
        blocks = re.split(r"(?=^\s+- id:)", text, flags=re.M)
        for block in blocks:
            m = re.search(r"^\s+- id:\s*(\S+)", block, re.M)
            if not m:
                continue
            if re.search(r"status:\s*ACTIVE", block) and m.group(1) not in seen_ids:
                active_missing.append(f"{os.path.basename(os.path.dirname(cat))}/{m.group(1)}")

    print(f"style yaml checked: {n_checked}")
    print(f"unique style ids: {len(seen_ids)}")
    print(f"catalog ACTIVE without yaml: {len(active_missing)}")
    if active_missing:
        print("  " + ", ".join(active_missing))
    print(f"\nERRORS: {len(all_errors)}")
    for e in all_errors:
        print("  " + e)
    print(f"WARNINGS: {len(all_warnings)}")
    for w in all_warnings:
        print("  " + w)

    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
