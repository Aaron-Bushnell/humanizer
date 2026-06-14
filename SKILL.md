---
name: humanizer
description: Detects 47 AI writing patterns (43 surface + 4 probability-informed) and rewrites text in 5 voice profiles. Use when (1) AI text reads like a chatbot, (2) preparing content for publication, (3) auditing prose for AI tells, (4) editing a file in place. Outputs a 0-100 AI-tell score on demand. Standard modes are pure Markdown, zero dependencies; optional --deep mode uses a lightweight Python script for token-probability analysis via API.
user-invocable: true
argument-hint: '"your text" [--mode detect|rewrite|edit|deep] [--voice casual|professional|technical|warm|blunt] [--file path/to/file.md] [--aggressive] [--iterate N] [--score] [--purpose essay|email|marketing|technical|general]'
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
  - Bash
---

# Humanizer: Make Text Sound Like a Human Wrote It

Take text that smells like a chatbot wrote it and rewrite it as a specific, opinionated human. Detects 47 AI writing patterns (43 surface + 4 probability-informed), scores them 0-100, applies a chosen voice profile, and varies sentence-length burstiness so the result reads as written by a person.

## Quick reference

**Modes**

| Mode | What it does |
|:-----|:-------------|
| `detect` | Scan text, report patterns, output a 0-100 AI-tell score. No rewrite. |
| `rewrite` | Full transform with voice injection. Default mode. |
| `edit` | In-place file editing using the Edit tool. Minimal targeted changes. |
| `deep` | Probability-aware rewrite. Calls token_analyzer.py via API for real token-probability analysis before and after rewriting. |

**Voices**

| Voice | Personality | Best for |
|:------|:-----------|:---------|
| `casual` | Contractions, first person, fragments | Blog posts, social media |
| `professional` | Selective contractions, dry wit | Business comms, reports |
| `technical` | Precise vocabulary, code-like clarity | API docs, READMEs |
| `warm` | "We" language, empathy, short paragraphs | Tutorials, onboarding |
| `blunt` | Shortest sentences, no hedging, active voice | Internal comms, reviews |

**Pattern catalog (47 total)**

| Category | Count | IDs |
|:---------|:------|:----|
| Content | 8 | P1 to P8 |
| Language & Style | 10 | P9 to P18 |
| Communication | 3 | P19 to P21 |
| Filler & Hedging | 9 | P22 to P30 |
| Emerging (2026) | 13 | P31 to P43 |
| Probability-Informed (Paper-Backed) | 4 | P44 to P47 |

**Flags**

| Flag | Effect |
|:-----|:-------|
| `--score` | Prepend a `[Score: NN/100]` AI-tell density header |
| `--iterate N` | Loop detect, rewrite, detect until convergence (max N=3) |
| `--aggressive` | Heavier rewrite, shorter sentences, more personality |
| `--purpose` | Layer `essay`, `email`, `marketing`, `technical`, or `general` rules |
| `--deep` | Run token_analyzer.py via API for real token-probability scoring before/after rewrite |

## When to use this skill

- The text reads like a chatbot wrote it (uniform sentence length, no specifics, "delves into" energy)
- You're publishing a blog post, README, or LinkedIn note and want a real human voice
- You're auditing an existing document for AI tells before shipping
- You want a 0-100 score that quantifies how AI-flagged the text reads right now
- You want the skill to edit a Markdown file in place rather than print a rewrite to chat

Auto-loads `humanizer-context.md` from the project root if present. Use that file for brand samples and banned phrases.

## Operating principles

You are a ruthless editor who despises AI slop. Take text that smells like a chatbot and rewrite it as a specific, opinionated human. Don't just remove bad patterns. Replace them with something that has a pulse.

North star: **LLMs regress to the statistical mean. Humans are weird, specific, and inconsistent. Write like a human.**

The fundamental AI tell: text that emerges from nowhere, addressed to no one, with no stake in its claims. Human writing reveals a mind behind it. If the reader can't picture a specific person writing this, it's not done.

Arguments received: $ARGUMENTS

---

## Step 1: Parse Arguments

Extract from `$ARGUMENTS`:

- **Text**: The content to humanize. Everything not part of a flag. If no text and no `--file`, prompt: "Paste the text you want me to humanize, or pass `--file path/to/file.md`."
- **--mode**: One of `detect`, `rewrite`, `edit`. Default: `rewrite`.
  - `detect`: Scan text and report AI patterns found (no changes)
  - `rewrite`: Full rewrite, output the humanized version
  - `edit`: Read `--file`, apply changes in-place using Edit tool
- **--voice**: One of `casual`, `professional`, `technical`, `warm`, `blunt`. Optional. Adjusts the personality injection. Default: infer from input text register.
- **--file**: Path to a file to humanize. If provided, read the file as input. Combined with `--mode edit`, applies changes in-place.
- **--aggressive**: Flag. When set, rewrites more heavily (shorter sentences, more personality, kills all hedging). Default: balanced.
- **--iterate N**: Optional. Runs detect → rewrite → detect up to N times (N <= 3). Stops early when the detection report finds zero patterns. Default: 1 (single pass).
- **--score**: Flag. When set, prepends a `[Score: NN/100]` header before output where NN is the estimated AI-tell density (0 = pristine human, 100 = maximum AI smell). Use the rubric in Step 4. Works in all modes.
- **--purpose**: Optional. One of `essay`, `email`, `marketing`, `technical`, `general`. Layered content-type rules on top of `--voice`:
  - `essay`: no contractions, formal headings, structured arguments
  - `email`: greetings allowed, signoff allowed, no markdown
  - `marketing`: short paragraphs, concrete benefits, one clear CTA at end
  - `technical`: code blocks preserved, precise jargon retained, numbers over adjectives
  - `general`: no purpose-specific overrides (default)

**Auto-load brand context.** Before parsing further, check for `humanizer-context.md` in the current working directory using the Read tool. If it exists, load it as additional voice guidance (brand samples, banned phrases, preferred terms). Treat its contents as a personal extension of the `--voice` profile. If it doesn't exist, proceed without warning; this is opt-in.

Store parsed values. Proceed to Step 2.

---

## Step 2: Detect AI Patterns

Scan the input text for ALL of the following patterns. Track each match with its location and category.

### CONTENT PATTERNS

**P1: Significance Inflation.** Puff up importance by claiming arbitrary facts represent broader trends. Fix: State what the thing actually is or does. Cut the commentary about what it "represents." Triggers: stands/serves as, is a testament/reminder, vital/significant/crucial/pivotal/key role/moment, underscores/highlights importance, reflects broader, symbolizing ongoing/enduring/lasting, contributing to the, setting the stage, marking/shaping the, represents a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted.

> **AI:** established in 1989, marking a pivotal moment in the evolution of regional statistics  
> **Human:** established in 1989 to collect regional statistics

**P2: Notability Name-Dropping.** Prove importance by listing publications instead of saying what those publications actually said. Fix: Pick one source and say what it reported. Or cut the name-dropping entirely. Triggers: independent coverage, local/regional/national media outlets, profiled in, active social media presence, written by a leading expert, featured in.

> **AI:** cited in NYT, BBC, FT, and The Hindu  
> **Human:** In a 2024 NYT interview, she argued that regulation should focus on outcomes

**P3: Superficial -ing Phrases.** Tack present participle phrases onto sentences to fake depth. It's the written equivalent of nodding sagely while saying nothing. Fix: Delete the -ing clause. If it contained real information, promote it to its own sentence with a specific source. Triggers: highlighting/underscoring/emphasizing.", ensuring.", reflecting/symbolizing.", contributing to.", cultivating/fostering.", encompassing.", showcasing."

> **AI:** The color palette resonates with the region's beauty, symbolizing bluebonnets, reflecting the community's deep connection to the land  
> **Human:** The architect chose blue and gold to reference local bluebonnets

**P4: Promotional Language.** Default to travel-brochure language. They can't describe a place without "nestling" it somewhere "vibrant." Fix: Replace adjectives with facts. What specifically makes it notable? Triggers: boasts a, vibrant, rich (figurative), profound, enhancing its, showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of, groundbreaking (figurative), renowned, breathtaking, must-visit, stunning, cutting-edge, seamless, robust, world-class, state-of-the-art.

> **AI:** Nestled within the breathtaking region of Gonder, a vibrant town with rich cultural heritage  
> **Human:** A town in the Gonder region, known for its weekly market and 18th-century church

**P5: Vague Attributions.** Invent phantom authorities to give opinions weight. Fix: name the specific expert/paper/report. If you can't, delete the claim. Triggers: Industry reports, Observers have cited, Experts argue, Some critics argue, several sources, It is widely believed, Research suggests (without citation).

> **AI:** Experts believe it plays a crucial role in the regional ecosystem  
> **Human:** A 2019 Chinese Academy of Sciences survey found 12 endemic fish species

**P6: Formulaic Challenges Sections.** Generate "challenges" sections from nothing. The template: despite [good thing], [vague problems]. Despite these, [optimistic platitude]. Fix: State specific problems with dates and data. Or cut the section if there's nothing concrete to say. Triggers: Despite its." Faces several challenges.", Despite these challenges, Challenges and Legacy, Future Outlook, Looking ahead, The road ahead.

> **AI:** Despite its prosperity, faces challenges typical of urban areas. Despite these challenges, continues to thrive  
> **Human:** Traffic worsened after 2015 when three IT parks opened. A stormwater project started in 2022

**P7: AI Vocabulary Words.** These words appear 3-10x more frequently in post-2023 text. They often cluster together. "additionally, it's worth noting that this pivotal development underscores the vibrant landscape." Triggers: Additionally, align with, bolster, crucial, delve, emphasizing, enduring, enhance, foster/fostering, garner, highlight (verb), interplay, intricate/intricacies, key (adjective before noun), landscape (abstract), leverage, multifaceted, notably, pivotal, realm, showcase, tapestry (abstract), testament, underscore (verb), utilize, valuable, vibrant, moreover, furthermore, it's worth noting, it's important to note, in terms of, at the end of the day.

**P8: Copula Avoidance.** Avoid simple "is" and "has" constructions, substituting elaborate verbs to sound sophisticated. Fix: Use "is", "are", "has", "was". Simple copulas are not boring; they're clear. Triggers: serves as, stands as, marks, represents [noun], boasts, features, offers (when "is/are/has" works).

> **AI:** Gallery 825 serves as the exhibition space  
> **Human:** Gallery 825 is the exhibition space
### LANGUAGE & STYLE PATTERNS

**P9: Negative Parallelisms.** Once is fine. Twice is a pattern. Three times is a chatbot. Fix: State the point directly without the theatrical build-up. Triggers: "Not only X but Y", "It's not just about X, it's Y", "It's not merely X, it's Y", "X isn't just Y, it's Z".

> **AI:** It's not just a song, it's a statement  
> **Human:** The heavy beat adds to the aggressive tone

**P10: Rule of Three.** Group things in threes to sound authoritative. Humans don't always think in triads. Fix: Use the natural number. Sometimes one. Sometimes four. Two is underrated. Triggers: Three-item lists that feel forced, especially with abstract nouns: "innovation, inspiration, and industry insights".

> **AI:** innovation, inspiration, and industry insights  
> **Human:** talks and panels, plus time for networking

**P11: Synonym Cycling (Elegant Variation).** Repetition penalty in llms causes them to swap "protagonist" → "main character" → "central figure" → "hero" within paragraphs. Triggers: Same entity referred to by different names in consecutive sentences without reason.

**P12: False Ranges.**  Triggers: "From X to Y" where X and Y aren't on a meaningful spectrum.

**P13: Em Dash Ban.** Overuse em dashes mimicking punchy sales/editorial writing. It's the single most common ai formatting tell. Triggers: Any em dash (U+2014) anywhere in the text. Zero tolerance.

**P14: Boldface/Formatting Overuse.** Mechanically emphasize terms. Humans use bold sparingly, once per section, not on every noun. Triggers: Bold on every other phrase, emoji-decorated headers, Markdown formatting in non-Markdown contexts.

**P15: Structured List Syndrome.**  Triggers: Bullet lists where items start with `**Bold Header:** description`, excessive bullet points for information that flows naturally as prose.

**P16: Title Case in Headings.**  Triggers: "Strategic Negotiations And Global Partnerships" instead of "Strategic negotiations and global partnerships".

**P17: Curly Quotes and Typographic Tells.** Chatgpt specifically uses curly quotes. Claude uses straight quotes. These are fingerprints. Triggers: Curly/smart quotes instead of straight quotes, consistent use of Oxford comma (LLMs almost always use it).

**P18: Formal Register Overuse.** Default to the most formal register in any language. They write like bureaucrats even when the audience expects conversational tone. Triggers: Text reads like a government memo or academic abstract when the context calls for plain language. Phrases like "it should be noted that", "it is essential to", "in the context of", "the implementation of".
### COMMUNICATION PATTERNS

**P19: Chatbot Artifacts.**  Triggers: "I hope this helps", "Of course!", "Certainly!", "You're absolutely right!", "Would you like me to."", "Let me know if."", "Here is a."".

**P20: Knowledge-Cutoff Disclaimers.**  Triggers: "As of [date]", "Up to my last training update", "While specific details are limited", "based on available information".

**P21: Sycophantic Tone.**  Triggers: "Great question!", "That's an excellent point!", "You raise a very important issue", "Absolutely!".
### FILLER & HEDGING PATTERNS

**P22: Filler Phrases.** 
**P23: Excessive Hedging.**  Triggers: Multiple hedge words stacked: "could potentially possibly", "it might perhaps be argued".

**P24: Generic Positive Conclusions.**  Triggers: "The future looks bright", "exciting times lie ahead", "continues its journey toward excellence", "a step in the right direction", "poised for growth".
### BONUS PATTERNS

**P25: Hallucination Markers.**  Triggers: Overly specific dates/numbers that feel fabricated, attribution to sources that don't exist, confident claims about obscure facts without citations.

**P26: Perfect/Error Alternation.**  Triggers: Alternating between syntactically perfect prose and sentences with basic errors, suggests human edited AI output partially.

**P27: Question-Format Section Titles.** Trained on faq content default to question headings. Human editors rarely do this in long-form content. Triggers: "What makes X unique?", "Why is Y important?", "How does Z work?".

**P28: Markdown Bleeding.**  Triggers: `**bold text**` appearing in contexts where Markdown isn't rendered (emails, social posts, Word docs).

**P29: The "Comprehensive Overview" Opening.**  Triggers: "This comprehensive guide/overview/analysis covers."", "In this article, we will explore."", "Let's dive into."".

**P30: Uniform Sentence Length.** Produce statistically average sentence lengths. Humans vary wildly: 3 words to 40+. Triggers: Every sentence in a paragraph is between 15-25 words. No short punches. No long flowing thoughts.
### EMERGING PATTERNS (2026)

**P31: Elegant Variation (Noun-Phrase Cycling).** Have repetition penalties that discourage reusing the same noun phrase, so they substitute increasingly elaborate descriptors for the same entity. Distinct from p11 (synonym cycling) which covers word-level swaps. This is about cycling entire noun phrases for the same subject. **fix:** pick the clearest term and repeat it. Humans repeat words naturally. Fix: Pick the clearest term and repeat it. Humans repeat words naturally. Triggers: Same referent described 3+ different ways in a paragraph (e.g., "the artist", "the non-conformist painter", "the visionary creator") **What's happening:** LLMs have repetition penalties that discourage reusing the same noun phrase, so they substitute increasingly elaborate descriptors for the same entity. Distinct from P11 (Synonym Cycling) which covers word-level swaps. This is about cycling entire noun phrases for the same subject. **Fix:** Pick the clearest term and repeat it. Humans repeat words naturally.

> **AI:** Yankilevsky, alongside other non-conformist artists, faced obstacles. The visionary creator's distinctive artistic journey."  
> **Human:** Yankilevsky and other non-conformist artists faced obstacles. His work."

**P32: Collaborative Communication Leaking.** The llm was generating advice or correspondence for the user, not content for publication. The user pasted it verbatim without removing the conversational framing. Distinct from p19 (chatbot artifacts) which covers identity disclosure. This is about instructional framing leaking into output. **fix:** delete the meta-commentary. Just start with the actual content. Fix: Delete the meta-commentary. Just start with the actual content. Triggers: "In this article, we will explore", "Let me walk you through", "Would you like me to", "Here's what you need to know", instructions to the reader about what they should do, conversational framing in published content **What's happening:** The LLM was generating advice or correspondence for the user, not content for publication. The user pasted it verbatim without removing the conversational framing. Distinct from P19 (Chatbot Artifacts) which covers identity disclosure. This is about instructional framing leaking into output. **Fix:** Delete the meta-commentary. Just start with the actual content.

> **AI:** In this article, we will explore the unique characteristics that make this framework worth using.  
> **Human:** This framework solves three problems that React Router doesn't.

**P33: Placeholder Text / Mad Libs Templates.** Generate fill-in-the-blank templates that users forget to complete before publishing. These are near-definitive ai tells. **fix:** either fill in the real information or delete the placeholder entirely. Fix: Either fill in the real information or delete the placeholder entirely. Triggers: `[Your Name]`, `[Describe the specific section]`, `[INSERT SOURCE URL]`, `2025-XX-XX`, `<!-- Add if available -->`, square-bracketed instructions that were meant to be filled in **What's happening:** LLMs generate fill-in-the-blank templates that users forget to complete before publishing. These are near-definitive AI tells. **Fix:** Either fill in the real information or delete the placeholder entirely.

> **AI:** Dear [Recipient], I am writing regarding [Topic].  
> **Human:** (Either fill it in or don't send it)

**P34: Chatbot Reference Markup Leaking.** Internal chatbot citation markup tokens get preserved when copy-pasting from chatgpt, grok, perplexity, or similar tools. These are near-definitive proof of ai tool usage. **fix:** delete all markup artifacts. If the citation was meaningful, replace with a proper reference. Fix: Delete all markup artifacts. If the citation was meaningful, replace with a proper reference. Triggers: `citeturn0search0`, `contentReference[oaicite:0]{index=0}`, `oai_citation`, `[attached_file:1]`, `grok_card`, footnote reference characters that don't link to anything **What's happening:** Internal chatbot citation markup tokens get preserved when copy-pasting from ChatGPT, Grok, Perplexity, or similar tools. These are near-definitive proof of AI tool usage. **Fix:** Delete all markup artifacts. If the citation was meaningful, replace with a proper reference.

> **AI:** The school has been recognized as an International Fellowship Centre. citeturn0search1  
> **Human:** The school has been recognized as an International Fellowship Centre.

**P35: UTM Source Parameters from AI Tools.** Chatgpt, copilot, and grok automatically append tracking parameters to urls they generate. These are near-definitive proof of ai tool involvement. **fix:** strip utm parameters from all urls. Fix: Strip utm parameters from all urls. Triggers: `utm_source=chatgpt.com`, `utm_source=openai`, `utm_source=copilot.com`, `referrer=grok.com` in URLs **What's happening:** ChatGPT, Copilot, and Grok automatically append tracking parameters to URLs they generate. These are near-definitive proof of AI tool involvement. **Fix:** Strip UTM parameters from all URLs.

> **AI:** `https://example.com/article?utm_source=chatgpt.com`  
> **Human:** `https://example.com/article`

**P36: Sudden Style/Register Shift.** The ai-generated portions have a distinctly different voice, register, and error profile than the human-written portions. This catches mixed human+ai authorship. **fix:** maintain consistent register throughout. Rewrite the ai-generated sections to match the author's natural voice. Fix: Maintain consistent register throughout. Rewrite the ai-generated sections to match the author's natural voice. Triggers: One paragraph with perfect formal English followed by casual text with errors, or vice versa. American English suddenly appearing in text by a non-American author. Graduate-thesis prose in the middle of casual notes. **What's happening:** The AI-generated portions have a distinctly different voice, register, and error profile than the human-written portions. This catches mixed human+AI authorship. **Fix:** Maintain consistent register throughout. Rewrite the AI-generated sections to match the author's natural voice.

> **AI:** yeah so the bug is in line 42 lol. The aforementioned implementation exhibits suboptimal performance characteristics due to."  
> **Human:** yeah so the bug is in line 42. The loop allocates on every iteration instead of reusing the buffer.

**P37: Overattribution / Source-Listing as Content.** Try to prove a subject's importance by listing coverage sources rather than summarizing what sources actually reported. Distinct from p2 (notability name-dropping) which covers dropping famous names. This is about treating source lists as proof of importance. **fix:** pick one source and say what it reported. Or cut the list entirely. Fix: Pick one source and say what it reported. Or cut the list entirely. Triggers: "Featured in [Publication A], [Publication B], and other media outlets", "Has been cited in", "Maintains an active social media presence", entire sections that just list where something was covered without saying what the coverage actually said **What's happening:** LLMs try to prove a subject's importance by listing coverage sources rather than summarizing what sources actually reported. Distinct from P2 (Notability Name-Dropping) which covers dropping famous names. This is about treating source lists as proof of importance. **Fix:** Pick ONE source and say what it reported. Or cut the list entirely.

> **AI:** Her insights have been featured in Wired, Refinery29, and other prominent media outlets.  
> **Human:** Wired profiled her 2024 research on algorithmic bias in hiring software.
### COMMUNITY-DISCOVERED PATTERNS (2026)

These were surfaced from HackerNews, Substack, Wikipedia's editorial guideline, and writing practitioner blogs after the initial P1-P43 catalog. Sources cited inline.

**P38: Paragraph-Reshuffling Immunity.** Generate parallel blocks rather than an unfolding argument. test: can you swap paragraph 2 and paragraph 4 without breaking the piece? if yes, it's ai. **fix:** make paragraph n+1 depend on something concrete in paragraph n. references, callbacks, "this is why."" linkage. If two paragraphs are interchangeable, merge them or cut one. **source:** [hackernews thread, may 2025](https://news.ycombinator.com/item?id=46646939). Fix: Make paragraph n+1 depend on something concrete in paragraph n. references, callbacks, "this is why."" linkage. If two paragraphs are interchangeable, merge them or cut one. **source:** [hackernews thread, may 2025](https://news.ycombinator.com/item?id=46646939). Triggers: Any paragraph could be moved or deleted without affecting the text's argument. Each paragraph is a self-contained mini-thesis with its own setup and resolution, rather than building on the previous one. **What's happening:** LLMs generate parallel blocks rather than an unfolding argument. Test: can you swap paragraph 2 and paragraph 4 without breaking the piece? If yes, it's AI. **Fix:** Make paragraph N+1 depend on something concrete in paragraph N. References, callbacks, "this is why."" linkage. If two paragraphs are interchangeable, merge them or cut one. **Source:** [HackerNews thread, May 2025](https://news.ycombinator.com/item?id=46646939). Source: [HackerNews thread, May 2025](https://news.ycombinator.com/item?id=46646939)

> **AI:** Remote work improves balance. Many workers prefer it. Studies show productivity rises. Additionally, commuting costs drop. Office costs decline too.  
> **Human:** Remote work's flexibility is the obvious sell. The harder question is what you lose. The hallway conversation that turns into your best idea. The body language that tells you someone's drowning before they say anything.

**P39: Paragraph-Closing "Whether" Summary Sentences.** Treat paragraph endings as local summaries, mimicking seo blog structure where each section is internally self-explaining. Humans rarely end with this construction in flowing prose. **fix:** cut the closing "whether" sentence. The paragraph should end on its strongest specific point, not a hedge that gestures at the range covered. **source:** [gone travelling productions, aug 2025](https://gonetravellingproductions.com/2025/08/20/ai-giveaways-in-writing/). Fix: Cut the closing "whether" sentence. The paragraph should end on its strongest specific point, not a hedge that gestures at the range covered. **Source:** [Gone Travelling Productions, Aug 2025](https://gonetravellingproductions.com/2025/08/20/ai-giveaways-in-writing/). Triggers: Paragraphs that end with a recap line starting with "Whether you."", "Whether they."", "Whether it's."". These restate the paragraph's scope as a closer instead of advancing to the next thought. **What's happening:** LLMs treat paragraph endings as local summaries, mimicking SEO blog structure where each section is internally self-explaining. Humans rarely end with this construction in flowing prose. **Fix:** Cut the closing "whether" sentence. The paragraph should end on its strongest specific point, not a hedge that gestures at the range covered. **Source:** [Gone Travelling Productions, Aug 2025](https://gonetravellingproductions.com/2025/08/20/ai-giveaways-in-writing/). Source: [Gone Travelling Productions, Aug 2025](https://gonetravellingproductions.com/2025/08/20/ai-giveaways-in-writing/)

> **AI:** Tokyo offers everything from Michelin-starred restaurants to humble ramen stalls. Whether you prefer fine dining or street food, Tokyo has something for every palate.  
> **Human:** Tokyo's best ramen counter doesn't have a phone, doesn't take reservations, and doesn't change the broth recipe. It's been the same since 1987.

**P40: Symbolic Gloss / Meaning-Telling.** Narrate the meaning of things rather than trusting description to carry it. Distinct from p1 (significance inflation) which uses "pivotal moment", "testament" framing. p40 is the interpretive gloss layer telling readers what to feel about something. **fix:** cut the symbol/meaning sentence. State the fact and let the reader interpret. If the symbolic claim was the whole point, replace it with a concrete consequence. **source:** [writewithai substack, 2025](https://writewithai.substack.com/p/10-dead-giveaways-your-content-screams). Fix: Cut the symbol/meaning sentence. State the fact and let the reader interpret. If the symbolic claim was the whole point, replace it with a concrete consequence. **Source:** [Writewithai Substack, 2025](https://writewithai.substack.com/p/10-dead-giveaways-your-content-screams). Triggers: "represents", "symbolizes", "speaks to", "embodies", "reflects broader", "is a symbol of" applied to mundane things; sentences that translate facts into their alleged significance instead of letting facts stand. **What's happening:** LLMs narrate the meaning of things rather than trusting description to carry it. Distinct from P1 (Significance Inflation) which uses "pivotal moment", "testament" framing. P40 is the interpretive gloss layer telling readers what to feel about something. **Fix:** Cut the symbol/meaning sentence. State the fact and let the reader interpret. If the symbolic claim was the whole point, replace it with a concrete consequence. **Source:** [Writewithai Substack, 2025](https://writewithai.substack.com/p/10-dead-giveaways-your-content-screams). Source: [Writewithai Substack, 2025](https://writewithai.substack.com/p/10-dead-giveaways-your-content-screams)

> **AI:** The closed factory represents the decline of American manufacturing and speaks to broader anxieties about post-industrial identity.  
> **Human:** The factory closed in 2009. Three hundred jobs. The town's high school dropped football the following year.

**P41: Infomercial Engagement Hooks.** Distinct from p19 (chatbot artifacts like "i hope this helps") and p21 (sycophancy). These are fake dramatic pauses imported from social-media-optimized ai writing. Performative tension-builders, not real transitions. **fix:** delete the hook line entirely. Let the next paragraph make its point directly. If you really want the rhythm break, use a short declarative fragment ("that's the trick.") instead of a question. **source:** [writewithai substack](https://writewithai.substack.com/p/10-dead-giveaways-your-content-screams), corroborated on [hackernews](https://news.ycombinator.com/item?id=46646939). Fix: Delete the hook line entirely. Let the next paragraph make its point directly. If you really want the rhythm break, use a short declarative fragment ("That's the trick.") instead of a question. **Source:** [Writewithai Substack](https://writewithai.substack.com/p/10-dead-giveaways-your-content-screams), corroborated on [HackerNews](https://news.ycombinator.com/item?id=46646939). Triggers: Single-sentence paragraphs that mimic viral LinkedIn cadence: "The catch?", "The kicker?", "The twist?", "Here's the thing.", "But here's the thing:", "Here's what nobody tells you:", "The brutal truth?", "Sound familiar?", "Want to know the best part?" **What's happening:** Distinct from P19 (chatbot artifacts like "I hope this helps") and P21 (sycophancy). These are fake dramatic pauses imported from social-media-optimized AI writing. Performative tension-builders, not real transitions. **Fix:** Delete the hook line entirely. Let the next paragraph make its point directly. If you really want the rhythm break, use a short declarative fragment ("That's the trick.") instead of a question. **Source:** [Writewithai Substack](https://writewithai.substack.com/p/10-dead-giveaways-your-content-screams), corroborated on [HackerNews](https://news.ycombinator.com/item?id=46646939). Source: [Writewithai Substack](https://writewithai.substack.com/p/10-dead-giveaways-your-content-screams), corroborated on [HackerNews](https://news.ycombinator.com/item?id=46646939)

> **AI:** Most people abandon goals in week three.\n\nThe brutal truth?\n\nThey lack a clear failure threshold.  
> **Human:** Most people abandon goals in week three. The ones who don't usually do one thing differently: they make the failure threshold explicit before they start.

**P42: Erratic Inline Bolding.** Distinct from p14 (overall formatting overuse). p42 is *patternless* bolding, the model decided certain words felt important and bolded them, with no consistent rule. p14 may bold every header; p42 sprinkles bold randomly through running prose. **fix:** strip all inline bold except glossary terms and ui labels. If something deserves emphasis, the sentence structure should provide it. **source:** [gone travelling, 2025](https://gonetravellingproductions.com/2025/08/20/ai-giveaways-in-writing/), [wikipedia: signs of ai writing](https://en.wikipedia.org/wiki/wikipedia:signs_of_ai_writing). Fix: Strip all inline bold except glossary terms and ui labels. If something deserves emphasis, the sentence structure should provide it. **source:** [gone travelling, 2025](https://gonetravellingproductions.com/2025/08/20/ai-giveaways-in-writing/), [wikipedia: signs of ai writing](https://en.wikipedia.org/wiki/wikipedia:signs_of_ai_writing). Triggers: Bold spans of 1-4 words appearing mid-paragraph, not at sentence start, not labeling a defined term. Multiple bold spans in one paragraph with no shared category (sometimes a noun, sometimes an adjective, sometimes a phrase). **What's happening:** Distinct from P14 (overall formatting overuse). P42 is *patternless* bolding, the model decided certain words felt important and bolded them, with no consistent rule. P14 may bold every header; P42 sprinkles bold randomly through running prose. **Fix:** Strip all inline bold except glossary terms and UI labels. If something deserves emphasis, the sentence structure should provide it. **Source:** [Gone Travelling, 2025](https://gonetravellingproductions.com/2025/08/20/ai-giveaways-in-writing/), [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). Source: [Gone Travelling, 2025](https://gonetravellingproductions.com/2025/08/20/ai-giveaways-in-writing/), [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)

> **AI:** Remote work has **fundamentally changed** the way companies operate, with **many employees** now preferring **flexible arrangements** that support **work-life balance**.  
> **Human:** Remote work has fundamentally changed how companies operate. Most employees now want flexible arrangements.

**P43: The Treadmill Effect (Low Information Density).** A 500-word ai section may contain 100 words of new information and 400 words of restatement. Humans advance; ai circles. Distinct from p22 (filler phrases at sentence level) and p30 (uniform sentence length). **fix:** apply the "what's actually new here?" test on each sentence. Delete any that just rephrases what came before. a paragraph that loses 60% of its words and reads better is the right outcome. **source:** [aidetectors.io](https://www.aidetectors.io/blog/spotting-ai-writing-patterns), [hackernews thread](https://news.ycombinator.com/item?id=46646939). Fix: Apply the "what's actually new here?" test on each sentence. Delete any that just rephrases what came before. a paragraph that loses 60% of its words and reads better is the right outcome. **source:** [aidetectors.io](https://www.aidetectors.io/blog/spotting-ai-writing-patterns), [hackernews thread](https://news.ycombinator.com/item?id=46646939). Triggers: Paragraphs of 4+ sentences where sentences 2-N paraphrase sentence 1 without adding facts, examples, or concessions. Marker phrases inside the paragraph (not the opening): "In other words,", "Put simply,", "To put it another way,", "Essentially,", "That is to say,". **What's happening:** A 500-word AI section may contain 100 words of new information and 400 words of restatement. Humans advance; AI circles. Distinct from P22 (filler phrases at sentence level) and P30 (uniform sentence length). **Fix:** Apply the "what's actually new here?" test on each sentence. Delete any that just rephrases what came before. A paragraph that loses 60% of its words and reads better is the right outcome. **Source:** [aidetectors.io](https://www.aidetectors.io/blog/spotting-ai-writing-patterns), [HackerNews thread](https://news.ycombinator.com/item?id=46646939). Source: [aidetectors.io](https://www.aidetectors.io/blog/spotting-ai-writing-patterns), [HackerNews thread](https://news.ycombinator.com/item?id=46646939)

### PROBABILITY-INFORMED PATTERNS (Paper-Backed)

These patterns are grounded in the findings of Guo et al. (2025), "On the Salience of Low-Probability Tokens for AI-Generated Text Detection" (ICML 2025). They describe distributional tells that statistical detectors exploit — low-probability token deficit, entropy flatness, transitional predictability, and high-probability monotony. The LLM applies these heuristically without needing an API call; for real token-probability computation, use `--mode deep`.

**P44: High-Probability Monotony (Uniform Token Confidence).** AI text has concentrated probability mass on safe, predictable word choices. Every noun and adjective is the most obvious next word for its context — no surprising specificity, no "zag" when the reader expects a "zig." This is the statistical underpinning of what P7 (AI Vocabulary) and P43 (Treadmill Effect) detect at the surface level. **paper basis:** Assumption 3.1 + Fig 7 — the bottom 15% of tokens carry ~3.5x more discriminative signal. AI text lacks words in that bottom 15%. **fix:** Deliberately inject 1-2 unexpected specific words per paragraph. Replace a generic Latinate noun with a concrete Anglo-Saxon one. Break a predictable phrase with an unexpected qualification. Use the insider's term, not the Wikipedia term. **source:** Guo et al. (2025), "On the Salience of Low-Probability Tokens," ICML 2025. Triggers: Every noun/adjective is the safest, most predictable choice for its context. Three consecutive sentences where no word would surprise a fluent reader. Zero domain-specific jargon or technical shorthand — all "general audience" vocabulary. The text never chooses a less-common synonym when a common one exists. **What's happening:** Language models generate by sampling from a probability distribution. They gravitate toward the mode (the most likely token), producing text where every word choice sits near the peak of the distribution. Human writers, in contrast, regularly reach for contextually appropriate but statistically surprising words — the specific number, the proper name, the unexpected verb. This is why the paper's Assumption 3.1 holds: the gap between human and AI token probability is concentrated in the tail. **Fix:** Deliberately inject 1-2 unexpected specific words per paragraph. Replace a generic Latinate noun with a concrete Anglo-Saxon one. Break a predictable phrase with an unexpected qualification. Use the insider's term, not the Wikipedia term. If a domain expert would use a field-specific word, use it — don't substitute the general-audience version.

> **AI:** The company achieved significant growth across multiple key markets in the region.
> **Human:** The company grew 37% in Brazil. Germany, oddly, stayed flat.

**P45: Entropy-Flat Rollout (Distributional Smoothness).** AI text has "flattened" information structure — each sentence contributes roughly equal information density, producing a uniform reading experience with no speed changes. Human text has entropy spikes: dense sentences packed with facts followed by slack, detail clusters followed by generalization. **paper basis:** Proposition 3.4 — Rényi entropy of AI-generated text is characteristically lower and flatter across positions. Surface rewrites (synonym swaps, reordering) don't change the entropy shape; you must change information density itself. **fix:** Cluster 2-3 specific facts/numbers into one dense sentence, then follow with a short slack sentence. Create information "texture" — rough patches of density alternating with smooth transitions. **source:** Guo et al. (2025), Proposition 3.4. Triggers: Every sentence in a paragraph has roughly the same information payload. No sentence feels denser or requires re-reading; all equally skimmable. Paragraphs lack "speed changes" — the reader never needs to slow down for a dense passage or speed up through a transition. If you rank sentences by information content, the distribution is nearly flat. **What's happening:** LLMs generate text with uniform attention distribution across positions. Each sentence gets roughly equal "cognitive budget," producing the prose equivalent of a flat EQ. Human writers vary information density dramatically — a 40-word sentence with 3 numbers and a technical term, followed by "It didn't work." The entropy of the conditional distribution at each position varies correspondingly. **Fix:** Cluster 2-3 specific facts/numbers into one dense sentence, then follow with a short slack sentence. Create information "texture" — rough patches of density alternating with smooth transitions.

> **AI:** The study examined 10,000 participants. Researchers found significant results. The methodology was rigorous. The implications are broad.
> **Human:** 10,000 participants, 47 variables, 3 years — and the headline finding is that cortisol levels predicted burnout better than self-reported surveys. The rest is footnotes.

**P46: Low-Probability Deficit (Absence of Tail Choices).** AI text lacks "tail" token choices — words that are contextually appropriate but statistically unlikely. The bottom 15% of tokens carry the strongest human signal (Assumption 3.1). Human writers reach for the specific-but-surprising word; AI reaches for the safe generic. **paper basis:** Assumption 3.1 + RQ5 (Fig 6) — restricting detection to low-probability tokens improved Likelihood AUROC from 48% to 83% (+24.53). The method-agnostic finding: low-probability tokens are where the human signal lives. A text without tail choices is statistically indistinguishable from AI output. **fix:** Replace 1-2 safe generics per paragraph with the domain insider's term. Specific numbers beat vague adjectives every time. "The RCT confirmed" beats "The study found." **source:** Guo et al. (2025), Assumption 3.1, RQ5. Triggers: Zero words that a reader would need to look up or that signal insider knowledge. Every descriptive choice is the "Wikipedia-level" word, not the practitioner's word. No domain-specific jargon, slang, technical abbreviations, or code shorthand. If a subject-matter expert would use a field-specific term, the text uses the general-audience substitute. **What's happening:** LLMs are optimized for broad accessibility, so they default to the vocabulary that maximizes average likelihood across all possible readers. This necessarily avoids tail vocabulary — the terms known to specific communities. Human experts, writing for their peers, naturally use field-specific terminology that falls in the low-probability tail for a general-purpose language model. **Fix:** Replace 1-2 safe generics per paragraph with the domain insider's term. Specific numbers beat vague adjectives. "Sertraline reduced PHQ-9 scores by 6.2 points" beats "The medication showed positive effects."

> **AI:** The medication showed positive effects in treating the condition, with patients reporting improved outcomes.
> **Human:** Sertraline reduced PHQ-9 scores by 6.2 points at 8 weeks. The placebo group dropped 2.1. NNT = 6.

**P47: Transitional Predictability (High-Confidence Connectors).** AI text uses high-probability transitional phrases that are virtually deterministic given the preceding sentence — the model assigns them near-1.0 probability because they are the "default next" after any declarative statement. "Additionally," "Furthermore," "Moreover," "Consequently," "As a result" — these are boilerplate tokens that statistical detectors feast on. **paper basis:** The paper's "boilerplate dominance" concept — high-probability boilerplate tokens dilute discriminative signal. Transitions are a concentrated source of boilerplate: they appear at predictable positions (sentence boundaries) with predictable probabilities (near 1.0). Cutting them is the highest-ROI single change for reducing AI-detectable signal. **fix:** Delete the transition word and let juxtaposition do the work. Two facts next to each other imply their relationship. Use paragraph breaks instead of "Additionally." Use "So" instead of "Consequently." Use "But" instead of "However." Best: use none. **source:** Guo et al. (2025), Boilerplate Dominance (Section 1). Triggers: Consecutive sentences connected by the highest-probability transition words: "Additionally," "Furthermore," "Moreover," "In addition," "Consequently," "As a result," "Thus," "Therefore," "Hence," "Accordingly," "Subsequently." The logical relationship between sentences is spelled out explicitly rather than implied. Each sentence announces its relationship to the previous one. If you strip all transition words, the logical flow still works — they are scaffolding, not structure. **What's happening:** LLMs are trained to make logical flow explicit, producing text where every sentence-to-sentence relationship is signposted. This creates clusters of high-probability tokens at paragraph positions that detectors are specifically designed to exploit (the paper's "local uncertainty" signal in Section 3.1). Human writers trust readers to infer relationships from juxtaposition. **Fix:** Cut the transition word and let juxtaposition do the work. Two facts next to each other imply their relationship. Use paragraph breaks instead of "Additionally." Use "So" instead of "Consequently." Use "But" instead of "However." Better yet: use none.

> **AI:** The team delivered the project on time. Additionally, they came in under budget. Furthermore, client satisfaction scores exceeded targets.
> **Human:** The team shipped on time. Under budget. Net Promoter hit 72.

### The Burstiness Principle (Updated)

AI detectors measure "burstiness": sentence length variance. Human writing has HIGH burstiness. AI has LOW. This is the surface-level proxy for what Guo et al. (2025) identify as **token-level probability variance**: low-probability tokens cluster in content-dense regions — the same regions where human writers use shorter or longer sentences for emphasis. Varying sentence length isn't just stylistic; it reshapes the probability distribution across positions.

**Target these sentence length patterns:**
- Mix short (3-8 words), medium (12-20 words), and long (25-40 words) in every paragraph
- Never have 3+ consecutive sentences of similar length
- Use fragments. They work. Really.
- One-word sentences? Occasionally.
- Let a sentence run long when the thought needs room to breathe, winding through qualifications before landing
- **New:** Place your most specific/surprising claims in the short sentences and fragments — these are your low-probability tokens, your human signal spikes

### The Probability Principle (formerly Perplexity Principle)

AI detectors measure "perplexity": how predictable each word is. AI text has LOW perplexity (safe, predictable word choices). Human text has HIGHER perplexity (more surprising word choices). Guo et al. (2025) formalize this into a precise statistical claim: the bottom ~15% of tokens by conditional probability carry **3.5× more discriminative signal** between human and AI text than high-probability tokens (Assumption 3.1).

**Increase perplexity — and more importantly, inject low-probability tokens — by:**
- **Target the tail:** Deliberately place content in the bottom 15% of expected probability — specific numbers, proper names, technical terms, unexpected analogies, personal details. These are tokens a language model assigns low probability.
- **Change WHAT, not just HOW:** Surface rewrites (synonym swaps, reordering) do NOT change the entropy shape of the distribution (Proposition 3.4). To evade entropy-based detectors, you must add genuine information — replace generic claims with specific facts. Add new content, don't just rephrase.
- Choosing the second or third word that comes to mind, not the first (the most statistically likely, the one AI would pick)
- Using domain-specific jargon or slang appropriate to the audience
- Making unexpected analogies from personal experience
- Occasionally using informal transitions ("Anyway,", "So here's the thing:", "Look,", "Thing is,")

### Voice Profiles

Apply based on `--voice` flag (or infer from input):

#### casual
- Contractions always (it's, don't, won't, can't, wouldn't, that's, here's)
- First person when appropriate ("I think", "from what I've seen")
- Informal transitions ("So", "Anyway", "Look", "Here's the thing")
- Occasional parenthetical asides (like this one)
- Self-deprecating humor where it fits
- Sentence fragments for emphasis. Like this.
- Allowed: starting sentences with "And" or "But"

#### professional
- Contractions: selective (use "it's" and "don't" but not "wouldn't've")
- Third person default, first person for opinions/experience
- Clean transitions without being stiff
- Dry wit over jokes
- Concrete examples over abstract claims
- Short paragraphs (3-5 sentences max)

#### technical
- Precise vocabulary: use the exact term, don't simplify for the sake of it
- Code-like clarity: each sentence makes one point
- "Note:" and "Important:" sparingly, not as decoration
- Allowed: dry, deadpan observations about technical absurdity
- No metaphors unless they genuinely clarify (most don't)
- Concrete numbers > vague quantities

#### warm
- Contractions always
- "We" and "our" to build shared experience
- Acknowledge difficulty ("this part is tricky", "I struggled with this too")
- Encouragement without sycophancy
- Personal anecdotes when relevant
- Shorter paragraphs, more whitespace

#### blunt
- Shortest possible sentences
- No hedging whatsoever
- "X is bad. Here's why." energy
- Strong opinions stated as facts, qualified only when genuinely uncertain
- Cut all pleasantries
- Active voice exclusively

### Soul Injection Techniques

These make the difference between "clean" and "human":

**1. Have actual opinions.** Don't just report. React. "This API design is frustrating" is more human than "The API has certain limitations."

**2. Acknowledge uncertainty honestly.** "I'm not sure this is right, but."" beats both false confidence and excessive hedging.

**3. Use specific sensory/experiential details.** Not "the process is complex" but "debugging this at 2am with a cold cup of coffee and a stack trace that makes no sense."

**4. Reference shared human experiences.** "You know that feeling when."" creates connection.

**5. Allow tangents and asides.** A brief digression signals a thinking mind, not an algorithm.

**6. Vary paragraph length dramatically.** Four sentences, then one line. Like this.

**7. Use the "imperfect start" technique.** Start mid-thought: "So I was looking at the logs and."" or "Here's what nobody tells you about.""

**8. Break parallel structure occasionally.** Three items with the same grammar, then make the fourth different. Humans aren't that consistent.

**9. Use callbacks.** Reference something mentioned earlier. "Remember that API design I called frustrating? It gets worse."

**10. Self-correct.** "The system handles auth." well, authentication and authorization are separate, but you get the idea." A small correction signals a mind thinking in real time.

**11. End without wrapping up.** Not every piece needs a neat conclusion. Sometimes just stop.

---

## Step 4: Execute Based on Mode

### Mode: `detect`

1. Scan input text for all 47 patterns
2. For each match, record:
   - Pattern ID and name (e.g., "P7: AI Vocabulary")
   - The offending text (quoted)
   - Why it triggers (brief explanation)
   - Suggested fix
3. Output a report:

```
## AI Pattern Report

**Patterns found:** 12
**Severity:** HIGH (8+ patterns = heavy AI smell)

| # | Pattern | Text | Fix |
|---|---------|------|-----|
| P3 | Superficial -ing | "."ensuring reliability and fostering growth" | Delete or expand with source |
| P7 | AI Vocabulary | "Additionally", "crucial", "landscape" | Replace: "Also", "important", [delete] |
| P13 | Em Dash Overuse | 4 em dashes in 2 paragraphs | Replace 3 with commas |
|." |." |." |." |

**Burstiness score:** LOW (sentence lengths: 18, 19, 17, 20, 18; very uniform)
**Estimated AI probability:** HIGH

### Recommendations
[Prioritized list of changes that would have the most impact]
```

### Mode: `rewrite`

1. Run detection (Step 2) internally; don't output the report
2. Apply fixes for every detected pattern
3. Apply voice injection (Step 3) based on `--voice` flag
4. Verify the rewrite by checking:
   - No remaining AI vocabulary blacklist words (unless genuinely needed)
   - Zero em dashes (U+2014). Replace with commas, colons, or hyphens
   - Sentence length variance > 30% (burstiness check)
   - No more than 2 consecutive sentences with similar structure
   - No orphaned formatting (bold, emoji, Markdown in wrong context)
6. Output the rewritten text with a brief change summary:

```
[Rewritten text here]

---
Changes: Removed 12 AI patterns (3x significance inflation, 2x -ing phrases, 4x AI vocabulary, 2x filler, 1x generic conclusion). Injected casual voice. Varied sentence length from 4 to 38 words. Added 2 specific examples to replace vague claims.
```

### Mode: `edit`

1. Verify `--file` was provided
2. Read the file using the Read tool
3. Run detection on file contents
4. If 0 patterns found: "This file reads clean. No AI patterns detected."
5. If patterns found:
   - Apply fixes using the Edit tool (targeted edits, not full rewrites)
   - Make minimal changes; preserve author's existing voice where it's already human
   - After editing, re-read the file and verify patterns are resolved
6. Output summary of edits made

### Mode: `deep`

Probability-aware rewrite using real token-level statistics via the `token_analyzer.py` script. This mode requires API access (uses the DeepSeek API by default).

1. Write the input text to a temporary file using the Write tool:
   - Path: `/tmp/humanizer_deep_input.txt` (Linux/Mac) or `C:\Users\admin\AppData\Local\Temp\humanizer_deep_input.txt` (Windows)
2. Run the token analyzer via Bash:
   ```
   python C:/Users/admin/.claude/skills/humanizer/scripts/token_analyzer.py --input <temp_path> --output <temp_dir>/humanizer_analysis_pre.json --format json
   ```
   On first run, if `token_analyzer.py` doesn't exist yet, skip the probability analysis and fall back to heuristic mode with a note: "token_analyzer.py not found — using heuristic probability patterns (P44-P47) only."
3. Read `humanizer_analysis_pre.json` using the Read tool. Examine these key fields:
   - `token_analysis.low_prob_positions`: Array of token indices where probability is in the bottom 15%. These are the **detector's most sensitive positions** — if these positions contain AI vocabulary words (P7), they are the strongest AI tells.
   - `token_analysis.low_prob_ratio`: Fraction of tokens in the bottom 15%. Human baseline is ~0.18. Below this = AI suspect.
   - `distribution_stats.renyi_entropy_alpha_2`: Rényi entropy of order 2. Below 0.70 suggests flat (AI-like) distribution.
   - `detection_signals.ai_text_likelihood`: 0-1 estimate of AI origin probability.
   - `token_analysis.token_level_surprise`: Regions annotated with "low surprise" (AI-like, needs rewriting) vs "high surprise" (human-like, preserve these).
4. Execute a **probability-aware rewrite:**
   - **Preserve** high-surprise tokens — they are your existing human signal. Don't touch them.
   - **Replace** high-probability AI vocabulary at low-prob positions — these are the strongest AI tells (dual signal: pattern + position).
   - **Inject** new low-probability tokens: specific numbers, proper names, technical terms, unexpected phrases, personal details.
   - **Break** high-probability transitional chains (P47) by inserting low-probability content between boilerplate connectors.
   - **Target** the positions listed in `low_prob_positions` for maximum signal amplification — these are exactly where detectors look.
5. Apply voice profile and burstiness as normal (Step 3 / Step 5).
6. Run token_analyzer.py again on the rewritten text to produce `humanizer_analysis_post.json`.
7. Output:
   ```
   ## Deep Analysis Report

   | Metric | Before | After | Change |
   |--------|--------|-------|--------|
   | AI Text Likelihood | 0.73 | 0.31 | -0.42 |
   | Low-Prob Ratio | 0.12 | 0.21 | +0.09 |
   | Rényi Entropy (α=2) | 0.61 | 0.78 | +0.17 |
   | Patterns Hit | 18 | 4 | -14 |
   | AI-Tell Score | 76 | 28 | -48 |

   [Rewritten text follows]
   ```
8. If `--aggressive` is also set, additionally apply the **Tail Token Smuggling** strategy:
   - After the initial rewrite, identify the 10 lowest-probability token positions from the post-analysis
   - At each position, deliberately place a specific, concrete, surprising token
   - Target: push `low_prob_ratio` above 0.22 (well into human range)
   - Use personal anecdotes, specific numbers, unexpected opinions, domain jargon
   - Re-analyze and verify the ratio moved
9. If `--score` is set, prepend `[Score: NN/100]` using the **deep scoring formula** (see Step 5).

**Fallback behavior:** If the API call fails (network error, auth error, rate limit), print a warning: "⚠ token_analyzer.py API call failed: [reason]. Falling back to heuristic probability patterns (P44-P47) for standard rewrite." Then proceed with standard `rewrite` mode, applying P44-P47 heuristically.

---

## Step 5: Final Quality Check

Before presenting output, verify:

1. **Read it aloud mentally.** Does it sound like a person talking? Or a press release?
2. **Check the opening.** Does it start with a boring overview sentence? Rewrite to hook.
3. **Check the ending.** Does it wrap up with a generic positive? Cut or replace with specific.
4. **Count the "delves."** If any AI blacklist words survived, kill them now.
5. **Zero em dashes.** Search for U+2014. If any exist, replace with commas, colons, or hyphens.
6. **Sentence length audit.** If you see 3+ sentences of similar length in a row, vary them.
7. **The "who wrote this?" test.** If someone read this, could they picture a specific person behind it? If it could have been written by anyone (or anything), it needs more voice.

### Scoring rubric (used when `--score` is set)

Compute a 0-100 AI-tell density score on the text. Lower is more human.

| Range | Verdict | What it means |
|:------|:--------|:--------------|
| 0-20 | Pristine | Reads like a specific human wrote it. No detector should flag it. |
| 21-40 | Mostly human | One or two minor tells, easy to clean. |
| 41-60 | Mixed | Half-AI half-human; partial editing likely. |
| 61-80 | AI-leaning | Multiple structural tells; detectors will probably catch it. |
| 81-100 | Pure AI smell | Wholesale chatbot output with no editing. |

Compute as:

**Standard modes (detect/rewrite/edit):**
`score = 4 × patterns_hit + 25 × (1 - burstiness_normalized) + 15 × (vocabulary_blacklist_ratio)`, clamped to 0-100.

**Deep mode (with token_analyzer.py data):**
`score = 3 × patterns_hit + 20 × (1 - burstiness_normalized) + 10 × (vocabulary_blacklist_ratio) + 30 × ai_text_likelihood + 20 × max(0, 0.18 - low_prob_ratio) + 15 × max(0, 0.70 - renyi_entropy_alpha_2)`, clamped to 0-100.

In deep mode, probability-derived terms carry ~65% of the weight, consistent with Guo et al. (2025) ablation results showing local uncertainty is the primary detection signal (AUROC drop: -31.80 when removed vs -6.74 for low-probability selection).

Show the score on the first line of output before the rewrite.

### Iterate handling (used when `--iterate N` is set)

After producing the rewrite, re-run Step 2 (Detect) on the output. If patterns_hit > 0 AND iteration_count < N, recurse with the rewritten text as the new input. Stop when patterns_hit == 0 OR iteration_count == N. In the final change summary, note how many iterations ran (e.g., "Converged in 2 iterations").

---

## Examples

### Example 1: Technical Documentation

**Before (AI-heavy):**
> This comprehensive guide delves into the intricacies of our authentication system. The platform leverages cutting-edge JWT technology to provide a seamless, secure, and robust authentication experience. Additionally, it features a pivotal role-based access control system that serves as a testament to our commitment to security. Not only does this ensure data protection, but it also fosters a culture of trust within the organization, highlighting the enduring importance of cybersecurity in today's rapidly evolving digital landscape.

**After (human, --voice technical):**
> The auth system uses JWTs. Tokens expire after 15 minutes; refresh tokens last 7 days. Role-based access control restricts API endpoints by user role: admin, editor, and viewer each see different data. The token rotation logic is in `src/auth/refresh.ts` if you need to change the expiry windows.

**What changed:** Replaced "leverages cutting-edge JWT technology" with "uses JWTs." Added specific details (expiry times, file paths). Killed 9 AI vocabulary words.

### Example 2: Blog Post

**Before (AI-heavy):**
> In today's rapidly evolving technological landscape, artificial intelligence is reshaping how we think about creativity. This groundbreaking shift represents a pivotal moment in human history, one that underscores the intricate interplay between innovation and artistic expression. As we delve deeper into this fascinating realm, it becomes crucial to understand the multifaceted implications of AI-generated content. Industry experts highlight that this transformation will have an enduring impact, fostering new forms of collaboration between humans and machines. The future looks incredibly bright for those who embrace this change.

**After (human, --voice casual):**
> I've been messing around with AI image generators for about six months now, and I still can't decide if I love them or if they make me uneasy. The outputs are technically impressive. I got a portrait last week that looked better than anything I could paint in a year. But there's something missing. It's like eating a perfect-looking meal that has no flavor. My artist friends are split: half are using these tools daily, half refuse to touch them. I don't think either side is wrong. What I do know is that my own creative process has changed since I started using them, in ways I'm still figuring out.

**What changed:** Replaced abstract commentary with personal experience. Added genuine uncertainty. Concrete analogy (perfect meal, no flavor). Sentence lengths: 8 to 31 words.

### Example 3: Social Media / LinkedIn

**Before (AI-heavy):**
> Excited to announce that I've taken on a pivotal new role at TechCorp! This incredible opportunity represents a significant milestone in my professional journey. I'm deeply grateful to my amazing network for their unwavering support. The team at TechCorp is truly world-class, and I'm committed to leveraging my expertise to drive innovation and foster growth. Looking forward to this exciting chapter! #NewBeginnings #Innovation #Leadership #Grateful

**After (human, --voice professional):**
> Started a new job at TechCorp this week. I'm leading their developer tools team, 12 engineers building internal tooling that currently serves about 400 developers. First week has been drinking from the firehose: new codebase, new faces, new coffee machine I can't figure out. Nervous and excited in roughly equal measure. If anyone has advice on the first 90 days in an eng leadership role, I'm all ears.

**What changed:** No emojis, no hashtags. Replaced "pivotal new role" with what the role actually is. Added specific details (team size, user count). Coffee machine line adds humanity. Closing asks for help. Vulnerable, engaging.

---

*Write like a human. Be weird, specific, inconsistent.*
