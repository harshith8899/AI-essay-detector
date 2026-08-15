"""Stylometric feature extraction.

Pure linguistic/statistical measurements via spaCy — sentence length,
lexical diversity, POS-tag entropy, function-word frequencies, cliche
phrases, transition-word openers. This module never loads GPT-2 or any
other language model, and it never produces an AI/human verdict or
probability. It only returns measurable numbers for a later phase to
combine and threshold explicitly.
"""

import math
import re
import statistics

from app.spacy_pipeline import nlp

# A token counts as a "lexical word" if it contains at least one alphabetic
# character. This excludes pure punctuation, digits, and whitespace tokens,
# while still counting contraction fragments (spaCy already splits "don't"
# into "do" + "n't", and "n't"/"'s" etc. contain letters) as lexical words.
def _is_lexical(token) -> bool:
    return any(ch.isalpha() for ch in token.text)


FUNCTION_WORDS = [
    "the", "a", "an", "and", "or", "but", "if", "then", "because", "although",
    "of", "to", "in", "on", "at", "for", "from", "with", "by", "about",
    "as", "into", "through", "during", "before", "after", "between", "while",
    "is", "am", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did",
    "I", "you", "he", "she", "it", "we", "they", "this",
]

CLICHE_PHRASES = [
    "delve into",
    "tapestry of",
    "testament to",
    "in today's society",
    "plays a pivotal role",
    "it is important to note",
    "navigate the complexities of",
]

TRANSITION_OPENERS = [
    "moreover",
    "furthermore",
    "additionally",
    "in conclusion",
]

# Leading characters (quotation marks) tolerated before a transition opener,
# in addition to plain whitespace.
_LEADING_QUOTE_CHARS = "\"'“‘’”"


def _apostrophe_tolerant_pattern(phrase: str) -> re.Pattern:
    """Regex for `phrase`, matching straight (') or curly (’) apostrophes."""
    escaped = re.escape(phrase).replace("\\'", "['’]")
    return re.compile(escaped, re.IGNORECASE)


_CLICHE_PATTERNS = [(phrase, _apostrophe_tolerant_pattern(phrase)) for phrase in CLICHE_PHRASES]

_TRANSITION_PATTERN = re.compile(
    r"^(" + "|".join(re.escape(p) for p in TRANSITION_OPENERS) + r")\b",
    re.IGNORECASE,
)


def _safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    if not denominator:
        return default
    return numerator / denominator


def _find_cliche_matches(essay: str) -> list[dict]:
    matches = []
    for phrase, pattern in _CLICHE_PATTERNS:
        for m in pattern.finditer(essay):
            matches.append({"phrase": phrase, "start_offset": m.start(), "end_offset": m.end()})
    matches.sort(key=lambda d: d["start_offset"])
    return matches


def _find_transition_opener(sentence_text: str, sentence_start: int) -> dict | None:
    lead = 0
    while lead < len(sentence_text) and (
        sentence_text[lead].isspace() or sentence_text[lead] in _LEADING_QUOTE_CHARS
    ):
        lead += 1
    m = _TRANSITION_PATTERN.match(sentence_text, lead)
    if not m:
        return None
    return {
        "phrase": sentence_text[m.start() : m.end()],
        "start_offset": sentence_start + m.start(),
        "end_offset": sentence_start + m.end(),
    }


def _empty_result() -> dict:
    return {
        "sentences": [],
        "essay": {
            "sentence_count": 0,
            "lexical_token_count": 0,
            "sentence_length_mean": 0.0,
            "sentence_length_std": 0.0,
            "type_token_ratio": 0.0,
            "hapax_rate": 0.0,
            "pos_bigram_entropy": 0.0,
            "pos_bigram_count": 0,
            "function_word_rate": 0.0,
            "function_word_profile": {word: 0.0 for word in FUNCTION_WORDS},
            "cliche_count": 0,
            "cliche_rate": 0.0,
            "transition_opener_rate": 0.0,
        },
    }


def analyze_stylometry(essay: str) -> dict:
    """Compute stylometric features for `essay`. Pure measurement, no verdict."""
    if not essay or not essay.strip():
        return _empty_result()

    doc = nlp(essay)
    sents = [sent for sent in doc.sents if sent.end_char > sent.start_char]
    if not sents:
        return _empty_result()

    # --- sentence length (in spaCy tokens, whitespace tokens excluded) ---
    sentence_lengths = []
    sentence_token_lists = []
    for sent in sents:
        tokens = [tok for tok in sent if not tok.is_space]
        sentence_token_lists.append(tokens)
        sentence_lengths.append(len(tokens))

    sentence_length_mean = statistics.mean(sentence_lengths) if sentence_lengths else 0.0
    sentence_length_std = statistics.pstdev(sentence_lengths) if len(sentence_lengths) > 1 else 0.0

    # --- lexical stats: type-token ratio, hapax rate ---
    lexical_words = [tok.text.lower() for tok in doc if _is_lexical(tok)]
    total_lexical = len(lexical_words)
    freq = {}
    for w in lexical_words:
        freq[w] = freq.get(w, 0) + 1
    unique_types = len(freq)
    type_token_ratio = _safe_div(unique_types, total_lexical)
    hapax_words = sum(1 for count in freq.values() if count == 1)
    hapax_rate = _safe_div(hapax_words, total_lexical)

    # --- POS-tag bigram entropy (across the whole essay, whitespace tokens excluded) ---
    pos_sequence = [tok.pos_ for tok in doc if not tok.is_space]
    pos_bigrams = list(zip(pos_sequence, pos_sequence[1:]))
    pos_bigram_count = len(pos_bigrams)
    if pos_bigram_count == 0:
        pos_bigram_entropy = 0.0
    else:
        bigram_freq = {}
        for bg in pos_bigrams:
            bigram_freq[bg] = bigram_freq.get(bg, 0) + 1
        pos_bigram_entropy = -sum(
            (count / pos_bigram_count) * math.log2(count / pos_bigram_count) for count in bigram_freq.values()
        )

    # --- function-word profile: frequency per 1000 lexical tokens ---
    function_word_set_lower = {w.lower() for w in FUNCTION_WORDS}
    function_word_counts = {word: 0 for word in FUNCTION_WORDS}
    lower_to_original = {}
    for word in FUNCTION_WORDS:
        lower_to_original.setdefault(word.lower(), word)
    total_function_word_occurrences = 0
    for w in lexical_words:
        if w in function_word_set_lower:
            function_word_counts[lower_to_original[w]] += 1
            total_function_word_occurrences += 1
    function_word_profile = {
        word: _safe_div(count, total_lexical) * 1000 for word, count in function_word_counts.items()
    }
    function_word_rate = _safe_div(total_function_word_occurrences, total_lexical) * 1000

    # --- cliche phrases ---
    cliche_matches = _find_cliche_matches(essay)
    cliche_count = len(cliche_matches)
    # Normalized as occurrences per 1000 lexical tokens, matching the
    # function-word-rate units so the two are directly comparable.
    cliche_rate = _safe_div(cliche_count, total_lexical) * 1000

    # --- assign cliche matches + transition openers to sentences ---
    sentence_results = []
    ci = 0
    transition_hits = 0
    for sent, tokens in zip(sents, sentence_token_lists):
        start, end = sent.start_char, sent.end_char

        sent_matches = []
        while ci < len(cliche_matches) and cliche_matches[ci]["start_offset"] < end:
            if cliche_matches[ci]["start_offset"] >= start:
                sent_matches.append(cliche_matches[ci])
            ci += 1

        transition_opener = _find_transition_opener(sent.text, start)
        if transition_opener is not None:
            transition_hits += 1

        sentence_results.append(
            {
                "text": sent.text,
                "start_offset": start,
                "end_offset": end,
                "token_count": len(tokens),
                "contains_cliche": len(sent_matches) > 0,
                "cliche_matches": sent_matches,
                "transition_opener": transition_opener,
            }
        )

    transition_opener_rate = _safe_div(transition_hits, len(sents))

    return {
        "sentences": sentence_results,
        "essay": {
            "sentence_count": len(sents),
            "lexical_token_count": total_lexical,
            "sentence_length_mean": sentence_length_mean,
            "sentence_length_std": sentence_length_std,
            "type_token_ratio": type_token_ratio,
            "hapax_rate": hapax_rate,
            "pos_bigram_entropy": pos_bigram_entropy,
            "pos_bigram_count": pos_bigram_count,
            "function_word_rate": function_word_rate,
            "function_word_profile": function_word_profile,
            "cliche_count": cliche_count,
            "cliche_rate": cliche_rate,
            "transition_opener_rate": transition_opener_rate,
        },
    }


if __name__ == "__main__":
    human_paragraph = (
        "I didn't expect to fall in love with the smell of sawdust, but that's "
        "exactly what happened the summer I started helping my grandfather in "
        "his garage. He'd hand me a piece of scrap wood and just say 'see what's "
        "in there,' which honestly annoyed me at first because I wanted "
        "instructions, not riddles. By August I was the one telling him to slow "
        "down and let me finish a cut."
    )

    ai_paragraph = (
        "Throughout my academic journey, I have consistently demonstrated a "
        "commitment to excellence and a passion for lifelong learning. It is "
        "through overcoming numerous challenges that I have cultivated resilience "
        "and honed my leadership skills. These formative experiences have not only "
        "shaped my character but have also prepared me to make a meaningful "
        "contribution to your esteemed institution."
    )

    results = {}
    for label, paragraph in [("HUMAN-STYLE PARAGRAPH", human_paragraph), ("AI-STYLE PARAGRAPH", ai_paragraph)]:
        print(f"\n=== {label} ===")
        result = analyze_stylometry(paragraph)
        results[label] = result
        for sent in result["sentences"]:
            print(f"- text: {sent['text']!r}")
            print(f"  token_count: {sent['token_count']}")
            print(f"  contains_cliche: {sent['contains_cliche']}")
            print(f"  transition_opener: {sent['transition_opener']}")
        essay = result["essay"]
        print(f"essay: {essay}")

    print("\n=== COMPARISON ===")
    for label in results:
        essay = results[label]["essay"]
        print(
            f"{label}: "
            f"sent_len_mean={essay['sentence_length_mean']:.2f} "
            f"sent_len_std={essay['sentence_length_std']:.2f} "
            f"TTR={essay['type_token_ratio']:.3f} "
            f"hapax_rate={essay['hapax_rate']:.3f} "
            f"pos_entropy={essay['pos_bigram_entropy']:.3f} "
            f"cliche_count={essay['cliche_count']} "
            f"transition_opener_rate={essay['transition_opener_rate']:.3f}"
        )
