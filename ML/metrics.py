from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)

from training_data import TRAINING_DATA


def compute_metrics() -> dict:
    texts  = [item[0] for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    vec = TfidfVectorizer(stop_words="english", lowercase=True, ngram_range=(1, 2))
    clf = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs")
    clf.fit(vec.fit_transform(X_train), y_train)

    y_pred = clf.predict(vec.transform(X_test))
    acc          = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="macro")
    cm           = confusion_matrix(y_test, y_pred, labels=clf.classes_)

    return {
        "accuracy":         round(acc,  4),
        "precision_macro":  round(prec, 4),
        "recall_macro":     round(rec,  4),
        "f1_macro":         round(f1,   4),
        "confusion_matrix": cm.tolist(),
        "classes":          list(clf.classes_),
    }


# Computed once at import time
metrics = compute_metrics()