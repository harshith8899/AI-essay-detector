# AI Essay Signal Analyzer

## Problem

College admissions offices increasingly worry that essays may be partly or wholly written by AI. Existing "AI detectors" are largely black boxes: they hand an essay to a chat model and ask it to render a verdict, then present a single confident-looking percentage with no way to inspect *why*. That approach is unreliable (LLM self-judgment of AI-generated text is not well-calibrated) and unaccountable (a reader can't see what evidence, if any, backs the number).

This project takes a different approach: extract **measurable, inspectable, numeric signals** from an essay — statistical properties of how predictable its wording is under a language model, and independent linguistic/stylometric properties of its structure and word choice — and combine those explicit numbers with our own trained classifier. The result is a score with a paper trail: every essay-level and sentence-level number traces back to a specific, named, human-readable measurement.

## Core design principle

```
LM        →  statistical measurements   (token log-probabilities, perplexity, burstiness)
Our code  →  feature extraction          (lm_features.py + stylometry.py, 61 numeric features)
Our classifier →  decision               (scikit-learn Logistic Regression, explicitly trained)
UI        →  evidence                    (sentence highlighting, plain-language explanations, charts)
```

**No chat model is called during essay analysis to make the classification decision.** GPT-2 is loaded locally and used strictly as an instrument: it is never prompted with "is this AI-generated?" and it never renders a verdict. It only produces token log-probabilities, from which our own code computes perplexity and burstiness. All feature combination, thresholds, scaling, and classification happen in explicit Python/scikit-learn code that ships in this repository and can be read end to end.

## Architecture

```
ai-essay-detector/
├── backend/
│   ├── app/
│   │   ├── main.py             FastAPI app: GET /, POST /analyze
│   │   ├── lm_features.py      GPT-2 instrument: token log-probs → perplexity, burstiness
│   │   ├── stylometry.py       spaCy-based linguistic features (no LLM involved)
│   │   ├── spacy_pipeline.py   Shared en_core_web_sm loader (used by both extractors)
│   │   ├── scoring.py          Feature-vector construction, classifier loading,
│   │   │                       essay score + sentence-evidence engine
│   │   └── models/             Saved artifacts: model.pkl, scaler.pkl,
│   │                           feature_names.json, metadata.json
│   ├── scripts/
│   │   ├── seed_dev_dataset.py    Writes the hand-authored development dataset
│   │   ├── generate_polished.py   Real (API-gated) human→polished essay generator
│   │   ├── build_dataset.py       data/*_essays/*.txt → dataset table
│   │   ├── build_features.py      Runs both extractors on every essay → features.csv
│   │   ├── train_classifier.py    Trains, evaluates, saves the deployed classifier
│   │   └── evaluate.py            Held-out evaluation, ablation, confident-failure,
│   │                              and polished-essay analysis (see REPORT.md)
│   └── tests/                  pytest suite (unit tests per module + API integration test)
├── data/                       Essay corpora + features.csv — see data/README.md
├── frontend/                   React + Vite web interface
├── REPORT.md                   Full evaluation report
└── README.md                   This file
```

## Tech stack

**Backend:** Python, FastAPI, PyTorch, Hugging Face Transformers, GPT-2, spaCy, scikit-learn.

**Frontend:** React, Vite, plain CSS (no UI framework, no state-management library).

## Features

- **Essay analysis** — paste an essay, get a full breakdown in one request.
- **Sentence highlighting** — every sentence in the essay is rendered with a continuous, single-hue background intensity proportional to its own signal score (never a red/green binary verdict).
- **Evidence explanations** — click any sentence to open a side panel showing its signal score and the top 3 contributing measurements, each with a plain-language note (a secondary "technical details" toggle exposes the raw numbers for anyone who wants them).
- **Perplexity visualization** — a per-sentence perplexity bar chart makes the burstiness concept (human writing tends to swing between predictable and surprising; AI text tends to stay uniformly predictable) visible at a glance.
- **Overall signal score** — a single 0–100 "AI-likeness signal" with a continuous meter, explicitly labeled as an experimental model score, not a probability of authorship.
- **Limitations panel** — every response carries a `limitations` array, rendered prominently in the UI (not hidden in a tooltip), listing the dataset's size, known artifacts, and the fact that no AI detector can establish authorship with certainty.

## How it works

```
Essay
  |
  v
Sentence segmentation (spaCy, en_core_web_sm)
  |
  v
GPT-2 token log-probabilities (real preceding-essay context, sliding
window beyond GPT-2's 1024-token limit)          -->  mean_perplexity, burstiness
  |
  +-----------------------------+
                                |
                                v
                    Stylometric extraction (spaCy only, no LLM):
                    sentence length, TTR, hapax rate, POS-bigram
                    entropy, function-word profile, cliche/transition
                    detection
                                |
  +-----------------------------+
  |
  v
61-feature vector (fixed order, see REPORT.md §9)
  |
  v
StandardScaler (fit on training data, saved to disk)
  |
  v
Logistic Regression (explicitly trained, saved to disk — no retraining at request time)
  |
  v
Essay signal (0-100, from predict_proba, presented as an experimental score)
  |
  v
Sentence evidence (a documented, deterministic heuristic — see "Sentence-level
scoring" below — NOT an independently trained sentence-level classifier)
```

## Running locally

**Backend:**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
python -m spacy download en_core_web_sm   # if not already installed
uvicorn app.main:app --reload
```

`GET http://localhost:8000/` → `{"status": "ok", "service": "AI Essay Detector"}`.
`POST http://localhost:8000/analyze` with body `{"essay": "..."}` → the full analysis response.

**Frontend** (in a second terminal):

```bash
cd frontend
npm install
cp .env.example .env      # or set VITE_API_URL yourself; defaults to http://localhost:8000
npm run dev
```

Open the printed local URL (typically `http://localhost:5173`), paste an essay, click "Analyze Essay".

**Tests:**

```bash
cd backend
pytest tests -v
```

```bash
cd frontend
npm run build
```

## Training workflow

```
data/human_essays, data/ai_essays, data/polished_essays  (.txt + .json sidecars)
        |  scripts/build_dataset.py
        v
dataset table (essay_id, category, label, text, source metadata)
        |  scripts/build_features.py  (runs lm_features + stylometry on every essay)
        v
data/features.csv + data/feature_names.json
        |  scripts/train_classifier.py
        v
essay-level train/test split (stratified, fixed seed=42, test_size=0.25;
never splits sentences of one essay — each row is already one whole essay)
        v
Logistic Regression (scaled) + Gradient Boosting, evaluated on held-out test set
        v
backend/app/models/{model.pkl, scaler.pkl, feature_names.json, metadata.json}
```

Polished essays are loaded but deliberately excluded from the binary train/test split — they are a mixed human+LLM-edited case, not a clean human/AI label — and are only scored as a reference after training. Run `python -m scripts.evaluate` for the full held-out evaluation, ablation experiment, and polished-essay analysis (see `REPORT.md`).

## Dataset

**44 essays total: 16 human, 16 AI, 12 polished.** Every essay was hand-authored by the assistant in a single offline session as development placeholder content — none are real applicants' essays, and none were produced by an actual LLM API call (no API is configured in this project). Full provenance, topic coverage, and known authoring artifacts are documented in [`data/README.md`](data/README.md).

## Evaluation

**These are development-dataset results, not a scientific validation of real-world accuracy.** Full methodology, tables, an ablation experiment, confident-failure analysis, and polished-essay results are in [`REPORT.md`](REPORT.md). Headline numbers:

| | Full model (61 features) | Ablation model (58 features, cliché/transition removed) |
|---|---:|---:|
| Accuracy | 1.000 | 1.000 |
| Precision | 1.000 | 1.000 |
| Recall | 1.000 | 1.000 |
| F1 | 1.000 | 1.000 |

n_test = 8. Zero genuine misclassifications occurred on this test set for either model — see `REPORT.md` §7 for why that is itself evidence the dataset is too small/easy, not evidence of real-world accuracy, and §5 for why the ablation result doesn't rule out a single-author stylistic confound (the same author wrote both classes).

## Known limitations

- **Tiny dataset** — 44 hand-authored essays (32 for binary training). No result here generalizes beyond this specific small corpus.
- **Authoring artifacts** — all essays written by one author in one sitting; AI examples deliberately cliché/transition-heavy.
- **Topic limitations** — personal-narrative admissions-essay topics only; no STEM-heavy research essays, sensitive topics, non-US formats, or long-form essays.
- **No controlled ESL evaluation** — documented as **NOT YET ESTABLISHED**, not glossed over. See `REPORT.md` §8.
- **No guarantee of authorship** — even a perfectly-scoring model provides no proof that any individual essay was or wasn't AI-written. This tool must never be the sole basis for an academic-dishonesty accusation.
- **Sentence-level scores are an explanatory heuristic, not a trained sentence-level classifier.** The Logistic Regression only ever sees essay-level aggregate features — it has no notion of an individual sentence's probability. Sentence-level signals are explanatory estimates derived from sentence-local measurements: each sentence's own local value is substituted into the corresponding essay-level feature slot, standardized the same way that feature was standardized during training, multiplied by the model's learned coefficient, then normalized within the essay. **They are not independently trained sentence-level probabilities or proof of authorship.** The same wording appears in the UI's "Technical details" panel (`frontend/src/components/EvidencePanel.jsx`) and in `backend/app/scoring.py`.
- **GPT-2 context limitation** — GPT-2's attention window is 1024 tokens. Longer essays are scored via an overlapping sliding window (every token still gets real preceding context), but no token in a very long essay can attend to the *entire* preceding essay at once — an architectural limit of GPT-2, not a shortcut taken here.

## Why this is not an LLM wrapper

The application never sends a user's essay to a chat model and asks it to classify, score, or judge it. The only language model in the request path is GPT-2, running locally, used exclusively to compute token log-probabilities — a fixed, deterministic, non-generative statistical measurement. Every step that turns those numbers (and the independent stylometric numbers) into a decision — feature combination, scaling, classification, thresholds, sentence-level evidence — is explicit Python/scikit-learn code in this repository, not a prompt to a chat model. `backend/scripts/generate_polished.py` is the one place an external chat-model API (Anthropic/OpenAI) is referenced anywhere in the codebase, and it is strictly an **offline dataset-authoring tool**: it is never imported by, or reachable from, the `/analyze` request path, and its provider functions currently only raise `NotImplementedError`/`RuntimeError` rather than making any real call.
