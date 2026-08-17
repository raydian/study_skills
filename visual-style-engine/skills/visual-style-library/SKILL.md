---
name: visual-style-library
description: Use when a visual style definition must be read, interpreted, compared, or used — looking up Style Spec / DNA / Fingerprint / rules by ID, resolving aliases, or checking confusion relationships between styles. The canonical data source for all style information.
agent_created: true
---

# Visual Style Library

标准视觉风格定义的**唯一数据源**。负责读取、解释、比较 Style Spec / DNA / Fingerprint / Rules。

## 触发条件

触发：

- 需要 Style 定义（Spec / DNA / Fingerprint / rules / anchors）；
- 通过 Style ID、别名或自然语言检索风格；
- 需要对比两个 Style（混淆关系、DNA 距离）；
- selector / compiler / evaluator 需要加载 Style 数据。

不触发：

- 生成最终 Prompt（那是 compiler + adapter 的职责）；
- 创建/修改 Style（那是人工 + Benchmark 流程）。

## 数据源

```text
style-library/
├── base/                      父类（VECTOR_BASE 等，定义继承基线）
├── <16 个分类>/
│   ├── catalog.yaml           分类内全部 Style 清单（ID/名称/一句话定义/状态）
│   └── <ID>.yaml              具体 Style 定义
```

## 查找流程

1. 规范化查询：Style ID（如 IL03）→ 直接定位；别名/中文名/自然语言 → 在 catalog 与 aliases 中匹配。
2. 读取 `style-library/<category>/<ID>.yaml`。
3. 解析继承：若有 `parent_style`，先加载父类，子 Style 只描述差异，合并后返回完整 Spec。
4. 返回所需切片（selector 要 DNA/compatibility，compiler 要 fingerprint/rules/anchors，evaluator 要 confusion/correction/evaluation_profile）。

## 关键规则

- **只读**：本 Skill 不修改任何 Style 文件。
- 状态过滤：selector 只推荐 ACTIVE（DRAFT/BENCHMARKING 不推荐）。
- 合并继承：子 Style 覆盖父类字段（数组字段 = 覆盖而非追加，除非父类用 `+` 前缀声明追加）。
- 版本化：读取时固定 version，供可复现性记录。
- 混淆检查：两个 Style 若 confusion_with 关系存在，比较时输出 risk 与 difference。

## 输出

```yaml
style: IL03
version: 1.2.0
status: ACTIVE
category: illustration
parent_style: null
summary: "..."
dna: {realism: 3, abstraction: 7, ...}       # 切片
fingerprint: {shape: [...], line: [...], ...} # 切片
rules: {must: [...], must_not: [...]}
confusion_with: [{style, risk, difference}]
```

## 质量自检

- [ ] 引用的 Style ID 存在且版本正确
- [ ] 继承合并正确（父类基线 + 子类差异）
- [ ] 未返回已废弃/非 ACTIVE 定义用于推荐
- [ ] 没有把 Attribute 文件误当 Style 返回
