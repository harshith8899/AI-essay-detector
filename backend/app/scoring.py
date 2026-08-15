"""Feature-vector construction, trained-classifier loading, and sentence-
level evidence generation.

This is where the project's standing rule is implemented: lm_features.py
(the GPT-2 instrument) and stylometry.py (the linguistic feature
extractor) only produce measurable numbers. This module is the one place
that combines those numbers into a fixed-order feature vector and applies
our own explicitly-trained scikit-learn classifier to them. Nothing here
asks a chat model for a verdict.
"""

import json
from pathlib import Path

import joblib

from app.lm_features import analyze_lm_features
from app.stylometry import FUNCTION_WORDS, analyze_stylometry

MODELS_DIR = Path(__file__).resolve().parent / "models"

LM_FEATURE_NAMES = [
    "mean_perplexity",
    "burstiness",
]
STYLOMETRY_FEATURE_NAMES = [
    "sentence_length_mean",
    "sentence_length_std",
    "type_token_ratio",
    "hapax_rate",
    "pos_bigram_entropy",
    "function_word_rate",
    "cliche_count",
    "cliche_rate",
    "transition_opener_rate",
]
FUNCTION_WORD_FEATURE_NAMES = [f"fw_{word}" for word in FUNCTION_WORDS]

# Stable feature ordering used everywhere: dataset-building, training, and
# inference all import this same list so the ordering can never drift.
FEATURE_NAMES = LM_FEATURE_NAMES + STYLOMETRY_FEATURE_NAMES + FUNCTION_WORD_FEATURE_NAMES

LIMITATIONS = [
    "The model behind this score was trained on a very small, hand-authored "
    "development dataset (44 essays) and has not been scientifically validated.",
    "Current results reflect a development-stage pipeline check, not a "
    "validated measurement of real-world accuracy.",
    "The AI-authored examples used to train this model contain authoring "
    "artifacts (e.g. deliberately cliché-heavy phrasing) that make them "
    "easier to separate from human examples than real, adversarial AI text "
    "would be.",
    "This model may behave differently on essay topics, formats, lengths, or "
    "writing styles not represented in the small development dataset.",
    "Performance for English-language learners and across different "
    "linguistic or demographic backgrounds has not been evaluated, and "
    "fairness has not been established.",
    "No AI detector, including this one, can establish authorship with "
    "certainty. Scores reflect measurable statistical signals, not proof.",
    "This tool should never be used as the sole basis for an accusation of "
    "academic dishonesty.",
]


class FeatureExtractionError(Exception):
    """Raised when an essay cannot produce a usable feature vector."""


def _essay_feature_dict(lm_result: dict, sty_result: dict) -> dict:
    lm_essay = lm_result["essay"]
    sty_essay = sty_result["essay"]

    if lm_essay["mean_perplexity"] is None or lm_essay["burstiness"] is None:
        raise FeatureExtractionError(
            "GPT-2 features could not be computed for this essay (no scoreable sentences)."
        )

    features = {
        "mean_perplexity": lm_essay["mean_perplexity"],
        "burstiness": lm_essay["burstiness"],
        "sentence_length_mean": sty_essay["sentence_length_mean"],
        "sentence_length_std": sty_essay["sentence_length_std"],
        "type_token_ratio": sty_essay["type_token_ratio"],
        "hapax_rate": sty_essay["hapax_rate"],
        "pos_bigram_entropy": sty_essay["pos_bigram_entropy"],
        "function_word_rate": sty_essay["function_word_rate"],
        "cliche_count": sty_essay["cliche_count"],
        "cliche_rate": sty_essay["cliche_rate"],
        "transition_opener_rate": sty_essay["transition_opener_rate"],
    }
    for word in FUNCTION_WORDS:
        features[f"fw_{word}"] = sty_essay["function_word_profile"][word]

    return features


def build_feature_vector(essay: str) -> dict:
    """Run both extractors on `essay` and combine essay-level numbers.

    Raises FeatureExtractionError instead of fabricating a value when a
    feature genuinely cannot be computed (e.g. an essay with no
    GPT-2-scoreable sentences).
    """
    lm_result = analyze_lm_features(essay)
    sty_result = analyze_stylometry(essay)
    return _essay_feature_dict(lm_result, sty_result)


def load_classifier(models_dir: Path = MODELS_DIR):
    """Load the trained model, scaler, feature-name ordering, and metadata."""
    model = joblib.load(models_dir / "model.pkl")
    scaler = joblib.load(models_dir / "scaler.pkl")
    with open(models_dir / "feature_names.json", encoding="utf-8") as f:
        feature_names = json.load(f)
    with open(models_dir / "metadata.json", encoding="utf-8") as f:
        metadata = json.load(f)
    return model, scaler, feature_names, metadata


def predict(essay: str, models_dir: Path = MODELS_DIR):
    """Run the full pipeline (features -> scaler -> classifier) on `essay`.

    Returns (label, features) where label is 0 (human-like) or 1 (AI-like)
    per the saved classifier's own training labels. This is our own
    explicit, interpretable model — never a chat-model judgement.
    """
    model, scaler, feature_names, metadata = load_classifier(models_dir)
    features = build_feature_vector(essay)
    row = [[features[name] for name in feature_names]]
    if metadata.get("requires_scaling"):
        row = scaler.transform(row)
    label = int(model.predict(row)[0])
    return label, features


# ---------------------------------------------------------------------------
# Sentence-level evidence
#
# The trained classifier only ever sees essay-level aggregate features (its
# 61 inputs are things like mean_perplexity and sentence_length_std, computed
# over the whole essay) — it has no native notion of "this one sentence's
# score". To surface sentence-level evidence anyway, we use a documented,
# deterministic SUBSTITUTION heuristic: for a small, curated set of features
# that have an obvious sentence-level analogue, we compute what that
# feature's value would be "if this single sentence were the entire essay",
# standardize it exactly the way the real feature was standardized for
# training (same scaler mean_/scale_), and multiply by the model's own
# learned coefficient for that feature. Summing those five terms gives each
# sentence a partial, local approximation of its pull on the essay-level
# logit — not the real per-sentence output of the classifier (no such thing
# exists), but a transparent, inspectable proxy for it. Sentence scores are
# then min-max normalized across the essay's own sentences (0-100), per the
# project requirement that sentence signals be normalized within the essay
# rather than forced onto the same absolute scale as the essay-level score.
# ---------------------------------------------------------------------------

# signal name -> the essay-level feature whose trained weight we reuse
#
# cliche maps to the RATE feature (occurrences per 1000 tokens), not the raw
# essay-wide COUNT: a sentence's raw match count (0-2) is almost always below
# an essay's total count, which would make the substitution systematically
# negative even when a cliche is present. The rate is comparable in scale at
# both the sentence and essay level, so it doesn't have that bias.
SENTENCE_SIGNAL_FEATURE_MAP = {
    "perplexity": "mean_perplexity",
    "burstiness": "burstiness",
    "sentence_length": "sentence_length_mean",
    "cliche": "cliche_rate",
    "transition_opener": "transition_opener_rate",
}


def _sentence_raw_values(sentence_lm: dict, sentence_sty: dict, essay_mean_perplexity: float) -> dict:
    sentence_perplexity = sentence_lm["perplexity"] if sentence_lm["perplexity"] is not None else essay_mean_perplexity
    token_count = max(sentence_sty["token_count"], 1)
    cliche_rate = (len(sentence_sty["cliche_matches"]) / token_count) * 1000
    return {
        "perplexity": sentence_perplexity,
        "burstiness": abs(sentence_perplexity - essay_mean_perplexity),
        "sentence_length": sentence_sty["token_count"],
        "cliche": cliche_rate,
        "transition_opener": 1.0 if sentence_sty["transition_opener"] else 0.0,
    }


def _feature_weight(model, feature_index: int) -> float:
    if hasattr(model, "coef_"):
        return float(model.coef_[0][feature_index])
    if hasattr(model, "feature_importances_"):
        # Tree ensembles have no signed direction; importance is used as an
        # unsigned weight so a contribution can still be computed, just
        # without a "this pushes toward AI vs human" sign.
        return float(model.feature_importances_[feature_index])
    return 1.0


def _sentence_contributions(raw_values: dict, model, scaler, feature_names: list) -> dict:
    index_of = {name: i for i, name in enumerate(feature_names)}
    contributions = {}
    for signal_name, feature_name in SENTENCE_SIGNAL_FEATURE_MAP.items():
        i = index_of[feature_name]
        mean = scaler.mean_[i]
        scale = scaler.scale_[i] if scaler.scale_[i] else 1.0
        standardized = (raw_values[signal_name] - mean) / scale
        contributions[signal_name] = _feature_weight(model, i) * standardized
    return contributions


def _perplexity_note(contribution: float) -> str:
    if contribution > 0.05:
        return "This sentence's wording is relatively predictable under GPT-2 compared to the rest of the essay."
    if contribution < -0.05:
        return "This sentence's wording is relatively unpredictable (surprising) under GPT-2 compared to the rest of the essay."
    return "This sentence's predictability under GPT-2 is close to the essay's average."


def _burstiness_note(contribution: float) -> str:
    if contribution > 0.05:
        return "This sentence closely matches the essay's overall predictability pattern, contributing to a more uniform rhythm."
    if contribution < -0.05:
        return "This sentence's predictability stands out from the essay's overall pattern, contributing to more variation (burstiness)."
    return "This sentence's predictability is close to typical for this essay."


def _sentence_length_note(contribution: float) -> str:
    if contribution > 0.05:
        return "This sentence's length is close to the essay's typical sentence length, contributing to a more uniform rhythm."
    if contribution < -0.05:
        return "This sentence's length differs noticeably from the essay's typical rhythm."
    return "This sentence's length is close to the essay's average."


def _cliche_note(sentence_sty: dict) -> str:
    matches = sentence_sty["cliche_matches"]
    if matches:
        phrases = ", ".join(f"\"{m['phrase']}\"" for m in matches)
        return f"Contains a phrase from the detector's curated cliche list: {phrases}."
    return "Does not contain any phrase from the detector's curated cliche list."


def _transition_note(sentence_sty: dict) -> str:
    opener = sentence_sty["transition_opener"]
    if opener:
        return f"Opens with \"{opener['phrase']}\", a transition phrase often overused in AI-generated writing."
    return "Does not open with one of the curated transition phrases."


_NOTE_BUILDERS = {
    "perplexity": lambda contribution, sty: _perplexity_note(contribution),
    "burstiness": lambda contribution, sty: _burstiness_note(contribution),
    "sentence_length": lambda contribution, sty: _sentence_length_note(contribution),
    "cliche": lambda contribution, sty: _cliche_note(sty),
    "transition_opener": lambda contribution, sty: _transition_note(sty),
}


def _top_features(contributions: dict, sentence_sty: dict, top_n: int = 3) -> list:
    ranked = sorted(contributions.items(), key=lambda item: abs(item[1]), reverse=True)
    top = []
    for signal_name, contribution in ranked[:top_n]:
        top.append(
            {
                "name": signal_name,
                "contribution": round(contribution, 4),
                "plain_language_note": _NOTE_BUILDERS[signal_name](contribution, sentence_sty),
            }
        )
    return top


def _normalize_scores(raw_scores: list) -> list:
    if not raw_scores:
        return []
    lo, hi = min(raw_scores), max(raw_scores)
    if hi - lo < 1e-9:
        return [50.0 for _ in raw_scores]
    return [round(100 * (v - lo) / (hi - lo), 1) for v in raw_scores]


def _sentence_evidence(lm_result: dict, sty_result: dict, model, scaler, feature_names: list) -> list:
    lm_sentences = lm_result["sentences"]
    sty_sentences = sty_result["sentences"]
    essay_mean_perplexity = lm_result["essay"]["mean_perplexity"] or 0.0

    # Both extractors segment the same essay text with the same shared spaCy
    # pipeline, so they always produce the same sentences in the same order;
    # this is asserted defensively rather than silently trusted.
    if len(lm_sentences) != len(sty_sentences):
        raise FeatureExtractionError(
            "Sentence segmentation mismatch between lm_features and stylometry."
        )

    per_sentence_contributions = []
    for sentence_lm, sentence_sty in zip(lm_sentences, sty_sentences):
        raw_values = _sentence_raw_values(sentence_lm, sentence_sty, essay_mean_perplexity)
        contributions = _sentence_contributions(raw_values, model, scaler, feature_names)
        per_sentence_contributions.append(contributions)

    raw_scores = [sum(c.values()) for c in per_sentence_contributions]
    normalized_scores = _normalize_scores(raw_scores)

    evidence = []
    for sentence_lm, sentence_sty, contributions, score in zip(
        lm_sentences, sty_sentences, per_sentence_contributions, normalized_scores
    ):
        evidence.append(
            {
                "text": sentence_sty["text"],
                "start_offset": sentence_sty["start_offset"],
                "end_offset": sentence_sty["end_offset"],
                "score": score,
                # Raw (non-normalized) GPT-2 perplexity for this sentence, so the
                # UI can plot sentence-number-vs-perplexity directly (see the
                # burstiness chart) without re-deriving it from `score`.
                "perplexity": sentence_lm["perplexity"],
                "top_features": _top_features(contributions, sentence_sty),
            }
        )
    return evidence


def analyze_essay(essay: str, models_dir: Path = MODELS_DIR) -> dict:
    """Full pipeline: essay -> GPT-2 + stylometric features -> scaled feature
    vector -> classifier -> essay score + sentence-level evidence.

    This is the single entrypoint the API calls. No retraining happens here
    — model/scaler/feature ordering are loaded from disk, exactly as saved
    by scripts/train_classifier.py.
    """
    model, scaler, feature_names, metadata = load_classifier(models_dir)

    lm_result = analyze_lm_features(essay)
    sty_result = analyze_stylometry(essay)
    features = _essay_feature_dict(lm_result, sty_result)

    if feature_names != FEATURE_NAMES:
        raise FeatureExtractionError(
            "Saved feature_names.json does not match the current feature ordering."
        )

    row = [[features[name] for name in feature_names]]
    scaled_row = scaler.transform(row) if metadata.get("requires_scaling") else row

    if hasattr(model, "predict_proba"):
        ai_probability = float(model.predict_proba(scaled_row)[0][1])
    else:
        # Fallback for a model type with no predict_proba: treat the binary
        # prediction itself as a 0/100 signal rather than fabricating a
        # continuous number the model never actually produced.
        ai_probability = float(model.predict(scaled_row)[0])

    essay_score = round(100 * ai_probability, 1)
    label = "higher AI-like signal" if essay_score >= 50 else "lower AI-like signal"

    sentences = _sentence_evidence(lm_result, sty_result, model, scaler, feature_names)

    return {
        "essay_score": essay_score,
        "label": label,
        "sentences": sentences,
        "limitations": LIMITATIONS,
    }
