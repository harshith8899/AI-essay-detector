# Data

**This is a development-only, synthetic dataset. None of it is scientifically
validated, and none of it should be presented as evidence that the detector
works on real essays.** It exists purely so the Phase 3/4 pipeline
(dataset loading -> feature extraction -> training -> integration test) has
something to run end-to-end.

## Contents

| Category | Count | Location |
|---|---|---|
| Human | 16 | `human_essays/` |
| AI | 16 | `ai_essays/` |
| Polished | 12 | `polished_essays/` |

## Where this data actually came from

**Every essay in this dataset was hand-written by the coding assistant
(Claude) in a single offline authoring session, at the user's explicit
request, as placeholder content.** No essay in this directory is:

- a real applicant's admissions essay,
- scraped or sourced from any external dataset, or
- the output of an actual call to an LLM API (no API is configured in this
  project; see below).

This matters because the project's standing rule is that LLMs may only be
used *offline* to help build the dataset, never at request time to judge an
essay. The dataset-authoring step above is exactly that kind of offline use
— but it means the "ai_essays" are not empirical samples of what a real
LLM produces; they are the assistant's imitation of typical AI-essay prose
(heavy on cliches, transition-word sentence openers, and generic uplifting
language), written specifically so `stylometry.py`'s cliche/transition
detectors would have something real to find in the pipeline.

- **Human essays** (`human_essays/`): Manually authored short personal
  narratives, each covering a distinct topic (see each essay's `.json`
  sidecar for its `topic` field). Written in a deliberately casual,
  imperfect, contraction-heavy voice.
- **AI essays** (`ai_essays/`): Manually authored to imitate generic
  AI-generated admissions-essay prose. Each has a `.json` sidecar recording
  `model: "development-placeholder"` and the (fictional) prompt it's meant
  to represent — no external model was actually called.
- **Polished essays** (`polished_essays/`): 12 of the 16 human essays,
  hand-rewritten in a more embellished, uniform, "AI-polished" register
  while preserving the original story and facts — a stand-in for what
  `scripts/generate_polished.py` will produce once a real API is
  configured. Each has a `.json` sidecar (`source_human_essay`, `model:
  "development-placeholder-manual-edit"`, `prompt`, `generated_at`) and a
  `.diff.json` sentence-level diff against its source human essay,
  computed with `difflib.SequenceMatcher` over spaCy sentence
  segmentation (see `sentence_diff()` in `generate_polished.py`).

Polished essays are **not** labeled 0/1 for the binary classifier — they
represent a mixed/realistic case (human content, machine-adjusted
phrasing), not a clean example of either class. `train_classifier.py` holds
them out entirely from training/testing and only reports, as a reference,
how the trained models happen to score them.

## Generating a real dataset later

- `backend/scripts/generate_polished.py` is the real pipeline for
  producing polished essays: it requires `ANTHROPIC_API_KEY` or
  `OPENAI_API_KEY` to be set and fails loudly with instructions if neither
  is configured. Its actual provider call is intentionally left
  unimplemented (`_polish_with_anthropic` / `_polish_with_openai` both
  raise `NotImplementedError`) until a real integration is wired up — it
  will never silently fall back to fabricating a "polished" essay locally.
- There is currently no equivalent script for generating real AI essays
  from an LLM; `generate_polished.py`'s provider-dispatch pattern
  (environment-variable-gated, fails clearly if unconfigured) should be
  followed for that when it's built.
- Real human essays still need to be sourced and documented here
  (provenance, consent/licensing, topics covered) before they replace this
  placeholder set.

## Topics represented

Personal narrative topics only: family/mentorship (grandparents, siblings,
parents), extracurriculars (debate, robotics, cross country, chess,
guitar), part-time jobs (restaurant, bookstore), volunteering (animal
shelter, community garden), immigration/language, and a small coding
project. The AI-essay set covers a parallel but broader list of generic
"admissions essay" topics (leadership, resilience, cultural identity,
STEM passion, global citizenship, entrepreneurship, social justice, etc.).

## Topics NOT represented

- STEM-heavy technical/research essays written by humans (only one, `human_014`,
  touches an internship; there's no human equivalent of `ai_008`'s research-project essay)
- Essays on trauma, family loss, mental health, or other sensitive topics
- Non-US application contexts (UK/Common App personal statements, supplemental
  "why this school" essays, scholarship-specific prompts)
- Essays outside the ~120-220 word range (this set has no long-form essays
  near the typical 500-650 word Common App length)
- Any non-English essays
- Essays revised by a human editor (as opposed to polished by an LLM)

## Known limitations

- **Tiny sample size** (44 essays total, 32 for binary training). Any
  metrics reported by `train_classifier.py` are a pipeline sanity check,
  not evidence of real-world accuracy, and are explicitly labeled as such
  in that script's output.
- **The AI-vs-human separation is partly an authoring artifact.** The AI
  essays were deliberately written with heavy cliche/transition-word usage
  to exercise `stylometry.py`'s detectors, so `cliche_count` and
  `transition_opener_rate` separate the two classes almost perfectly on
  this dataset — a real adversarial AI essay wouldn't be this
  cooperative. `mean_perplexity`/`burstiness` (genuine GPT-2 signal, not
  hand-injected) also separate the classes, which is a more meaningful
  result, but still on a tiny, non-adversarial sample.
- **Single author, single sitting.** All essays were written by the same
  assistant in one session, so cross-essay stylistic variance is narrower
  than a real corpus from many different writers.
- **No topic overlap control.** Human and AI essay topics are similar but
  not paired 1:1 on the same prompt, so some of the measured difference
  could reflect topic rather than authorship.

**Bottom line: treat every number this dataset produces as "does the
pipeline run end-to-end," not "does the detector work."**
