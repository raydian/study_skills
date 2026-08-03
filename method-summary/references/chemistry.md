# 化学方法总结规范

## Output

```text
high_school/化学/方法总结/<方法名称>.md
```

## Required Structure

```markdown
# 方法名称

## 来源题目概览
## 题目形态归纳
## 方法分类归纳
## 适用场景
## 方法核心
## 操作步骤
## 判断依据
## 示例演示
## 常见变形
## 易错提醒
## 训练建议
## 速查清单
```

## Method Types

- 离子反应、离子共存、离子方程式书写。
- 氧化还原配平、电子转移、化合价判断。
- 物质推断、元素化合物转化。
- 化学实验设计、现象分析、误差分析。
- 物质的量、溶液浓度、化学计算。

## Requirements

- Classify input questions by problem form before summarizing methods.
- Classify input questions by solving method or analysis method, then summarize each reusable method.
- `题目形态归纳` should describe visible question forms such as material type, chart/diagram/table, experiment, calculation, proof, reading passage, multiple-choice, short-answer, essay, or comprehensive task.
- `方法分类归纳` should group questions by shared thinking path, not by source order.
- Explain "现象 -> 微观粒子 -> 方程式 -> 结论" when applicable.
- Use Markdown/LaTeX for equations.
- Include condition checks, conservation checks, and common traps.
- Examples should separate clue extraction, equation writing, and answer verification.
