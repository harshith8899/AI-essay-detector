"""Feature-vector construction and trained-classifier loading.

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


class FeatureExtractionError(Exception):
    """Raised when an essay cannot produce a usable feature vector."""


def build_feature_vector(essay: str) -> dict:
    """Run both extractors on `essay` and combine essay-level numbers.

    Raises FeatureExtractionError instead of fabricating a value when a
    feature genuinely cannot be computed (e.g. an essay with no
    GPT-2-scoreable sentences).
    """
    lm_result = analyze_lm_features(essay)
    sty_result = analyze_stylometry(essay)

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
