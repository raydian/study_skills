# Style References Index — 公共库参考图索引（library scope）
schema: reference_index
scope: library
version: "1.0.0"

# 每个 Core Style 需 3–6 张 canonical references，覆盖 portrait / still_life / environment
# （推荐增加 architecture / complex_scene / abstract）
# 参考图元数据模板见 schemas/reference.schema.yaml

# 目录约定：
# references/styles/<STYLE_ID>/REF_<STYLE_ID>_<NN>.<ext>
# 每目录放 references.yaml 索引，示例：

example:
  style_id: IL03
  style_version: 1.2.0
  refs:
    - id: REF_IL03_01
      role: overall_style
      subject: still_life
      source: ""
      license: ""
      approved: false
    - id: REF_IL03_02
      role: overall_style
      subject: environment
      source: ""
      license: ""
      approved: false
    - id: REF_IL03_03
      role: overall_style
      subject: portrait
      source: ""
      license: ""
      approved: false

# 生成方法：用该 Style 的 benchmark 5 类场景生成候选（见 evaluation/benchmarks/benchmarks.yaml），
# 从中挑选最能代表视觉语言的 3 张；overall_style 优先取 still_life + environment，避免人物过强。
# 采集与人工审阅后标记 approved=true 方可正式使用。
