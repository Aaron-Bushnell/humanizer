# Contributing to Humanizer

Thanks for your interest in contributing! Humanizer is a community-driven catalog of AI writing patterns and rewriting strategies. Here's how to help.

## Adding a New Pattern

Found an AI writing tell that's not in our 47-pattern catalog? We add community-discovered patterns with attribution (see P38–P43 for examples).

1. **Open an issue** with the pattern proposal. Include:
   - A name for the pattern (descriptive, 2-5 words)
   - 2+ example texts showing the pattern in AI output
   - 2+ counter-examples showing how a human would write it
   - Specific trigger words/phrases
   - A suggested fix strategy
   - Source (where you discovered it — blog post, HackerNews thread, personal experience)

2. **If the pattern is accepted**, submit a PR adding it to `SKILL.md`. Follow the existing pattern format:
   ```markdown
   **PXX: Pattern Name.** Description. **fix:** fix strategy.
   Triggers: specific triggers.
   > **AI:** example
   > **Human:** counter-example
   ```

3. **Attribution:** Community-discovered patterns include a `**source:**` line with a link to the original discussion or blog post.

## Improving a Voice Profile

Voice profiles should feel genuinely distinct. If `--voice blunt` sounds too soft, or `--voice warm` sounds too formal:

1. Open an issue describing what feels off, with before/after examples
2. PR guidelines: voice profile changes should not break existing behavior for other voices

## Expanding token_analyzer.py

The token analyzer uses statistical heuristics (frequency-based proxies) by default. Improvements welcome:

- **Better heuristics:** Improved surprise scoring, better AI-vocabulary detection
- **New statistical measures:** Additional entropy variants, perplexity proxies, distribution shape metrics
- **API integration:** Real logprobs support for endpoints that implement `echo=True`

### Python Conventions
- Python 3.10+ stdlib only (no external dependencies for core analysis)
- `openai` package optional (only needed for API-based logprobs)
- Keep the script under 500 lines
- Output JSON schema should remain backward-compatible

## Translating

We welcome translations of:
- Pattern descriptions and triggers (currently English)
- Voice profile guidance
- Documentation (README, CONTRIBUTING)

## Pull Request Process

1. Fork the repo and create a feature branch
2. Add or modify the relevant files
3. If adding a new pattern, include before/after examples in the PR description
4. If modifying `SKILL.md`, verify the pattern count and catalog table are updated
5. If modifying `token_analyzer.py`, include sample output showing the change

## Code of Conduct

Be respectful. Assume good faith. We're all trying to make AI text sound more human — the irony is not lost on us.
