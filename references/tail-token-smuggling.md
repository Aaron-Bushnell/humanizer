# Tail Token Smuggling: 低概率 Token 注入策略

> 基于 Guo et al. (2025), "On the Salience of Low-Probability Tokens for AI-Generated Text Detection," ICML 2025.

## 核心原理

### 什么是"尾 Token"？

论文 Assumption 3.1 证明：在 AI 文本检测中，底部 ~15% 概率的 token 携带的判别信号是高概率 token 的 **3.5 倍**。这些"尾 token"——上下文合适但统计上不太可能的词——是区分人类写作和 AI 写作的最强信号。

```
高概率 token（套话区）：
  "the", "is", "additionally", "crucial", "furthermore"
  → Human-AI LogRank gap: 0.45（弱信号）

低概率 token（尾部区）：
  "37%", "Brazil", "Sertraline", "PHQ-9", "2am coffee", "Net Promoter 72"
  → Human-AI LogRank gap: 1.59（强信号，3.5×）
```

### 为什么"走私"？

常规改写（换词、调语序）改变文本的表面，但不改变概率分布的形状。Proposition 3.4 证明：Rényi 熵在表面扰动下的变化是有界的（O(τ^min(α,1))）。这意味着基于熵的检测器（如 Uncertainty++）能"看穿"表层修改。

要真正降低检测分数，必须改变概率分布本身——在低概率区域**注入**新信号，而不是仅仅**替换**高概率区域的词汇。

---

## 可靠产生低概率的 Token 类别

以下 8 类 token 在各种 LLM 中始终产生低概率：

### 1. 具体数字
```
❌ "significant growth"（高概率套话）
✅ "grew 37%"（具体数字 = 低概率）

❌ "many participants"
✅ "10,000 participants, 47 variables, 3 years"
```

### 2. 专有名词和人名
```
❌ "the study found"
✅ "The Framingham Heart Study found"

❌ "a researcher argues"
✅ "Dr. Chen at Tsinghua argues"
```

### 3. 领域技术术语
```
❌ "the medication showed positive effects"
✅ "Sertraline reduced PHQ-9 scores by 6.2 points"
```

### 4. 非标准语法/口语化表达
```
❌ "The results were unexpected"
✅ "The results? Not what we signed up for."

❌ "It was surprising"
✅ "Weirdly, it worked"
```

### 5. 个人引用和轶事
```
❌ "Debugging can be challenging"
✅ "Debugging this at 2am with a cold cup of coffee and a stack trace that makes no sense"
```

### 6. 精确时间/位置细节
```
❌ "recently"
✅ "last Tuesday at 3pm"

❌ "in a major city"
✅ "on Nanjing Road, third floor, above the dumpling shop"
```

### 7. 感官描述
```
❌ "The interface was poorly designed"
✅ "The button was the exact shade of neon green that makes your eyes hurt"
```

### 8. 意外观点/争议性陈述
```
❌ "The API has certain limitations"
✅ "This API design is actively user-hostile"
```

---

## 放置策略

### "三明治"技术

```
[低概率 token — 具体数字/术语]
    ↓
[高概率过渡 — 短松弛句]
    ↓
[低概率 token — 个人轶事/意外观点]
```

**示例：**
```
Sertraline reduced PHQ-9 scores by 6.2 points at 8 weeks.
The placebo group dropped 2.1. NNT = 6.
I've prescribed this for three years now.
The side effects are real — about 20% of my patients get nausea in week one.
But here's what the trials don't tell you: most people who quit
do it because of the sexual side effects, not the nausea.
```

每段包含 2-3 个低概率 token 峰值，中间用短暂的过渡句连接。

### 目标指标

使用 `token_analyzer.py` 验证：

| 指标 | AI 典型值 | 人类典型值 | 激进目标 |
|------|----------|-----------|---------|
| AI Signal Density | >8% | <3% | <2% |
| Gini Coefficient | <0.25 | >0.30 | >0.35 |
| Type-Token Ratio | <0.70 | >0.78 | >0.82 |
| Hapax Legomena | <50% | >65% | >72% |
| AI Text Likelihood | >60% | <35% | <25% |

### 常见失败模式

1. **过度注入：** 每句都塞数字和术语 → 显得造作。每段 2-3 个低概率 token 即可。
2. **注入错误位置：** 只在开头和结尾改 → 概率分布整体形状不变。需要在段落中间注入。
3. **注入同质化：** 全部用数字不用其他类型 → 分布仍然可预测。混合 8 种类型。
4. **牺牲可读性：** 为了低概率而强行加 jargon → 文本不自然。低概率 token 必须在上下文中合适。

### 验证流程

```
1. 运行 token_analyzer.py 获取改写前基线
2. 识别 low_prob_positions（当前最低概率位置）
3. 在这些位置及附近注入新低概率 token
4. 重新运行 token_analyzer.py
5. 验证: low_prob_ratio ↑, ai_signal_density ↓, gini_coefficient ↑, ai_text_likelihood ↓
6. 如果 ai_text_likelihood 仍 > 35%，重复步骤 2-5
```

---

## 与 Humanizer 模式的关系

- **P44 (High-Probability Monotony)** ← 诊断：文本缺乏尾 token → 用本策略注入
- **P45 (Entropy-Flat Rollout)** ← 诊断：信息密度平坦 → 用三明治技术制造纹理
- **P46 (Low-Probability Deficit)** ← 诊断：尾 token 赤字 → 从 8 个类别系统性补充
- **P47 (Transitional Predictability)** ← 诊断：过渡词高概率 → 用低概率内容打断过渡链
- **`--aggressive + --deep`** ← 触发条件：启用完整的尾 token 走私流程

---

*参考：Guo et al. (2025), "On the Salience of Low-Probability Tokens for AI-Generated Text Detection," ICML 2025, PMLR 306.*
