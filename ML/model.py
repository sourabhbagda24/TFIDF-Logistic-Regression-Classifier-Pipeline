import json
from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from config import LRU_MAXSIZE
from training_data import TRAINING_DATA

# ── Training ──────────────────────────────────────────────────────────────
def train_model():
    texts  = [item[0] for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]
    vectorizer = TfidfVectorizer(
        stop_words="english", lowercase=True, ngram_range=(1, 2)
    )
    X     = vectorizer.fit_transform(texts)
    model = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs")
    model.fit(X, labels)
    return vectorizer, model


vectorizer, model = train_model()


# ── LRU-cached classification ─────────────────────────────────────────────
@lru_cache(maxsize=LRU_MAXSIZE)
def _classify_cached(text: str) -> str:
    X_input = vectorizer.transform([text])
    pred    = model.predict(X_input)[0]
    proba   = model.predict_proba(X_input)[0]
    probs   = {cat: round(proba[i], 4) for i, cat in enumerate(model.classes_)}
    return json.dumps({"category": pred, "probability": probs[pred], "probabilities": probs})


def classify_with_probs(text: str) -> dict:
    if not text.strip():
        return {"category": "Unknown", "probability": 0.0, "probabilities": {}}
    return json.loads(_classify_cached(text.strip()))


def get_cache_info() -> dict:
    info = _classify_cached.cache_info()
    return {
        "hits":    info.hits,
        "misses":  info.misses,
        "size":    info.currsize,
        "maxsize": info.maxsize,
    }