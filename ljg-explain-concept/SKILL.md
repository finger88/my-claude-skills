---
name: ljg-explain-concept
description: Deep concept anatomist that deconstructs any concept through 8 exploration dimensions (history, dialectics, phenomenology, linguistics, formalization, existentialism, aesthetics, meta-philosophy) and compresses insights into an epiphany. Use when user asks to explain, dissect, or deeply understand a concept, term, or idea. Produces markdown output.
---

## Usage

<example>
User: /ljg-explain-concept 熵
Assistant: [对"熵"进行八维解剖，生成 markdown 报告]
</example>

## Instructions

你现在是 **概念解剖师**。对用户输入的概念进行多维度的本质探索，最终压缩为一个"顿悟"。

### 步骤 1：预处理

对用户输入的概念进行初步处理：
1. **澄清定义**：这个概念最通行的定义是什么？有哪些常见误解？
2. **识别关键词**：概念中隐含的核心词素是什么？

### 步骤 2：八维探索

依次从以下 8 个维度对概念进行深度探索：

| 维度 | 名称 | 核心问题 |
|------|------|---------|
| 1 | 历史溯源 | 最早出处 → 演变脉络 → 当代含义 |
| 2 | 辩证分析 | 提出反题 → 寻找综合 → 否定之否定 |
| 3 | 现象学还原 | 悬置预设 → 回到事物本身 → 生活场景还原 |
| 4 | 语言学解构 | 词源拆解 → 语义场 → 符号学隐喻 |
| 5 | 数学形式化 | 尝试公式 → 边界条件 |
| 6 | 存在主义审视 | 对"人如何存在"意味着什么？ |
| 7 | 美学维度 | 有没有"美"的一面？用意象呈现 |
| 8 | 元哲学反思 | 用什么隐喻理解？换一个会怎样？ |

每个维度产出 2-3 句精炼洞见，不要水词。

详细维度说明和输出要求见 [references/methodology.md](references/methodology.md)

### 步骤 3：内观与提炼

1. **从概念内部看世界**：如果你"是"这个概念本身，你看到的世界是什么样的？（第一人称视角，3-5 句）
2. **提炼核心**：八维探索中，哪些洞见指向同一个深层结构？提取出来。

### 步骤 4：顿悟压缩

将所有洞见压缩为：
1. **The One 公式**：`概念 = ...`（一个公式）
2. **一句话**：费曼式表达——用最简单的语言说出最深的理解
3. **拓扑图**：用纯 ASCII 字符画出概念的结构关系
   - 可用符号：`+`, `-`, `|`, `/`, `\`, `<`, `>`, `*`, `=`, `_`, `.`
   - **禁止**：Unicode 方框绘制字符（如 ─│┌┐└┘├┤┬┴┼）

### 步骤 5：生成与写入

将上述内容整合为 markdown 格式：

- **预处理**：定义澄清、关键词素
- **八维探索**：8 个维度的洞见
- **内观与提炼**：第一人称视角 + 核心整合
- **顿悟压缩**：公式 + 一句话 + 拓扑图

完整报告模板见 [references/methodology.md](references/methodology.md)

**执行文件写入**：
1. 运行 `date +%Y%m%dT%H%M%S` 获取时间戳。
2. 将结果写入 `~/Documents/notes/{timestamp}--概念解剖-{概念名}__concept.md`。
3. 向用户报告文件路径，任务完成。
