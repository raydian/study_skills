---
name: image-style-evaluator
description: Use when generated images must be checked for style consistency — scoring a result against the target style's fingerprint, DNA, and rules across 8 visual dimensions, and deciding PASS, CORRECT, or REGENERATE.
agent_created: true
---

# Image Style Evaluator

对生成结果做**维度级风格一致性评分**，不是"看起来差不多"，而是 8 维量化 + 判定 + 纠偏触发。

## 触发条件

触发：

- 已有生成结果，需要一致性 QA；
- 项目连续生成需要 PICS（项目一致性）评估；
- 自动链路中 evaluator 环节。

不触发：

- 还没有生成结果；
- 用户只想要文字评价风格理论。

## 输出（写入 visual_request.evaluation）

```yaml
style_score: 86

dimensions:
  shape: 91
  line: 88
  color: 82
  shading: 90
  lighting: 83
  texture: 79
  composition: 84
  detail: 87

decision: PASS          # PASS / CORRECT / REGENERATE

problems:
  - dimension: texture
    expected: 1
    actual: 7
    severity: high

corrections:
  - eliminate realistic material microtexture
  - return to flat color regions

project_identity_score: 92   # 项目级
```

## 评分体系

### 默认权重（可被 Profile 覆盖，如 DR07 提高 Line/Texture）

```text
Shape 20% | Line 15% | Color 15% | Shading 10% | Lighting 10% | Texture 10% | Composition 10% | Detail 10%
```

### 判定

```text
85–100  Strong Pass
80–84   Pass
65–79   Correction（走纠偏）
0–64    Regenerate
```

### 硬失败（直接 REGENERATE）

- 出现任一 MUST NOT 特征（violates_must_not）；
- 渲染方法错误（wrong_rendering_method，如矢量变摄影）。

## 决策流程

1. 加载 `evaluation/profiles/<style>_<variant>.yaml`（weights/thresholds/hard_fail/correction_map）。
2. 对照 Style fingerprint 8 维逐项评分（shape/line/color/shading/lighting/texture/composition/detail）。
3. 检查 MUST NOT 硬失败。
4. 加权总分 → 判定。
5. Correction 时查 correction_rules 输出纠正指令 → 交回 compiler/adapter 重生成。
6. 项目多图时计算 PICS（与 Identity 的偏差累积）。

## 纠偏（第 34 节）

```yaml
problems:
  - dimension: texture
    expected: 1
    actual: 7
    severity: high
```

Correction Engine 查 Style correction_rules：

```yaml
texture_too_realistic:
  instructions:
    - eliminate realistic material microtexture
    - return to flat color regions
    - remove photographic surface reflections
```

再进入 Compiler（不直接改 Style 定义）。

## 风格漂移检测

```text
Style Drift: IL03 → CI08   # 检测到漂向易混淆 Style
```

输出 correction：

```text
reduce photographic realism
restore conceptual editorial rendering
simplify physical lighting
strengthen symbolic illustration language
```

## 关键约束

- 只评分 + 触发纠偏，**不直接修改 Style**（Correction 改的是 Prompt 编译输入）；
- 评分须对照具体 Style 的 fingerprint/DNA，不凭感觉；
- 人工评审不可替代（Machine Score + Human Review，第 68 节）；
- 每次生成记录观测数据（request_id / style_id / adapter / score / corrections / retry_count，第 46 节）。

## 质量自检

- [ ] 8 维逐项评分有依据（对照 fingerprint）
- [ ] 硬失败优先于加权分判定
- [ ] Correction 输出有具体指令（非"请更像一点"）
- [ ] 项目场景输出了 PICS
