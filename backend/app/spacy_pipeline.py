"""Shared spaCy pipeline.

Both lm_features.py (GPT-2 instrument) and stylometry.py (linguistic feature
extraction) need the same sentence/token boundaries. Loading the model once
here means it's only loaded a single time, and stylometry.py never has to
import GPT-2/Transformers just to get spaCy sentences.
"""

import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError as exc:
    raise RuntimeError(
        "spaCy model 'en_core_web_sm' is not installed. Install it with:\n"
        "    python -m spacy download en_core_web_sm"
    ) from exc
