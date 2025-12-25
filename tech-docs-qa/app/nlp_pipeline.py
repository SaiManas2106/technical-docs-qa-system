import re
from typing import List, Dict
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# Simple semantic normalization map example
NORMALIZATION_MAP = {
    "PCB": "printed circuit board",
    "pcbs": "printed circuit board",
    "Power supply": "power_supply"
}

def normalize_text(text: str) -> str:
    text = text.strip()
    for k, v in NORMALIZATION_MAP.items():
        text = re.sub(r'\b' + re.escape(k) + r'\b', v, text, flags=re.IGNORECASE)
    return text

def extract_entities(text: str) -> List[Dict]:
    """Return a list of entities with type and span.
    Uses spaCy if available, otherwise simple regex heuristics for component-like entities.
    """
    if nlp:
        doc = nlp(text)
        ents = []
        for ent in doc.ents:
            ents.append({"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char})
        return ents
    # fallback simple heuristic: components often capitalized words with numbers or hyphens
    pattern = r'([A-Z][A-Za-z0-9\-]{2,})'
    matches = re.finditer(pattern, text)
    ents = []
    for m in matches:
        ents.append({"text": m.group(1), "label": "COMPONENT", "start": m.start(1), "end": m.end(1)})
    return ents