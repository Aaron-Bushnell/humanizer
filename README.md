<p align="center">
  <img src="https://img.shields.io/badge/patterns-47-blue?style=for-the-badge" alt="47 patterns">
  <img src="https://img.shields.io/badge/voices-5-orange?style=for-the-badge" alt="5 voices">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/Claude%20Code-skill-8A2BE2?style=for-the-badge" alt="Claude Code skill">
</p>

<h1 align="center">🖊️ Humanizer</h1>
<p align="center"><strong>Make AI-generated text read like a specific, opinionated human wrote it.</strong></p>
<p align="center">让 AI 生成的文本读起来像一个有血有肉、有观点的人写的。</p>

<p align="center">
  <a href="#-english">English</a> ·
  <a href="#-中文">中文</a> ·
  <a href="#-quick-start">Quick Start</a> ·
  <a href="#-how-it-works">How It Works</a> ·
  <a href="#-usage">Usage</a> ·
  <a href="#-deep-mode-probability-analysis">Deep Mode</a>
</p>

---

<a name="-english"></a>
## 🇬🇧 English

### What Is Humanizer?

Humanizer is a **Claude Code skill** that detects and rewrites AI-generated text. It scans for **47 AI writing patterns** (43 surface-level + 4 probability-informed), scores text on a 0–100 AI-tell density scale, and rewrites it in one of 5 distinct human voice profiles.

It's the difference between:

> *"This comprehensive guide delves into the intricacies of our authentication system. The platform leverages cutting-edge JWT technology to provide a seamless, secure, and robust authentication experience."*

and:

> *"The auth system uses JWTs. Tokens expire after 15 minutes; refresh tokens last 7 days. The token rotation logic is in `src/auth/refresh.ts` if you need to change the expiry windows."*

### Why Humanizer?

**The problem:** LLMs generate text that regresses to the statistical mean — safe words, uniform sentences, boilerplate transitions. Statistical detectors (like [Uncertainty++](https://arxiv.org/abs/2606.02158), ICML 2025) exploit these distributional tells: the bottom ~15% of tokens by probability carry **3.5× more discriminative signal** between human and AI text.

**The solution:** Humanizer rewrites text to reshape its probability distribution — injecting low-probability tokens (specific numbers, proper names, technical terms), creating information-density texture, and breaking high-probability transitional chains. It's not just surface editing; it's distributional remodeling.

### Features

| Feature | Description |
|---------|-------------|
| 🔍 **47 Detection Patterns** | 43 surface patterns (P1–P43: AI vocabulary, hedging, formatting tells, community-discovered patterns) + 4 probability-informed patterns (P44–P47: backed by ICML 2025 research on token probability distributions) |
| 🎭 **5 Voice Profiles** | `casual` · `professional` · `technical` · `warm` · `blunt` — each with distinct sentence rhythm, contraction rules, and personality |
| 📊 **0–100 AI-Tell Score** | Quantifies how "AI-flagged" text reads using a weighted formula combining pattern density, burstiness, and vocabulary blacklist ratio |
| 🔄 **Iterative Rewriting** | `--iterate N` loops detect → rewrite → detect until convergence |
| 🧬 **Deep Probability Mode** | `--deep` runs `token_analyzer.py` for statistical profiling: token-level surprise, Gini coefficient, Rényi entropy, AI text likelihood — then rewrites targeting the lowest-probability token positions |
| 🎯 **Tail Token Smuggling** | `--aggressive --deep` strategy based on Guo et al. (2025): deliberately injects low-probability tokens (specific numbers, insider jargon, unexpected opinions) at detector-sensitive positions |
| 📝 **In-Place Editing** | `--mode edit --file path/to/file.md` makes minimal targeted edits directly |
| 🌍 **Zero Dependencies (Standard)** | Standard modes need no API calls, no network, no Python packages. Pure Markdown skill. |
| 🔧 **Extensible** | Auto-loads `humanizer-context.md` from your project root for brand-specific voice guidance |

### Pattern Catalog (47 Total)

| Category | Count | IDs | What It Catches |
|----------|-------|-----|-----------------|
| Content | 8 | P1–P8 | Significance inflation, name-dropping, -ing fluff, promotional language, vague attributions, formulaic "challenges" sections, AI vocabulary words, copula avoidance |
| Language & Style | 10 | P9–P18 | Negative parallelisms, rule-of-three, synonym cycling, false ranges, em dashes, boldface overuse, structured list syndrome, title case, curly quotes, formal register |
| Communication | 3 | P19–P21 | Chatbot artifacts ("I hope this helps!"), knowledge-cutoff disclaimers, sycophantic tone |
| Filler & Hedging | 9 | P22–P30 | Filler phrases, excessive hedging, generic positive conclusions, hallucination markers, error alternation, question-format titles, Markdown bleeding, "comprehensive overview" openings, uniform sentence length |
| Emerging (2026) | 13 | P31–P43 | Noun-phrase cycling, collaborative communication leaking, placeholder text, chatbot citation markup, UTM parameters, style/register shifts, overattribution, reshuffling immunity, "whether" summary sentences, symbolic gloss, infomercial hooks, erratic bolding, treadmill effect |
| **Probability-Informed** ✨ | **4** | **P44–P47** | **High-probability monotony, entropy-flat rollout, low-probability deficit, transitional predictability** — grounded in Guo et al. (2025) ICML 2025 |

### The Probability Principle

Traditional "make it sound human" advice says: *"choose the second or third word that comes to mind."*

Humanizer formalizes this into a statistical strategy backed by peer-reviewed research:

1. **Low-probability tokens carry 3.5× more human signal** (Assumption 3.1, Guo et al. 2025). The bottom ~15% of tokens by conditional probability are where detectors look. Humanizer targets these positions.
2. **Surface rewrites don't change entropy shape** (Proposition 3.4). Swapping synonyms and reordering sentences leaves the Rényi entropy distribution nearly unchanged — entropy-based detectors see through it. You must add genuine information, not just rephrase.
3. **Boilerplate transitions are free detector signal.** "Additionally," "Furthermore," "Moreover" — these near-deterministic tokens sit at probability peaks. Cutting them is the highest-ROI single change.

---

<a name="-中文"></a>
## 🇨🇳 中文

### Humanizer 是什么？

Humanizer 是一个 **Claude Code 技能**，用于检测并重写 AI 生成的文本。它扫描 **47 种 AI 写作模式**（43 种表层 + 4 种概率驱动型），对文本进行 0–100 的 AI 痕迹评分，并用 5 种不同的人类声音风格进行重写。

它能把这样的文字：

> *"This comprehensive guide delves into the intricacies of our authentication system. The platform leverages cutting-edge JWT technology to provide a seamless, secure, and robust authentication experience."*

变成这样：

> *"The auth system uses JWTs. Tokens expire after 15 minutes; refresh tokens last 7 days. The token rotation logic is in `src/auth/refresh.ts` if you need to change the expiry windows."*

### 为什么需要 Humanizer？

**问题：** 大语言模型生成的文本回归统计均值——安全的词汇、均一的句式、套话过渡词。统计检测器（如 ICML 2025 发表的 [Uncertainty++](https://arxiv.org/abs/2606.02158)）正是利用这些分布特征：底部约 15% 概率的 token 携带的判别信号是高概率 token 的 **3.5 倍**。

**方案：** Humanizer 不仅做表面替换，而是重塑文本的概率分布——注入低概率 token（具体数字、专有名词、技术术语），制造信息密度纹理，打断高概率过渡链。这不是表面编辑，而是分布重塑。

### 功能特色

| 功能 | 说明 |
|------|------|
| 🔍 **47 种检测模式** | 43 种表层模式（AI 词汇、套话、格式指纹、社区发现的模式）+ 4 种概率驱动模式（P44–P47：基于 ICML 2025 论文的 token 概率分布研究） |
| 🎭 **5 种声音风格** | `casual`（随意）· `professional`（专业）· `technical`（技术）· `warm`（温暖）· `blunt`（直白）——各有不同的句长节奏、缩写规则和个性 |
| 📊 **0–100 AI 痕迹评分** | 用加权公式量化文本的"AI 嫌疑度"：综合模式密度、爆发度（句长方差）、词汇黑名单比 |
| 🔄 **迭代重写** | `--iterate N` 循环执行检测→重写→检测，直到收敛 |
| 🧬 **深度概率模式** | `--deep` 运行 `token_analyzer.py` 做统计画像：token 级惊讶度、基尼系数、Rényi 熵、AI 文本似然度——然后在检测器最敏感的低概率 token 位置进行精准重写 |
| 🎯 **尾 Token 走私策略** | `--aggressive --deep`：基于论文 Assumption 3.1，故意在检测器敏感位置注入低概率 token（具体数字、圈内术语、意外观点） |
| 📝 **原地编辑** | `--mode edit --file path/to/file.md` 对文件做最小化精准修改 |
| 🌍 **标准模式零依赖** | 标准模式无需 API 调用、无需网络、无需安装任何 Python 包。纯 Markdown 技能。 |
| 🔧 **可扩展** | 自动从项目根目录加载 `humanizer-context.md`，支持品牌定制的声音指导 |

### 概率原理

传统的"让人读起来像人"建议是：*"选第二个或第三个想到的词。"*

Humanizer 将这条建议形式化为有论文支撑的统计策略：

1. **低概率 token 携带 3.5× 的人类信号**（论文假设 3.1）。条件概率底部约 15% 的 token 是检测器最关注的位置，Humanizer 精准瞄准这些位置。
2. **表面改写不改变熵分布形状**（论文命题 3.4）。换同义词和调语序几乎不改变 Rényi 熵分布——基于熵的检测器能"看穿"这类修改。你必须增加真正的信息，而非仅改变措辞。
3. **套话过渡词是免费的检测信号。** "Additionally"、"Furthermore"、"Moreover"——这些近乎确定性的 token 位于概率分布的峰值。删掉它们是投资回报率最高的单项改动。

---

<a name="-quick-start"></a>
## 🚀 Quick Start

### Prerequisites

Humanizer is a [Claude Code](https://claude.ai/code) skill. It requires Claude Code to be installed.

```bash
# Install Claude Code (if you haven't)
npm install -g @anthropic-ai/claude-code
```

### Install the Skill

```bash
# Clone into your Claude skills directory
git clone https://github.com/Aaron-Bushnell/humanizer.git ~/.claude/skills/humanizer
```

Or manually copy the `humanizer/` folder into `~/.claude/skills/`.

### Basic Usage

In Claude Code, invoke the skill directly:

```bash
# Detect AI patterns in text
/humanizer --mode detect --score "Your text here..."

# Rewrite with a specific voice
/humanizer --mode rewrite --voice casual "Your text here..."

# Edit a file in place
/humanizer --mode edit --file docs/README.md --voice professional

# Iterate until clean
/humanizer --mode rewrite --iterate 3 --score "Your text here..."

# Deep probability-aware rewrite (uses token_analyzer.py)
/humanizer --mode deep --aggressive --score "Your text here..."
```

### Python Script (Deep Mode Only)

The `--deep` mode requires running `token_analyzer.py` once:

```bash
# No extra install needed — uses Python stdlib only
python scripts/token_analyzer.py --input sample.txt --format summary
```

The script outputs a statistical profile of the text's token distribution — low-probability positions, Gini coefficient, Rényi entropy, and an AI-text likelihood estimate. Humanizer then uses this data to target its rewrite at the most detector-sensitive positions.

---

<a name="-how-it-works"></a>
## 🔬 How It Works

### Architecture

```
Input Text
    │
    ├─→ [Pattern Detection] ── 47 patterns across 6 categories
    │         │
    │         └─→ [Score: 0-100] ← weighted formula
    │
    ├─→ [Optional: token_analyzer.py] ── Statistical profiling
    │         │                               (Gini, entropy, surprise)
    │         └─→ Low-probability position map
    │
    ├─→ [Voice Injection] ── 5 profiles × 11 soul techniques
    │
    └─→ [Rewrite Engine] ── Targeted fixes at pattern + probability level
              │
              └─→ Output + Change Summary
```

### Detection → Rewrite Pipeline

```
                    ┌──────────────┐
                    │  Input Text   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  DETECT: 47   │
                    │  patterns     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  DEEP? ──────┤ (if --deep)
                    │  token_      │
                    │  analyzer.py │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  REWRITE:    │
                    │  • Fix patterns│
                    │  • Inject tail │
                    │  • Vary entropy │
                    │  • Apply voice  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  VERIFY:     │
                    │  Score ↓     │
                    │  Patterns ↓  │
                    │  Entropy ↑   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Output +     │
                    │  Change Report│
                    └──────────────┘
```

### The 47-Pattern System

**Intuition:** AI text has a fingerprint. Not one big tell, but dozens of small ones that compound.

| Layer | What It Catches | Example |
|-------|----------------|---------|
| **Content** (P1–P8) | WHAT is said | "pivotal moment", "showcasing", "Experts believe" |
| **Language & Style** (P9–P18) | HOW it's said | "Not only X but Y", em dashes, Title Case |
| **Communication** (P19–P21) | WHO is speaking | "I hope this helps!", "Great question!" |
| **Filler & Hedging** (P22–P30) | WHAT shouldn't be there | Uniform sentence length, generic conclusions |
| **Emerging** (P31–P43) | Community-discovered 2026 tells | LLM citation markup, reshuffling immunity, infomercial hooks |
| **Probability** (P44–P47) ✨ | DISTRIBUTION tells | Token monotony, flat entropy, tail deficit, boilerplate transitions |

---

<a name="-usage"></a>
## 📖 Usage Guide

### Modes

| Mode | What It Does | When to Use |
|------|-------------|-------------|
| `detect` | Scans text, reports patterns + score. No changes. | Auditing before publishing |
| `rewrite` | Full rewrite with voice injection. Default. | Transforming AI draft into publishable text |
| `edit` | In-place minimal edits via Edit tool. | Cleaning a file without full rewrite |
| `deep` | Probability-aware rewrite with token analysis. | When you need to evade strong statistical detectors |

### Voices

| Voice | Sentence Rhythm | Signature |
|-------|----------------|-----------|
| `casual` | Fragments, contractions, first person | Blog posts, social media, personal essays |
| `professional` | 3–5 sentence paragraphs, dry wit | Business comms, reports, newsletters |
| `technical` | Numbers > adjectives, code-like clarity | API docs, READMEs, engineering blogs |
| `warm` | "We" language, shorter paragraphs | Tutorials, onboarding, community posts |
| `blunt` | Shortest sentences, no hedging, active voice | Internal comms, code reviews, opinion pieces |

### Flags

| Flag | Effect |
|------|--------|
| `--score` | Prepend `[Score: NN/100]` before output |
| `--iterate N` | Loop detect→rewrite→detect up to N times (max 3) |
| `--aggressive` | Heavier rewrite: shorter sentences, more personality, kills all hedging |
| `--purpose TYPE` | Layer domain rules: `essay`, `email`, `marketing`, `technical`, `general` |
| `--deep` | Run probability analysis via `token_analyzer.py`; rewrite targeting tail tokens |

### Examples

#### Detect AI Patterns

```bash
/humanizer --mode detect --score "In today's rapidly evolving technological landscape,
artificial intelligence is reshaping how we think about creativity. This groundbreaking
shift represents a pivotal moment..."

# Output:
# [Score: 76/100]
# ## AI Pattern Report
# Patterns found: 12
# Severity: HIGH
# | P7 | AI Vocabulary | "landscape", "groundbreaking", "pivotal" | ...
# | P1 | Significance Inflation | "represents a pivotal moment" | ...
# | P44 | High-Probability Monotony | Every noun is the safest choice | ...
```

#### Rewrite for Publication

```bash
/humanizer --mode rewrite --voice casual --score "The platform leverages cutting-edge
technology to deliver a seamless user experience. Additionally, it features robust
security measures and world-class performance."

# Output:
# [Score: 12/100]
# The platform runs on Rust. Pages load in under 200ms.
# Security-wise, we use WebAuthn — no passwords, no phishing.
```

#### Probability-Aware Deep Rewrite

```bash
/humanizer --mode deep --aggressive --score "AI-generated text here..."
```

This runs `token_analyzer.py`, identifies the detector's most sensitive positions, and rewrites them with deliberately surprising token choices — specific numbers, insider terms, unexpected opinions — then re-analyzes to verify the probability distribution has shifted toward human baseline.

---

<a name="-deep-mode-probability-analysis"></a>
## 🧬 Deep Mode: Probability Analysis

### The Science

Deep mode is grounded in **Guo et al. (2025)**, *"On the Salience of Low-Probability Tokens for AI-Generated Text Detection"* (ICML 2025, PMLR 306). Key findings that inform the implementation:

| Paper Finding | Humanizer Implementation |
|---------------|--------------------------|
| Bottom ~15% tokens carry 3.5× more discriminative signal (Assumption 3.1) | `token_analyzer.py` identifies these exact positions; rewrite targets them |
| Surface rewrites don't change Rényi entropy shape (Proposition 3.4) | Deep mode verifies entropy change post-rewrite; if unchanged, triggers structural rewrite |
| Low-probability focus improves ALL detectors, not just Likelihood (RQ5, Fig 6) | Tail Token Smuggling is method-agnostic — works regardless of which detector is used |
| Local uncertainty is primary signal; entropy is complementary stabilizer (Table 3) | Scoring formula: 65% weight on probability-derived terms |

### token_analyzer.py Output

```json
{
  "token_analysis": {
    "low_prob_positions": [47, 89, 142, 203],
    "low_prob_ratio": 0.12,
    "ai_signal_density": 0.08,
    "token_level_surprise": [
      {"range": [0, 20], "avg_surprise": 2.1, "description": "low surprise - generic/AI-like"},
      {"range": [40, 55], "avg_surprise": 5.8, "description": "high surprise - potential human signal"}
    ]
  },
  "distribution_stats": {
    "renyi_entropy_alpha_2": 0.61,
    "gini_coefficient": 0.25,
    "shannon_entropy": 3.42
  },
  "detection_signals": {
    "ai_text_likelihood": 0.73,
    "confidence": "high"
  }
}
```

### Deep Mode Scoring Formula

```
score = 3 × patterns_hit
      + 20 × (1 - burstiness_normalized)
      + 10 × (vocabulary_blacklist_ratio)
      + 30 × ai_text_likelihood          ← from token_analyzer.py
      + 20 × max(0, 0.18 - low_prob_ratio)
      + 15 × max(0, 0.70 - renyi_entropy)
```

Probability-derived terms carry **~65% of the weight**, matching the paper's ablation results (local uncertainty AUROC drop: -31.80 vs -6.74 for low-prob selection).

---

## 📁 File Structure

```
humanizer/
├── SKILL.md                                # Main skill definition (all 47 patterns, 5 voices, modes)
├── scripts/
│   └── token_analyzer.py                   # Statistical token-probability profiler
├── references/
│   └── tail-token-smuggling.md             # Deep strategy reference (low-prob injection)
├── README.md                               # This file
├── LICENSE                                 # MIT
└── .github/
    └── ISSUE_TEMPLATE.md                   # Bug report & feature request templates
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Add a new AI writing pattern.** Found a tell that's not in our catalog? Open an issue with examples. We add community-discovered patterns with attribution (see P38–P43 for examples).
2. **Improve a voice profile.** Each voice profile should feel distinct. If `--voice blunt` doesn't sound blunt enough, submit a PR.
3. **Expand token_analyzer.py.** Better heuristics, additional entropy measures, new statistical features. The script is designed to be API-optional (works with statistical proxies) but extensible for real logprobs when available.
4. **Translate.** We welcome translations of pattern descriptions, trigger words, and documentation.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

MIT © 2026 — see [LICENSE](LICENSE) for details.

The 4 probability-informed patterns (P44–P47) and the token_analyzer.py heuristics are implementations inspired by:

> Guo, Y., Wang, B., Fan, X., Ke, W., & Luo, H. (2025). *On the Salience of Low-Probability Tokens for AI-Generated Text Detection: A Multiscale Uncertainty Perspective.* Proceedings of the 43rd International Conference on Machine Learning (ICML 2025), PMLR 306.

---

## ⭐ Star History

If you find this useful, consider starring the repo. It helps others discover it.

---

<p align="center">
  <sub>Write like a human. Be weird, specific, inconsistent.</sub>
</p>
