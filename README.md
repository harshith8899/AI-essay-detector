# AI Essay Detector

## What this project does

A tool for analyzing college admissions essays to identify sentences or passages that are likely machine-written, with concrete evidence explaining why each flagged span was flagged.

The detector does **not** ask a language model to render a verdict. A local language model (GPT-2) is used only as an instrument to produce measurable signals — token log-probabilities, perplexity, and burstiness. Those numbers are combined with independent stylometric features (sentence length, lexical diversity, POS-tag entropy, function-word frequencies, cliché/transition-word usage) into a fixed-order feature vector. Classification is performed by our own explicitly-trained, interpretable scikit-learn classifier (Logistic Regression / Gradient Boosting) — never by asking a chat model to classify or score the essay.

## Current architecture

```text
ai-essay-detector/
├── backend/
│   ├── app/
│   │   ├── main.py            FastAPI entrypoint (health check only so far)
│   │   ├── lm_features.py     GPT-2 instrument: token log-probs, perplexity, burstiness
│   │   ├── stylometry.py      spaCy-based linguistic/stylometric features (no LLM)
│   │   ├── spacy_pipeline.py  Shared en_core_web_sm loader used by both extractors
│   │   ├── scoring.py         Feature-vector construction + trained-classifier loading/prediction
│   │   └── models/            Saved classifier artifacts (model.pkl, scaler.pkl, feature_names.json, metadata.json)
│   ├── scripts/
│   │   ├── seed_dev_dataset.py    Writes the hand-authored development dataset to data/
│   │   ├── generate_polished.py   Real (API-gated) human->polished essay generator + sentence diff
│   │   ├── build_dataset.py       Discovers data/*_essays/*.txt -> dataset table
│   │   ├── build_features.py      Runs both extractors on every essay -> data/features.csv
│   │   └── train_classifier.py    Trains/evaluates/saves the classifier
│   └── tests/                 pytest suite (unit tests per module + full-pipeline integration test)
├── data/            Essay corpora (human / AI / AI-polished) + features.csv — see data/README.md
└── frontend/        Client application (not yet created)
```

## Current feature set

Computed per essay via `app/scoring.py: build_feature_vector()`, 61 features total, always in the same fixed order (`FEATURE_NAMES`):

- **From GPT-2** (`lm_features.py`): `mean_perplexity`, `burstiness` — token log-probabilities are computed with real preceding-essay context (not per-sentence in isolation), via a sliding window when an essay exceeds GPT-2's 1024-token context.
- **From stylometry** (`stylometry.py`, spaCy only, no LLM): `sentence_length_mean`, `sentence_length_std`, `type_token_ratio`, `hapax_rate`, `pos_bigram_entropy`, `function_word_rate`, `cliche_count`, `cliche_rate`, `transition_opener_rate`, plus the full 50-word fixed function-word frequency profile (`fw_<word>`).

Sentence-level detail (per-sentence perplexity, cliché matches, transition openers, offsets into the original essay) is preserved by both extractors so a future phase can derive sentence-level evidence without re-running the model.

## Training workflow

```text
data/human_essays, data/ai_essays, data/polished_essays  (.txt + .json sidecars)
        |  scripts/build_dataset.py
        v
dataset table (essay_id, category, label, text, source metadata)
        |  scripts/build_features.py  (runs lm_features + stylometry on every essay)
        v
data/features.csv + data/feature_names.json
        |  scripts/train_classifier.py
        v
essay-level train/test split (stratified, fixed seed, never splits sentences of one essay)
        v
Logistic Regression (scaled) + Gradient Boosting, evaluated on held-out test set
        v
backend/app/models/{model.pkl, scaler.pkl, feature_names.json, metadata.json}
```

Polished essays are loaded but deliberately excluded from the binary train/test split (they're a mixed human+LLM-edited case, not a clean human/AI label) — they're only scored as a reference after training.

## How to train

```bash
cd backend
.venv\Scripts\activate
python -m scripts.seed_dev_dataset     # only needed once, or to regenerate the dev dataset
python -m scripts.build_dataset        # sanity-check: prints dataset counts
python -m scripts.build_features       # writes data/features.csv
python -m scripts.train_classifier     # trains, evaluates, saves model artifacts
```

## How to run the application

```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
```

```text
GET http://localhost:8000/
```
returns `{"status": "ok", "service": "AI Essay Detector"}`.

`POST /analyze` (body: `{"essay": "..."}`) runs the full pipeline — GPT-2 features, stylometric features, the saved scaler, and the saved classifier — and returns an essay-level `essay_score` (0-100, described as an experimental signal, not a probability), a `label`, per-sentence evidence (`score`, raw `perplexity`, and the top 3 contributing signals with plain-language explanations), and a `limitations` list. See `app/scoring.py` for the sentence-evidence methodology (a documented substitution heuristic — the classifier only ever sees essay-level features, so sentence scores are a transparent local approximation, not the model's literal per-sentence output).

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env   # or set VITE_API_URL yourself
npm run dev
```

Open the printed local URL (typically `http://localhost:5173`), paste an essay, and click "Analyze Essay".

## How to run tests

```bash
cd backend
pytest tests -v
```

Covers: GPT-2 feature extraction edge cases, stylometric feature edge cases, and a full-pipeline integration test (essay → both extractors → combined feature vector → saved scaler → saved classifier → binary prediction), asserting no NaN/infinite values reach the classifier and that feature ordering matches what the model was trained on.

## Current development dataset limitations

The dataset in `data/` is **small (44 essays) and entirely hand-authored as development placeholder content** — not real applicant essays, and not the output of any actual LLM API call (none is configured in this project). Reported classifier metrics (currently 100% accuracy on an 8-essay test split) reflect that the placeholder "AI" essays were deliberately written with heavy cliché/transition-word usage to exercise the stylometry detectors, which makes the classes trivially separable — **this is a known dataset artifact, not a validated real-world result.** See [`data/README.md`](data/README.md) for the full, honest accounting of what this dataset is, what topics it does and doesn't cover, and what would need to change before any accuracy claim could be taken seriously.

## Current project status

**Phase 6 complete.** The full pipeline is wired end-to-end: a FastAPI `POST /analyze` endpoint (`app/main.py`, `app/scoring.py`) runs GPT-2 + stylometric feature extraction, the saved scaler and classifier, and a deterministic sentence-level evidence engine; a React + Vite frontend (`frontend/`) lets a user paste an essay, see a continuous 0-100 signal score, click individual sentences to see why they were flagged, and view a per-sentence perplexity chart and the model's limitations. Verified end-to-end in a real browser against a human, an AI-style, and a polished development essay.
