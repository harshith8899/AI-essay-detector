"""GPT-2 instrumentation: token log-probabilities, perplexity, and burstiness.

This module is an INSTRUMENT ONLY. It does not decide whether an essay is
AI-generated. It only returns measurable numbers (log-probabilities,
perplexity, burstiness) for later phases to interpret.
"""

import statistics

import torch
import torch.nn.functional as F
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

from app.spacy_pipeline import nlp

MODEL_NAME = "gpt2"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = GPT2TokenizerFast.from_pretrained(MODEL_NAME)
model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)
model.to(DEVICE)
model.eval()

# GPT-2's fixed attention window. Any token further back than this many
# positions cannot be attended to, no matter how the input is chunked.
MAX_CONTEXT = model.config.n_positions


def _token_logprobs(input_ids: torch.Tensor) -> torch.Tensor:
    """Log-prob of each token given everything before it, via a sliding window.

    `input_ids` is a 1D tensor whose first element is a synthetic
    beginning-of-context token (GPT-2's <|endoftext|>) followed by the
    essay's real tokens. This lets the very first essay token also get a
    conditional log-probability instead of being undefined.

    Returns a 1D tensor the same length as `input_ids`, where index 0 is
    NaN (no context exists for the leading token) and index i (i >= 1) is
    log P(input_ids[i] | input_ids[0:i]).

    GPT-2 can only attend to MAX_CONTEXT tokens at once. When the sequence
    is longer than that, it is scored in overlapping windows: each window
    reuses the tail of the previous one as context, so every token is
    scored with as much preceding context as fits in the window (up to
    MAX_CONTEXT - 1 tokens) rather than the model silently truncating
    everything down to a single MAX_CONTEXT-sized prefix of the essay.
    """
    seq_len = input_ids.size(0)
    log_probs = torch.full((seq_len,), float("nan"), dtype=torch.float32)

    stride = MAX_CONTEXT // 2
    prev_end = 0
    begin = 0
    while True:
        end = min(begin + MAX_CONTEXT, seq_len)
        chunk = input_ids[begin:end].unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            logits = model(chunk).logits[0]

        chunk_log_probs = F.log_softmax(logits[:-1], dim=-1)
        chunk_targets = chunk[0, 1:]
        token_lp = chunk_log_probs.gather(-1, chunk_targets.unsqueeze(-1)).squeeze(-1)

        new_start_in_chunk = max(prev_end - (begin + 1), 0)
        abs_start = begin + 1 + new_start_in_chunk
        log_probs[abs_start:end] = token_lp[new_start_in_chunk:].to("cpu")

        prev_end = end
        if end == seq_len:
            break
        begin += stride

    return log_probs


def _empty_result() -> dict:
    return {
        "sentences": [],
        "essay": {
            "mean_perplexity": None,
            "burstiness": None,
            "sentence_count": 0,
            "token_count": 0,
        },
    }


def analyze_lm_features(essay: str) -> dict:
    """Compute GPT-2-based token/sentence/essay statistics for `essay`.

    Pure function: no classification, no thresholds, no verdict. Every
    token's log-probability is conditioned on the real preceding essay
    text (via `_token_logprobs`), not computed sentence-by-sentence in
    isolation.
    """
    if not essay or not essay.strip():
        return _empty_result()

    doc = nlp(essay)
    sentences = [
        {"text": sent.text, "start_offset": sent.start_char, "end_offset": sent.end_char}
        for sent in doc.sents
        if sent.end_char > sent.start_char
    ]
    if not sentences:
        return _empty_result()

    encoding = tokenizer(essay, return_offsets_mapping=True, add_special_tokens=False)
    essay_token_ids = encoding["input_ids"]
    offsets = encoding["offset_mapping"]

    if not essay_token_ids:
        return _empty_result()

    bos_id = tokenizer.bos_token_id
    full_ids = torch.tensor([bos_id] + essay_token_ids, dtype=torch.long)
    all_log_probs = _token_logprobs(full_ids)
    token_logprobs = all_log_probs[1:].tolist()  # drop the synthetic BOS slot

    sentence_logprobs = [[] for _ in sentences]
    si = 0
    for (tok_start, tok_end), lp in zip(offsets, token_logprobs):
        while si < len(sentences) - 1 and tok_start >= sentences[si]["end_offset"]:
            si += 1
        if sentences[si]["start_offset"] <= tok_start < sentences[si]["end_offset"]:
            sentence_logprobs[si].append(lp)

    sentence_results = []
    sentence_perplexities = []
    for sent, lps in zip(sentences, sentence_logprobs):
        token_count = len(lps)
        if token_count == 0:
            mean_logprob = None
            perplexity = None
        else:
            mean_logprob = sum(lps) / token_count
            perplexity = float(torch.exp(torch.tensor(-mean_logprob)))
            sentence_perplexities.append(perplexity)
        sentence_results.append(
            {
                "text": sent["text"],
                "start_offset": sent["start_offset"],
                "end_offset": sent["end_offset"],
                "mean_logprob": mean_logprob,
                "perplexity": perplexity,
                "token_count": token_count,
            }
        )

    if sentence_perplexities:
        mean_perplexity = statistics.mean(sentence_perplexities)
        # Population standard deviation (divide by N, not N-1): the sentences
        # in this essay are the entire population we're measuring burstiness
        # over, not a sample drawn from a larger population.
        burstiness = statistics.pstdev(sentence_perplexities) if len(sentence_perplexities) > 1 else 0.0
    else:
        mean_perplexity = None
        burstiness = None

    return {
        "sentences": sentence_results,
        "essay": {
            "mean_perplexity": mean_perplexity,
            "burstiness": burstiness,
            "sentence_count": len(sentence_results),
            "token_count": len(essay_token_ids),
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

    for label, paragraph in [("HUMAN-STYLE PARAGRAPH", human_paragraph), ("AI-STYLE PARAGRAPH", ai_paragraph)]:
        print(f"\n=== {label} ===")
        result = analyze_lm_features(paragraph)
        for sent in result["sentences"]:
            print(f"- text: {sent['text']!r}")
            print(f"  token_count: {sent['token_count']}")
            print(f"  mean_logprob: {sent['mean_logprob']}")
            print(f"  perplexity: {sent['perplexity']}")
        print(f"essay mean_perplexity: {result['essay']['mean_perplexity']}")
        print(f"essay burstiness: {result['essay']['burstiness']}")
