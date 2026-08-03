# 数学错题本规范

## Output

```text
high_school/数学/错题本/<错题主题>.md
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

- 概念条件遗漏、定义域忽略、分类讨论不全。
- 公式套用错误、等价变形错误、符号和范围错误。
- 计算失误、设参不当、证明逻辑跳步。
- 图像理解错误、几何关系误判、概率事件划分错误。

## Requirements

- Show the exact step where the wrong path starts.
- Include condition checks and result verification.
- Same-type variants should test whether the method, not the original answer, is mastered.
