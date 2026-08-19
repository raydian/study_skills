# Evaluator 评分细则

## 8 维评分参照（对照 Style fingerprint 逐项）

| 维度 | 看什么 | 满分特征（以 VE01 为例） |
|---|---|---|
| shape | 形状语言 | 简化 silhouette、大面积有机色块、低几何复杂度 |
| line | 线条语言 | 平滑连续、线宽统一、数量少 |
| color | 色彩系统 | 3–7 色、色块边界清晰、大面积纯色 |
| shading | 阴影 | flat、0–15% 阴影强度、无复杂体积光 |
| lighting | 光照 | 不强调物理光源、浅/深色分层 |
| texture | 纹理 | 无纹理、至多极轻微 grain |
| composition | 构图 | 30–60% 留白、单一视觉中心、2–4 层级 |
| detail | 细节 | 2/10 低密度 |

## 评分锚点（每维 0–100 速判）

- 90+：与 fingerprint 描述完全吻合
- 80–89：吻合，个别可忽略偏差
- 65–79：出现该维度的风格外特征（如矢量图出现软渐变体积光）
- 0–64：该维度整体错误（如矢量图出现摄影景深）

## 常见漂移信号（baseline）

| 信号 | 判定 |
|---|---|
| 出现 PBR 材质 / 真实反射 | texture/lighting 分低 + 可能硬失败 |
| 出现景深虚化 | lighting 分低 |
| 出现摄影颗粒、真实皮肤毛孔 | 硬失败（photorealistic 漂移） |
| 构图变成海报式满铺、无留白 | composition 分低 |
| 色彩出现高饱和糖果色（原为 muted） | color 分低 |

## 项目一致性（PICS）

多图项目每张图计算与 Identity 的距离：
- 强锁定维度（shape/line/texture）偏差权重高；
- 半锁定维度（palette/composition）允许受限变化；
- PICS = 100 − 加权累计偏差；连续 20 张 ≥85 达标。

## 纠偏回环

```text
Evaluator (Correction)
   → 输出 problems + corrections
   → Compiler（调整 AST attributes 或重申强锁定）
   → Adapter（按模型重写）
   → Generator → Evaluator（再评）
```

限制：同一张图最多 3 次自动纠偏，仍失败则交人工评审并记录 retry_count。

## 观测数据（每次生成记录，第 46 节）

```yaml
request_id:
project_id:
style_id:
style_version:
preset_id:
adapter: {model, version}
compiled_prompt_hash:
reference_ids: []
generation_model:
evaluation_score:
corrections: []
retry_count:
```
