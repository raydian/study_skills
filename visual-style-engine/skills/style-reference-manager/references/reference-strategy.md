# 参考图策略

## 角色分配

| 角色 | 用途 | 数量建议 |
|---|---|---|
| overall_style | 整体风格锚定（喂给支持参考图的模型） | 3–6 / Style |
| line | 线条语言参考 | 1–2 |
| palette | 色板参考 | 1 |
| texture | 纹理参考 | 1 |
| composition | 构图参考 | 1–2 |
| character | 人物渲染参考 | 按需（character projects） |

## 参考图生成（无现成素材时）

用该 Style 的 benchmark 5 类场景生成候选：
1. portrait
2. still_life
3. environment
4. nature
5. complex_scene

从中挑出"最能代表视觉语言"的 3 张作为 canonical references（overall_style 优先取 still_life + environment，避免人物过强）。

## 校验清单（逐张）

- [ ] subject 类型明确（不混）
- [ ] 不依赖特定角色/商标/品牌
- [ ] 无 photorealistic 特征（当 Style 非摄影类时）
- [ ] 色彩符合 Style color_system（而非单一 Preset）
- [ ] 与 confusion 高风险 Style 有明显差异
- [ ] license 明确（生产可用）

## 存放规则

```text
references/
├── styles/       # 公共库参考（按 style_id 组织，library scope）
│   └── IL03/
│       ├── REF_IL03_01.png
│       └── references.yaml
└── projects/     # 项目参考（project scope）
    └── sapiens/
        ├── REF_PROJECT_01.png
        └── references.yaml
```

## 常见错误

- 用一张人物图当整体风格参考（角色 Identity 过强 → 生成结果跟着人物漂）；
- 参考图风格混杂（把两种 Style 的图放在同一角色）；
- 未 approved 的图进入正式生成。
