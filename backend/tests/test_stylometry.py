import math

from app.stylometry import FUNCTION_WORDS, analyze_stylometry

SAMPLE_ESSAY = (
    "I grew up in a small town where everyone knew everyone else. "
    "That closeness taught me both the comfort and the limits of community. "
    "When I left for college, I finally understood what I had taken for granted."
)

CLICHE_ESSAY = (
    "Education plays a pivotal role in society. "
    "Moreover, it helps students delve into new ideas. "
    "In today's society, this is a testament to progress."
)


def _assert_no_nan_or_inf(value, path=""):
    if isinstance(value, float):
        assert not math.isnan(value), f"NaN at {path}"
        assert not math.isinf(value), f"inf at {path}"
    elif isinstance(value, dict):
        for k, v in value.items():
            _assert_no_nan_or_inf(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _assert_no_nan_or_inf(v, f"{path}[{i}]")


def test_empty_input_does_not_crash():
    result = analyze_stylometry("")
    assert result["sentences"] == []
    assert result["essay"]["sentence_count"] == 0
    _assert_no_nan_or_inf(result)


def test_whitespace_only_input_does_not_crash():
    result = analyze_stylometry("   \n\t  ")
    assert result["sentences"] == []
    _assert_no_nan_or_inf(result)


def test_one_word_essay_does_not_crash():
    result = analyze_stylometry("Persevere.")
    _assert_no_nan_or_inf(result)
    assert result["essay"]["sentence_count"] >= 1


def test_punctuation_only_input_does_not_crash():
    result = analyze_stylometry("... !!! ???")
    _assert_no_nan_or_inf(result)


def test_normal_essay_returns_expected_keys():
    result = analyze_stylometry(SAMPLE_ESSAY)
    assert set(result.keys()) == {"sentences", "essay"}
    essay_keys = {
        "sentence_count",
        "lexical_token_count",
        "sentence_length_mean",
        "sentence_length_std",
        "type_token_ratio",
        "hapax_rate",
        "pos_bigram_entropy",
        "pos_bigram_count",
        "function_word_rate",
        "function_word_profile",
        "cliche_count",
        "cliche_rate",
        "transition_opener_rate",
    }
    assert essay_keys.issubset(result["essay"].keys())
    for sent in result["sentences"]:
        sentence_keys = {
            "text",
            "start_offset",
            "end_offset",
            "token_count",
            "contains_cliche",
            "cliche_matches",
            "transition_opener",
        }
        assert sentence_keys.issubset(sent.keys())


def test_sentence_offsets_match_original_text():
    result = analyze_stylometry(SAMPLE_ESSAY)
    assert len(result["sentences"]) == 3
    for sent in result["sentences"]:
        assert SAMPLE_ESSAY[sent["start_offset"] : sent["end_offset"]] == sent["text"]


def test_ttr_within_bounds():
    result = analyze_stylometry(SAMPLE_ESSAY)
    assert 0 <= result["essay"]["type_token_ratio"] <= 1


def test_hapax_rate_within_bounds():
    result = analyze_stylometry(SAMPLE_ESSAY)
    assert 0 <= result["essay"]["hapax_rate"] <= 1


def test_pos_entropy_non_negative():
    result = analyze_stylometry(SAMPLE_ESSAY)
    assert result["essay"]["pos_bigram_entropy"] >= 0


def test_function_word_profile_has_complete_fixed_vocabulary():
    result = analyze_stylometry(SAMPLE_ESSAY)
    profile = result["essay"]["function_word_profile"]
    assert set(profile.keys()) == set(FUNCTION_WORDS)

    # Even essays with none of these words must still report the full vocabulary.
    empty_result = analyze_stylometry("Zzyzx.")
    assert set(empty_result["essay"]["function_word_profile"].keys()) == set(FUNCTION_WORDS)


def test_function_word_rates_non_negative():
    result = analyze_stylometry(SAMPLE_ESSAY)
    assert result["essay"]["function_word_rate"] >= 0
    for rate in result["essay"]["function_word_profile"].values():
        assert rate >= 0


def test_known_cliche_phrase_is_detected():
    result = analyze_stylometry(CLICHE_ESSAY)
    assert result["essay"]["cliche_count"] >= 4
    phrases_found = {m["phrase"] for s in result["sentences"] for m in s["cliche_matches"]}
    assert "delve into" in phrases_found
    assert "plays a pivotal role" in phrases_found


def test_cliche_offsets_point_to_actual_phrase():
    result = analyze_stylometry(CLICHE_ESSAY)
    for sent in result["sentences"]:
        for m in sent["cliche_matches"]:
            snippet = CLICHE_ESSAY[m["start_offset"] : m["end_offset"]]
            assert snippet.lower() == m["phrase"].lower()


def test_moreover_sentence_opener_is_detected():
    result = analyze_stylometry(CLICHE_ESSAY)
    openers = [s["transition_opener"] for s in result["sentences"] if s["transition_opener"]]
    assert any(o["phrase"].lower() == "moreover" for o in openers)
    for o in openers:
        snippet = CLICHE_ESSAY[o["start_offset"] : o["end_offset"]]
        assert snippet == o["phrase"]


def test_no_cliches_or_transitions_in_plain_essay():
    result = analyze_stylometry(SAMPLE_ESSAY)
    assert result["essay"]["cliche_count"] == 0
    assert result["essay"]["transition_opener_rate"] == 0
    assert all(not s["contains_cliche"] for s in result["sentences"])
    assert all(s["transition_opener"] is None for s in result["sentences"])


def test_no_nan_or_infinite_values():
    for essay in [SAMPLE_ESSAY, CLICHE_ESSAY, "", "   ", "Word.", "!!!"]:
        result = analyze_stylometry(essay)
        _assert_no_nan_or_inf(result)


def test_unicode_and_contractions_do_not_crash():
    essay = "It's a “beautiful” day—don't you think? She said, ‘Yes!’"
    result = analyze_stylometry(essay)
    _assert_no_nan_or_inf(result)
    for sent in result["sentences"]:
        assert essay[sent["start_offset"] : sent["end_offset"]] == sent["text"]
