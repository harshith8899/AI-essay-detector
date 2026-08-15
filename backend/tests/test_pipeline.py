"""Integration test for the full pipeline:

essay -> GPT-2 features -> stylometric features -> combined feature vector
      -> saved scaler -> saved classifier -> prediction

Requires backend/app/models/{model.pkl,scaler.pkl,feature_names.json,
metadata.json} to already exist (produced by scripts/train_classifier.py).
Does not assert exact prediction values, since those depend on the
development dataset's specific training run.
"""

import math

from app.scoring import FEATURE_NAMES, build_feature_vector, load_classifier, predict

SAMPLE_ESSAY = (
    "I grew up in a small town where everyone knew everyone else. "
    "That closeness taught me both the comfort and the limits of community. "
    "When I left for college, I finally understood what I had taken for granted."
)


def test_essay_passes_through_both_feature_extractors():
    features = build_feature_vector(SAMPLE_ESSAY)
    assert isinstance(features, dict)
    assert len(features) == len(FEATURE_NAMES)


def test_feature_names_match_trained_feature_names():
    _, _, trained_feature_names, _ = load_classifier()
    features = build_feature_vector(SAMPLE_ESSAY)
    assert set(features.keys()) == set(trained_feature_names)
    assert trained_feature_names == FEATURE_NAMES


def test_saved_scaler_can_transform_feature_vector():
    _, scaler, feature_names, _ = load_classifier()
    features = build_feature_vector(SAMPLE_ESSAY)
    row = [[features[name] for name in feature_names]]
    scaled = scaler.transform(row)
    assert scaled.shape == (1, len(feature_names))


def test_saved_classifier_produces_a_prediction():
    model, scaler, feature_names, metadata = load_classifier()
    features = build_feature_vector(SAMPLE_ESSAY)
    row = [[features[name] for name in feature_names]]
    if metadata.get("requires_scaling"):
        row = scaler.transform(row)
    preds = model.predict(row)
    assert len(preds) == 1


def test_prediction_is_binary():
    label, _ = predict(SAMPLE_ESSAY)
    assert label in (0, 1)


def test_no_nan_or_infinite_values_reach_the_classifier():
    features = build_feature_vector(SAMPLE_ESSAY)
    for name, value in features.items():
        assert not math.isnan(value), f"NaN in feature {name}"
        assert not math.isinf(value), f"inf in feature {name}"


def test_pipeline_end_to_end_on_multiple_essays():
    other_essay = (
        "Throughout my academic journey, I have consistently demonstrated a "
        "commitment to excellence. It is important to note that resilience "
        "plays a pivotal role in personal growth."
    )
    for essay in (SAMPLE_ESSAY, other_essay):
        label, features = predict(essay)
        assert label in (0, 1)
        assert len(features) == len(FEATURE_NAMES)
        for value in features.values():
            assert not math.isnan(value)
            assert not math.isinf(value)
