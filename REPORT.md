# Evaluation Report

**All numbers in this report come from `backend/scripts/evaluate.py`, run against the development dataset in `data/`. Nothing here is fabricated or rounded up for presentation — see the raw run captured alongside this report's authoring. Every result in this document is a DEVELOPMENT DATASET RESULT, not a measurement of real-world accuracy.**

## 1. Executive Summary

The full pipeline (GPT-2 instrument → stylometric extractor → 61-feature vector → scaler → Logistic Regression) achieves perfect separation (accuracy/precision/recall/F1 = 1.000) on an 8-essay held-out development test set. An ablation experiment that removes the three features most directly tied to how the AI-example essays were authored (`cliche_count`, `cliche_rate`, `transition_opener_rate`) produces **no drop** in test-set performance, meaning the classifier is not relying solely on those crude keyword-style features. However, this result should not be read as evidence of real-world accuracy: the entire dataset (all 44 essays, both classes) was hand-authored by a single assistant in one session, so any residual separability — including the ablation model's continued strong performance, driven substantially by function-word patterns — may still reflect that single-author artifact rather than a generalizable human-vs-AI signal. Polished essays (human content, lightly LLM-style-edited) score low on average (mean 8.0/100), correctly not resembling clean AI examples. No controlled ESL-authored evaluation exists, and this is documented as an open gap rather than papered over.

## 2. Dataset

| Category | Count |
|---|---|
| Human | 16 |
| AI | 16 |
| Polished | 12 |
| **Total** | **44** |

**The current dataset is a development dataset, not a representative corpus of college admissions essays.**

- **Provenance / authorship**: every essay was hand-written by the coding assistant (Claude) in a single offline authoring session, at the user's explicit request, as placeholder content. None are real applicants' essays. None were produced by calling an external LLM API (no API is configured in this project) — the "AI" essays are the assistant's hand-written imitation of generic AI-generated admissions-essay prose, not an empirical sample of actual model output.
- **Generation method (AI essays)**: manually authored with deliberately heavy cliché usage (`delve into`, `plays a pivotal role`, `testament to`, etc.) and transition-word sentence openers (`Moreover`, `Furthermore`, `Additionally`, `In conclusion`), specifically so the stylometry detectors would have real matches to find.
- **Polishing method**: 12 of the 16 human essays were hand-rewritten in a more embellished, uniform register (a stand-in for what `scripts/generate_polished.py` will produce once a real API is configured), preserving the original story/facts. A sentence-level diff against each source is saved alongside.
- **Topic diversity**: personal-narrative topics only (family/mentorship, extracurriculars, part-time jobs, volunteering, immigration, a small coding project for the human set; a broader but still generic list — leadership, resilience, cultural identity, STEM passion, global citizenship, entrepreneurship, social justice, etc. — for the AI set).
- **Missing populations**: no ESL-authored essays, no essays on trauma/mental health/sensitive topics, no non-US application formats, no essays outside the ~120–220 word range, no non-English essays, no essays revised by a human editor (only LLM-style polish).
- **Known authoring artifacts**: single author for both classes in one sitting (narrower stylistic variance than a real multi-author corpus); AI essays deliberately cliché/transition-heavy; no topic-pairing control between human and AI essays on the same prompt.

Full detail: [`data/README.md`](data/README.md).

## 3. Experimental Setup

- Features: 61 total — `mean_perplexity`, `burstiness` (GPT-2), 9 stylometric aggregates, and the fixed 50-word function-word frequency profile. See §9 for the full feature table.
- Split: essay-level (each row is already one whole essay, so no sentence ever crosses the train/test boundary), stratified, `test_size=0.25`, `random_state=42`. Human+AI only (32 essays) — polished essays (12) are held out entirely from training/testing and evaluated separately (§6).
- Train size: 24. Test size: 8 (4 human, 4 AI).
- Models: Logistic Regression (features standardized via `StandardScaler` fit on train only) and, for the ablation experiment, a second Logistic Regression trained the same way on a reduced feature set.

## 4. Development Test Results

**Full model (Logistic Regression, 61 features, currently deployed as `backend/app/models/model.pkl`):**

| Metric | Value |
|---|---|
| Accuracy | 1.000 |
| Precision | 1.000 |
| Recall | 1.000 |
| F1 | 1.000 |

Confusion matrix (rows = actual [human, ai], cols = predicted):

```
[[4 0]
 [0 4]]
```

n_test = 8. This is a perfect score on a tiny, single-author, artifact-laden test set — see §10 for why this must not be read as real-world accuracy.

## 5. Ablation Experiment

Removed features: `cliche_count`, `cliche_rate`, `transition_opener_rate` (the three features most directly shaped by how the AI examples were deliberately authored). 58 features remain.

| Metric | Full model (61 features) | Ablation model (58 features) |
|---|---:|---:|
| Accuracy | 1.000 | 1.000 |
| Precision | 1.000 | 1.000 |
| Recall | 1.000 | 1.000 |
| F1 | 1.000 | 1.000 |

**F1 changed by 0.000.** Performance did not drop when the cliché/transition features were removed — the classes remain fully separable on the *remaining* 58 features alone.

Ablation model — top 10 features by |coefficient|:

| Feature | Coefficient |
|---|---:|
| `fw_into` | +0.3879 |
| `fw_have` | +0.3731 |
| `fw_has` | +0.3366 |
| `fw_is` | +0.3360 |
| `sentence_length_std` | −0.3142 |
| `sentence_length_mean` | −0.3007 |
| `fw_I` | −0.2989 |
| `fw_before` | −0.2788 |
| `fw_to` | +0.2764 |
| `fw_because` | −0.2540 |

**Honest interpretation — this is not a clean win.** The ablation result does show the model isn't relying *solely* on the crudest keyword-style features (cliché phrase matching, transition-word openers) — it retains signal from perplexity, sentence-rhythm, and function-word patterns, which is the more interesting and defensible kind of signal this project set out to measure. **But** the dataset was written by a single author (the assistant) deliberately switching between two registers, so the function-word patterns the ablation model leans on (`into`, `have`, `has`, `is`, sentence-length uniformity) may just as easily reflect *that author's* consistent stylistic choices when writing "AI-style" versus "human-style" prose, rather than a signal that would generalize to real AI-generated text from an actual language model, or to a different human author's writing. The ablation experiment rules out one specific failure mode (over-reliance on literal cliché keywords) but does **not** establish that the model would perform this well on a real, independently-sourced corpus.

## 6. Polished Essay Results

Polished essays have **no clean binary ground truth** — they are human-written content that has been lightly LLM-style-edited (human → LLM polish → mixed human/machine prose), so they are evaluated as a reference distribution only, never as "should be predicted human" or "should be predicted AI."

| Statistic | Value |
|---|---|
| n | 12 |
| Mean score | 8.0 / 100 |
| Min score | 1.5 / 100 (`polished_006`) |
| Max score | 35.1 / 100 (`polished_004`) |

Full distribution:

| essay_id | score |
|---|---:|
| polished_001 | 12.8 |
| polished_002 | 4.4 |
| polished_003 | 7.2 |
| polished_004 | 35.1 |
| polished_005 | 1.6 |
| polished_006 | 1.5 |
| polished_007 | 6.9 |
| polished_008 | 2.1 |
| polished_009 | 1.7 |
| polished_010 | 6.2 |
| polished_011 | 1.5 |
| polished_012 | 15.3 |

**Qualitative observations:**
- Every polished essay scored well below the 50-point midpoint, i.e. none were mistaken for clean AI examples — appropriate, since their underlying content is genuinely human.
- The highest-scoring polished essay, `polished_004` (35.1/100), earns its elevated score primarily from one sentence — *"This experience has been a testament to the transformative power of compassion."* — whose top evidence signal is the detected cliché **"testament to"**, introduced during the hand-polishing pass. This is a good illustration of the sentence-level evidence engine working as intended: the elevated signal traces to a specific, inspectable phrase, not an opaque overall judgment.
- The lowest-scoring polished essay, `polished_006` (1.5/100), shows no cliché or transition-opener matches; its highest-signal sentence (*"I still do not particularly enjoy washing dishes."*) is flagged only for unremarkable sentence-length rhythm — i.e., there was no strong signal to find, correctly reflected in a very low score.
- Polished essays are not equivalent to fully AI-generated essays: they retain a real human author's underlying story, structure, and most word choices, with only a subset of sentences touched by the polishing pass. The scoring pattern above (low overall scores, occasional spikes tied to specific inserted phrases) is consistent with that mixed nature.

## 7. Confident / Interesting Failure Cases

**Genuine misclassifications on the held-out test set: 0 (out of 8), for both the full model and the ablation model.**

The development test set is too small (8 essays) to provide three genuine failures, and manufacturing any would misrepresent the result. Instead, per the evaluation protocol, the most informative available cases are the **least-confident correct predictions** (closest to the 50-point decision boundary) from the full-model test set:

| essay_id | true category | predicted | score | mean_perplexity | burstiness | cliche_count | transition_opener_rate | sentence_length_std |
|---|---|---|---:|---:|---:|---:|---:|---:|
| human_007 | human | human | 6.6/100 | 54.0 | 18.9 | 0 | 0.00 | 8.4 |
| human_013 | human | human | 5.6/100 | 57.5 | 20.4 | 0 | 0.00 | 10.5 |
| human_004 | human | human | 2.3/100 | 30.5 | 15.1 | 0 | 0.00 | 5.3 |

**Grounded explanation, not "the model got confused":** all three are still confidently classified correct — the nearest any test-set prediction came to the decision boundary was 5.6 points away from it (5.6/100, versus a 50/100 threshold). `human_007` and `human_013` are the two human essays with the *highest* GPT-2 perplexity/burstiness in the test set (54.0/18.9 and 57.5/20.4 respectively) among the human examples, which pulls their score up relative to other human essays but nowhere close to the AI class. This indicates the dataset, as constructed, does not currently contain any genuinely ambiguous cases for this model — itself a limitation worth naming: an 8-essay test set with zero near-misses is more evidence that the dataset is too small/easy than evidence that the detector is highly accurate.

## 8. ESL / Fairness Assessment

**ESL fairness evaluation: NOT YET ESTABLISHED.**

No controlled ESL-authored evaluation subset currently exists in this dataset, so no quantitative ESL false-positive comparison can be honestly reported here. This is a significant, openly documented gap: GPT-2 perplexity and several stylometric features (sentence length variance, function-word frequency, lexical diversity) are all plausibly sensitive to non-native English writing patterns in ways that could produce a systematically higher false-positive rate for ESL writers — a well-known failure mode of AI-text detectors generally. Before any fairness claim can be made, future evaluation must include human-written essays from writers who learned English as a second language, evaluated separately from the current dataset.

## 9. Feature Analysis

| Feature | Type | Purpose |
|---|---|---|
| `mean_perplexity` | LM (GPT-2 instrument) | Average GPT-2 perplexity across sentences — lower means the essay's wording is more "predictable" under GPT-2 |
| `burstiness` | LM (GPT-2 instrument) | Population standard deviation of sentence-level perplexity — captures rhythm/variability across the essay |
| `sentence_length_mean` | Stylometric | Average sentence length in spaCy tokens |
| `sentence_length_std` | Stylometric | Population standard deviation of sentence length — a second, independent burstiness-like signal |
| `type_token_ratio` | Stylometric | Lexical diversity: unique lowercase lexical word types ÷ total lexical word tokens |
| `hapax_rate` | Stylometric | Proportion of lexical word types occurring exactly once (hapax legomena) |
| `pos_bigram_entropy` | Stylometric | Shannon entropy (bits) of adjacent POS-tag bigrams across the essay |
| `function_word_rate` | Stylometric | Total rate of the 50 curated function words, per 1000 lexical tokens |
| `fw_<word>` (× 50) | Stylometric | Per-word frequency for each of the 50 fixed function words, per 1000 lexical tokens |
| `cliche_count` | Stylometric | Count of curated cliché-phrase matches in the essay |
| `cliche_rate` | Stylometric | Cliché matches per 1000 lexical tokens |
| `transition_opener_rate` | Stylometric | Fraction of sentences opening with a curated transition phrase (Moreover, Furthermore, Additionally, In conclusion) |

**GPT-2 is used only as a statistical instrument.** It never receives a prompt asking whether the essay is AI-generated, and it never renders a verdict — it only produces token log-probabilities, from which `mean_perplexity` and `burstiness` are computed in our own code (`backend/app/lm_features.py`). All 61 numbers above feed a single scikit-learn Logistic Regression (`backend/app/scoring.py`, `backend/scripts/train_classifier.py`) that makes the actual classification decision.

## 10. Limitations

1. **Tiny dataset.** 44 hand-authored essays total (32 for binary train/test). No statistical claim here generalizes beyond "the pipeline runs and separates this specific, small, single-author dataset."
2. **Authoring artifacts.** All essays were written by one author (the assistant) in one sitting; the AI examples were deliberately cliché/transition-heavy. The ablation experiment (§5) shows the model doesn't depend *solely* on those specific features, but cannot rule out a deeper single-author stylistic confound.
3. **Topic limitations.** Personal-narrative admissions-essay topics only; no STEM-heavy research essays, sensitive topics, non-US formats, or long-form (~500–650 word) essays. See §2.
4. **No controlled ESL evaluation.** Documented as an open gap (§8), not evaluated.
5. **No guarantee of authorship.** Even a perfectly-scoring model on this dataset provides no proof that any individual essay was or wasn't written by AI. Scores are statistical signals, not forensic evidence.
6. **Sentence-level scores are an explanatory heuristic, not a trained sentence-level classifier.** The Logistic Regression only ever sees essay-level aggregate features; it has no notion of an individual sentence's probability. Sentence-level signals are explanatory estimates derived from sentence-local measurements — computed by substituting each sentence's own local value into the essay-level feature slot, standardizing it the same way the real feature was standardized during training, and multiplying by the model's learned coefficient, then normalizing within the essay. They are not independently trained sentence-level probabilities or proof of authorship. See `backend/app/scoring.py` (module docstring above `SENTENCE_SIGNAL_FEATURE_MAP`) and the frontend's "Technical details" disclosure for the same wording.
7. **GPT-2 context limitation.** GPT-2's attention window is 1024 tokens. Essays longer than that are scored via an overlapping sliding window (each token still gets real preceding context, up to ~1023 tokens), but no token in a very long essay can ever see the *entire* preceding essay at once — a hard architectural limit, not a shortcut taken in this codebase.

## 11. Conclusions

The pipeline works end-to-end and is technically sound: GPT-2 is used strictly as an instrument, stylometric features are computed independently, and an interpretable, explicitly-trained Logistic Regression — never a chat model — makes the classification decision, with sentence-level evidence traceable back to specific measurable signals. The ablation experiment is a genuinely useful (if modest) finding: the model does not collapse to a crude cliché-keyword detector when those features are removed. But every number in this report is a **development-dataset** result on a **44-essay, single-author, artifact-prone** corpus with **zero genuine test-set failures** to analyze and **no ESL evaluation**. None of it should be presented, in a submission or otherwise, as evidence that this tool reliably detects AI-written admissions essays in the real world. The honest summary is: the engineering pipeline is complete and defensible; the dataset and evaluation are a development-stage sanity check, clearly labeled as such throughout the codebase, UI, and this report.
