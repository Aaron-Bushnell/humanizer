"""
Token-probability analyzer for AI-generated text detection.
Computes token-level statistics and distribution heuristics inspired by
Guo et al. (2025), "On the Salience of Low-Probability Tokens for
AI-Generated Text Detection," ICML 2025.

Uses a local regex-based tokenizer (zero dependencies). Optionally calls
an OpenAI-compatible API if `echo=True` with logprobs is supported.
The core analysis runs without any API call.

Usage:
  python token_analyzer.py --input text.txt --output analysis.json
  python token_analyzer.py --input text.txt --format summary
  echo "text to analyze" | python token_analyzer.py --format summary
"""
import sys
import os
import re
import json
import math
import argparse
from collections import Counter
from datetime import datetime, timezone

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── Simple tokenizer ──
# Splits on whitespace, keeps punctuation attached to preceding word
# (rough approximation of GPT tokenization for heuristic analysis)
_WORD_RE = re.compile(r"[A-Za-z0-9]+('[A-Za-z]+)?|[^A-Za-z0-9\s]+")


def simple_tokenize(text):
    """Tokenize text into word/subword units using regex."""
    tokens = []
    for match in _WORD_RE.finditer(text):
        token_str = match.group()
        if token_str:
            tokens.append(token_str)
    return tokens


# ── Statistical heuristics (proxies for token probability signals) ──

# Common English words (top ~500) — high-frequency words are "high-probability boilerplate"
# These correlate with tokens a language model would assign high probability.
COMMON_WORDS = set("""
the be to of and a in that have i it for not on with he as you do at this
but his by from they we say her she or an will my one all would there their
what so up out if about who get which go me when make can like time no just
him know take people into year your good some could them see other than then
now look only its come over think also back after use two how our work first
well way even new want because any these give day most us great been such
still much too every is was are has had were been am been being
""".split())

# Words that signal AI-generated text (paper P7 vocabulary + boilerplate)
# Includes common inflected/derived forms for robust matching
_AI_SIGNAL_BASE = """
additionally moreover furthermore consequently thus therefore hence accordingly
crucial crucially pivotal vitally significant significantly key important importantly
essential essentially fundamental fundamentally
delve delves delved delving
showcase showcases showcased showcasing
underscore underscores underscored underscoring
highlight highlights highlighted highlighting
emphasize emphasizes emphasized emphasizing
foster fosters fostered fostering
enhance enhances enhanced enhancing
leverage leverages leveraged leveraging
utilize utilizes utilized utilizing
landscape landscapes realm realms tapestry tapestries
intricate intricacies multifaceted notably robust seamlessly seamless
groundbreaking cutting-edge world-class state-of-the-art vibrant unprecedented
transformative innovative revolutionizing revolution paradigm synergy ecosystem holistic
comprehensive overview exploration delve delve into
additionally furthermore moreover consequently thus therefore
notably strikingly remarkably profoundly deeply
""".split()
# Normalize: lowercase, strip punctuation
AI_SIGNAL_WORDS = set(w.lower().strip("'\".,!?;:-") for w in _AI_SIGNAL_BASE if w.strip())


def compute_token_statistics(tokens, low_prob_threshold=0.15):
    """
    Compute token-level statistics without API.
    Uses frequency-based heuristics as proxies for probability.
    """
    n = len(tokens)
    if n == 0:
        return _empty_stats(low_prob_threshold)

    # Token frequency (proxy for probability: frequent = high probability)
    freq = Counter(tokens)
    total = n

    # Assign a "surprise score" to each token: inverse frequency
    # Rare tokens get high surprise, common tokens get low surprise
    # This is a weak proxy for log-probability
    token_stats = []
    for i, token in enumerate(tokens):
        token_lower = token.lower().strip("'\".,!?;:-")
        # Surprise proxy: -log(freq/total), clamped
        raw_freq = freq[token]
        prob_proxy = raw_freq / total
        surprise = -math.log2(max(prob_proxy, 1e-6))

        # Adjust: common word penalty
        if token_lower in COMMON_WORDS:
            surprise *= 0.3  # common words are expected, less surprising
        # AI signal word bonus (these are high-prob boilerplate in LLM output)
        if token_lower in AI_SIGNAL_WORDS:
            surprise *= 0.5  # these are boilerplate, not genuinely surprising

        # Heuristic top candidates: most frequent tokens starting with same letter
        first_char = token_lower[:1] if token_lower else ""
        same_prefix = [(t, c) for t, c in freq.most_common(20)
                       if t.lower().startswith(first_char)][:5]

        token_stats.append({
            "index": i,
            "token": token,
            "surprise": round(surprise, 4),
            "freq": raw_freq,
            "freq_ratio": round(prob_proxy, 6),
            "is_common_word": token_lower in COMMON_WORDS,
            "is_ai_signal": token_lower in AI_SIGNAL_WORDS,
            "top_by_freq": [t for t, _ in same_prefix[:5]],
        })

    # Low-probability tokens: bottom threshold by surprise (higher surprise = lower probability)
    sorted_by_surprise = sorted(token_stats, key=lambda t: -t["surprise"])
    cutoff_idx = max(1, int(n * low_prob_threshold))
    low_prob_positions = [t["index"] for t in sorted_by_surprise[:cutoff_idx]]
    low_prob_ratio = len(low_prob_positions) / n

    # Distribution statistics on surprise scores
    surprises = [t["surprise"] for t in token_stats]
    avg_surprise = sum(surprises) / n if n > 0 else 0.0
    var_surprise = sum((s - avg_surprise) ** 2 for s in surprises) / n if n > 0 else 0.0

    # Gini coefficient of surprise distribution (higher Gini = more "spiky" = more human-like)
    sorted_s = sorted(surprises)
    cumsum = 0.0
    for i, s in enumerate(sorted_s):
        cumsum += s * (i + 1)
    gini = (2 * cumsum - (n + 1) * sum(sorted_s)) / (n * sum(sorted_s)) if sum(sorted_s) > 0 else 0.0

    # Type-Token Ratio (TTR) — higher TTR = more diverse vocabulary = more human-like
    unique_tokens = len(freq)
    ttr = unique_tokens / n

    # Hapax legomena ratio (tokens appearing only once)
    hapax = sum(1 for t, c in freq.items() if c == 1)
    hapax_ratio = hapax / n

    # AI signal word density
    ai_signal_count = sum(1 for t in tokens if t.lower().strip("'\".,!?;:-") in AI_SIGNAL_WORDS)
    ai_signal_density = ai_signal_count / n

    # Common word density (boilerplate proxy)
    common_count = sum(1 for t in tokens if t.lower().strip("'\".,!?;:-") in COMMON_WORDS)
    common_density = common_count / n

    # Rényi entropy proxy on frequency distribution
    freq_probs = [c / total for c in freq.values()]
    sum_sq = sum(p ** 2 for p in freq_probs)
    renyi_alpha_2 = -math.log2(sum_sq) if sum_sq > 0 else 0.0
    shannon = -sum(p * math.log2(p) for p in freq_probs if p > 0)

    # AI text likelihood heuristic (based on paper findings)
    # Higher common_density = more boilerplate = more AI-like
    # Higher ai_signal_density = more AI vocabulary = more AI-like
    # Lower Gini = flatter distribution = more AI-like (Proposition 3.4)
    # Lower TTR = less diverse = more AI-like
    # Lower hapax_ratio = fewer unique words = more AI-like
    score_common = min(1.0, common_density / 0.55)       # 0.55 is rough human baseline
    score_ai_vocab = min(1.0, ai_signal_density / 0.08)  # 8% AI vocab = strong signal
    score_flatness = max(0.0, 1.0 - (gini / 0.35))       # lower Gini = flatter = AI-like
    score_ttr = max(0.0, 1.0 - (ttr / 0.75))             # lower TTR = AI-like
    score_hapax = max(0.0, 1.0 - (hapax_ratio / 0.40))   # lower hapax = AI-like

    ai_likelihood = round(
        0.25 * score_common + 0.20 * score_ai_vocab + 0.25 * score_flatness
        + 0.15 * score_ttr + 0.15 * score_hapax, 4
    )

    # Token-level surprise regions
    window = max(5, n // 10)
    surprise_regions = []
    for start in range(0, n, window):
        end = min(start + window, n)
        chunk = token_stats[start:end]
        avg_s = sum(t["surprise"] for t in chunk) / len(chunk) if chunk else 0.0
        surprise_regions.append({
            "range": [start, end],
            "avg_surprise": round(avg_s, 4),
            "description": (
                "high surprise - potential human signal" if avg_s > 4.0
                else "moderate surprise" if avg_s > 2.0
                else "low surprise - generic/AI-like"
            ),
        })

    return {
        "tokens": token_stats,
        "total_tokens": n,
        "unique_tokens": unique_tokens,
        "type_token_ratio": round(ttr, 4),
        "hapax_legomena_ratio": round(hapax_ratio, 4),
        "low_prob_positions": low_prob_positions,
        "low_prob_ratio": round(low_prob_ratio, 4),
        "renyi_entropy_alpha_2": round(renyi_alpha_2, 4),
        "shannon_entropy": round(shannon, 4),
        "gini_coefficient": round(gini, 4),
        "avg_surprise": round(avg_surprise, 4),
        "var_surprise": round(var_surprise, 4),
        "ai_signal_density": round(ai_signal_density, 4),
        "common_word_density": round(common_density, 4),
        "ai_text_likelihood": ai_likelihood,
        "token_level_surprise": surprise_regions,
        "low_prob_threshold": low_prob_threshold,
        "method": "statistical-heuristics",
    }


def _empty_stats(threshold=0.15):
    return {
        "tokens": [],
        "total_tokens": 0,
        "unique_tokens": 0,
        "type_token_ratio": 0.0,
        "hapax_legomena_ratio": 0.0,
        "low_prob_positions": [],
        "low_prob_ratio": 0.0,
        "renyi_entropy_alpha_2": 0.0,
        "shannon_entropy": 0.0,
        "gini_coefficient": 0.0,
        "avg_surprise": 0.0,
        "var_surprise": 0.0,
        "ai_signal_density": 0.0,
        "common_word_density": 0.0,
        "ai_text_likelihood": 0.5,
        "token_level_surprise": [],
        "low_prob_threshold": threshold,
        "method": "statistical-heuristics",
    }


def read_input(args):
    """Read text from --input file or stdin."""
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            return f.read()
    return sys.stdin.read()


def format_summary(stats):
    """Produce a human-readable summary."""
    lines = []
    lines.append("TOKEN ANALYSIS SUMMARY")
    lines.append("=" * 60)
    lines.append(f"Method: {stats['method']}")
    lines.append(f"Total tokens: {stats['total_tokens']}")
    lines.append(f"Unique tokens: {stats['unique_tokens']} (TTR: {stats['type_token_ratio']:.3f})")
    lines.append(f"Hapax legomena: {stats['hapax_legomena_ratio']*100:.1f}% (tokens appearing only once)")
    lines.append(f"Low-probability tokens (<{stats['low_prob_threshold']*100:.0f}%): "
                 f"{len(stats['low_prob_positions'])} ({stats['low_prob_ratio']*100:.1f}%)")
    lines.append(f"AI signal word density: {stats['ai_signal_density']*100:.1f}%")
    lines.append(f"Common word density: {stats['common_word_density']*100:.1f}%")
    lines.append(f"Renyi entropy (alpha=2): {stats['renyi_entropy_alpha_2']:.4f}")
    lines.append(f"Shannon entropy: {stats['shannon_entropy']:.4f}")
    lines.append(f"Gini coefficient: {stats['gini_coefficient']:.4f}")
    lines.append(f"Avg surprise: {stats['avg_surprise']:.4f}")
    lines.append(f"AI text likelihood: {stats['ai_text_likelihood']*100:.0f}%")
    lines.append("")

    confidence = (
        "HIGH" if stats['ai_text_likelihood'] > 0.7
        else "MEDIUM" if stats['ai_text_likelihood'] > 0.4
        else "LOW"
    )
    lines.append(f"Confidence: {confidence}")
    lines.append("")

    # Top surprising tokens
    tokens = stats["tokens"]
    if tokens:
        lines.append("Top 10 most surprising tokens (proxy for low-probability):")
        surprising = sorted(tokens, key=lambda t: -t["surprise"])[:10]
        for t in surprising:
            flags = []
            if t.get("is_ai_signal"):
                flags.append("AI-VOCAB")
            if t.get("is_common_word"):
                flags.append("COMMON")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            freq_similar = ", ".join(t.get("top_by_freq", [])[:4])
            lines.append(f"  {t['index']:4d}. \"{t['token']}\" "
                         f"(surprise={t['surprise']:.2f}, freq={t['freq']}){flag_str}"
                         f"  similar: [{freq_similar}]")

    lines.append("")
    lines.append("Surprise regions:")
    for r in stats["token_level_surprise"]:
        lines.append(f"  tokens {r['range'][0]:4d}-{r['range'][1]:4d}: "
                     f"avg_surprise={r['avg_surprise']:.3f} — {r['description']}")

    lines.append("")
    if stats['ai_text_likelihood'] > 0.6:
        lines.append("Interpretation: HIGH AI signal. Distribution, vocabulary, and diversity all AI-like.")
    elif stats['ai_text_likelihood'] > 0.35:
        lines.append("Interpretation: MIXED signal. Some human-like features, some AI-like.")
    else:
        lines.append("Interpretation: LOW AI signal. Distribution consistent with human authorship.")

    lines.append("")
    lines.append("Note: Analysis uses statistical heuristics (frequency-based proxies).")
    lines.append("For real token-level logprobs, use an API endpoint that supports echo=True with logprobs.")
    lines.append("Reference: Guo et al. (2025), ICML 2025.")

    return "\n".join(lines)


def build_output(stats, metadata):
    """Build the full output dict for JSON format."""
    return {
        "metadata": metadata,
        "token_analysis": {
            "tokens": stats["tokens"],
            "total_tokens": stats["total_tokens"],
            "unique_tokens": stats["unique_tokens"],
            "type_token_ratio": stats["type_token_ratio"],
            "hapax_legomena_ratio": stats["hapax_legomena_ratio"],
            "low_prob_positions": stats["low_prob_positions"],
            "low_prob_ratio": stats["low_prob_ratio"],
            "ai_signal_density": stats["ai_signal_density"],
            "common_word_density": stats["common_word_density"],
            "token_level_surprise": stats["token_level_surprise"],
        },
        "distribution_stats": {
            "renyi_entropy_alpha_2": stats["renyi_entropy_alpha_2"],
            "shannon_entropy": stats["shannon_entropy"],
            "gini_coefficient": stats["gini_coefficient"],
            "avg_surprise": stats["avg_surprise"],
            "var_surprise": stats["var_surprise"],
            "probability_mass_bottom_15pct": round(
                sum(t["surprise"] for t in stats["tokens"] if t["index"] in stats["low_prob_positions"])
                / max(sum(t["surprise"] for t in stats["tokens"]), 1e-10), 4
            ) if stats["tokens"] else 0.0,
        },
        "detection_signals": {
            "ai_text_likelihood": stats["ai_text_likelihood"],
            "confidence": (
                "high" if stats["ai_text_likelihood"] > 0.7
                else "medium" if stats["ai_text_likelihood"] > 0.4
                else "low"
            ),
            "method": stats["method"],
            "rationale": (
                f"TTR={stats['type_token_ratio']:.3f}, "
                f"Hapax={stats['hapax_legomena_ratio']:.3f}, "
                f"AI vocab={stats['ai_signal_density']:.3f}, "
                f"Common={stats['common_word_density']:.3f}, "
                f"Gini={stats['gini_coefficient']:.3f}, "
                f"Renyi H2={stats['renyi_entropy_alpha_2']:.3f}. "
                f"See Guo et al. (2025), Assumption 3.1, Proposition 3.4."
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Token-probability analyzer for AI-generated text detection (Guo et al. 2025)",
    )
    parser.add_argument("--input", "-i", type=str, default=None,
                        help="Input text file (default: stdin)")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output JSON file (default: stdout)")
    parser.add_argument("--low-prob-threshold", type=float, default=0.15,
                        help="Threshold for low-probability classification (default: 0.15)")
    parser.add_argument("--format", "-f", choices=["json", "summary"], default="summary",
                        help="Output format (default: summary)")
    args = parser.parse_args()

    # Read input
    text = read_input(args)
    if not text.strip():
        print("Error: no input text provided.", file=sys.stderr)
        sys.exit(1)

    # Tokenize
    tokens = simple_tokenize(text)
    if not tokens:
        print("Error: could not tokenize input.", file=sys.stderr)
        sys.exit(1)

    # Compute statistics
    stats = compute_token_statistics(tokens, args.low_prob_threshold)

    # Metadata
    metadata = {
        "total_tokens": stats["total_tokens"],
        "unique_tokens": stats["unique_tokens"],
        "low_prob_threshold": args.low_prob_threshold,
        "method": "statistical-heuristics (frequency proxies)",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # Output
    if args.format == "summary":
        output_text = format_summary(stats)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_text)
        else:
            print(output_text)
    else:
        output_data = build_output(stats, metadata)
        json_text = json.dumps(output_data, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_text)
        else:
            print(json_text)


if __name__ == "__main__":
    main()
