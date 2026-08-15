from app.lm_features import analyze_lm_features

SAMPLE_ESSAY = (
    "I grew up in a small town where everyone knew everyone else. "
    "That closeness taught me both the comfort and the limits of community. "
    "When I left for college, I finally understood what I had taken for granted."
)


def test_empty_input_does_not_crash():
    result = analyze_lm_features("")
    assert result["sentences"] == []
    assert result["essay"]["sentence_count"] == 0
    assert result["essay"]["token_count"] == 0


def test_whitespace_only_input_does_not_crash():
    result = analyze_lm_features("   \n\t  ")
    assert result["sentences"] == []
    assert result["essay"]["sentence_count"] == 0


def test_top_level_keys_present():
    result = analyze_lm_features(SAMPLE_ESSAY)
    assert set(result.keys()) == {"sentences", "essay"}
    essay_keys = {"mean_perplexity", "burstiness", "sentence_count", "token_count"}
    assert essay_keys.issubset(result["essay"].keys())
    for sent in result["sentences"]:
        sentence_keys = {"text", "start_offset", "end_offset", "mean_logprob", "perplexity", "token_count"}
        assert sentence_keys.issubset(sent.keys())


def test_sentence_offsets_map_to_original_text():
    result = analyze_lm_features(SAMPLE_ESSAY)
    assert len(result["sentences"]) == 3
    for sent in result["sentences"]:
        assert SAMPLE_ESSAY[sent["start_offset"] : sent["end_offset"]] == sent["text"]


def test_non_empty_sentences_have_non_negative_token_count():
    result = analyze_lm_features(SAMPLE_ESSAY)
    assert len(result["sentences"]) > 0
    for sent in result["sentences"]:
        assert sent["token_count"] >= 0


def test_perplexity_positive_when_tokens_present():
    result = analyze_lm_features(SAMPLE_ESSAY)
    for sent in result["sentences"]:
        if sent["token_count"] > 0:
            assert sent["perplexity"] > 0


def test_essay_level_aggregates_exist():
    result = analyze_lm_features(SAMPLE_ESSAY)
    essay = result["essay"]
    assert essay["sentence_count"] == len(result["sentences"])
    assert essay["token_count"] > 0
    assert essay["mean_perplexity"] is not None
    assert essay["mean_perplexity"] > 0
    assert essay["burstiness"] is not None
    assert essay["burstiness"] >= 0
