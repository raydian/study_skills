# 模型差异速查（Adapter 行为基线）

## 各模型 prompt_behavior / capabilities

| 属性 | Seedream | GPT Image | Flux | Midjourney | SDXL |
|---|---|---|---|---|---|
| natural_language | strong | strong | medium | medium | weak |
| keyword_density | medium | low | high | medium | high |
| long_prompt_tolerance | high | high | medium | medium | high |
| reference_image | ✓ 多图 | ✓ | 部分 | ✓ 强 | ✓ IP-Adapter |
| negative_prompt | medium | weak（文字排除） | weak | ✓ --no | ✓ strong |
| typography | medium | strong | weak | weak | weak |
| image_editing | ✓ | ✓ | 部分 | 部分 | 部分 |

## 编译规则差异示例

### Seedream
- 描述式句子：`A lone farmer standing in a vast geometric grid of farmland, overcast day`
- 风格锚点保持英文关键词句 + 中文场景描述均可
- 长 Prompt 可完整保留 Core + Support anchor

### GPT Image
- 全部自然语言，避免逗号堆叠
- 负向用句子表达：`Do not make it photorealistic, no depth of field, no 3D rendering`
- 复杂文字可胜任但后置排版更稳

### Flux
- 精简短语：`minimal vector illustration, flat 2D, smooth shapes, muted earth palette`
- 负向能力弱，靠正向描述锚定

### Midjourney
- 短语 + 参数：`minimal vector illustration of a farmer in a field --ar 16:9 --style raw --no photorealism, depth of field`
- 风格一致性可用 `--cref` / 参考图权重 `--iw`

### SDXL
- 正向短语 + 独立 negative prompt（强）
- 可挂 LoRA（如特定画风）与 quality tags：`masterpiece, best quality`

## Fallback 规则（第 54 节）

```yaml
requested: {complex_typography: true}
adapter: {support: weak}
fallback: {image_without_text: true, typography_postprocess: required}
```

模型能力弱时返回 fallback，不让模型硬生成。

## Adapter Lint 检查项（第 66 节）

- 是否删除 MUST？
- 是否引入 MUST NOT？
- 是否改变 Style 定义？
- 是否使用已废弃模型参数？
- 是否缺失 Style Lock？
