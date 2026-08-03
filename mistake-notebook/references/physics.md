# 物理错题本规范

## Output

```text
high_school/物理/错题本/<错题主题>.md
```

## Required Structure

```markdown
# 错题主题

## 错题概览
## 题目形态归纳
## 错因统计
## 易错知识点
## 错题列表
## 二次订正
## 复习提醒
```

## Single Mistake Structure

```markdown
### 错题 1

- 来源：
- 日期：
- 题目形态：
- 知识点：
- 错因类型：
- 掌握状态：

#### 原题
#### 我的错误答案或错误思路
#### 正确解法
#### 错因分析
#### 防错提醒
#### 同类变式
#### 二次订正记录
```

## Subject-Specific Mistake Causes

- 研究对象选错、过程选错、受力分析漏力或多力。
- 公式适用条件误判、矢量方向错误、单位错误。
- 图像斜率/面积/截距意义误读。
- 守恒条件不满足却套用守恒。
- 实验题读数、有效数字、误差分析错误。

## Requirements

- State object, process, state, equation, and physical check.
- Use `[图片：...]` placeholders for essential diagrams when images are unavailable.
- Prevention rules should be checklist-like, such as "先画受力图，再列方程".
