# TF-IDF Logistic Regression Classifier Pipeline

A Flask-based customer lookup and text classification system that uses a pre-trained scikit-learn pipeline (TF-IDF Vectorizer + Logistic Regression) backed by a MySQL database. The app is structured using Flask Blueprints for clean separation of concerns.

---

## How It Works

```
User sends text input
        │
        ▼
  Flask Route (Blueprint)
  src/routes.py  →  main_bp / api_bp
        │
        ▼
  Load Trained Model
  src/model.py  →  classifier_model.pkl
  (TfidfVectorizer + LogisticRegression sklearn Pipeline)
        │
        ▼
  TF-IDF Vectorization
  (convert raw text → weighted term-frequency matrix)
        │
        ▼
  Logistic Regression Prediction
  (output: predicted class label)
        │
        ▼
  Database Lookup (optional)
  src/config.py  →  MySQL via mysql-connector-python
        │
        ▼
  JSON Response returned to client
```

---

## Pipeline Internals

```
Raw Text
   │
   ▼  TfidfVectorizer
   │  - tokenize & lowercase
   │  - remove stop words
   │  - compute TF-IDF scores
   ▼
TF-IDF Matrix
   │
   ▼  LogisticRegression
   │  - trained on labelled data
   │  - predicts class probabilities
   ▼
Predicted Label
```

The full pipeline is serialized and saved as `classifier_model.pkl` using `pickle`. At startup, `load_model()` in `src/model.py` deserializes it into memory.

---

## Project Structure

```
TFIDF-Logistic-Regression-Classifier-Pipeline/
├── src/
│   ├── config.py          # DB_CONFIG — MySQL connection settings
│   ├── model.py           # load_model() — loads classifier_model.pkl
│   └── routes.py          # Flask blueprints: main_bp, api_bp
├── main.py                # App factory — registers blueprints, runs server
├── classifier_model.pkl   # Pre-trained TF-IDF + LogisticRegression pipeline
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project config
└── .python-version        # Python version pin
```

---

## Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/techakash32/TFIDF-Logistic-Regression-Classifier-Pipeline.git
cd TFIDF-Logistic-Regression-Classifier-Pipeline

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure the database
#    Edit src/config.py and update DB_CONFIG with your MySQL credentials

# 4. Run the app
python main.py
```

Server starts at **http://localhost:5000**

---

## Database Config

Edit `src/config.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "your_user",
    "password": "your_password",
    "database": "your_database"
}
```

---

## Dependencies

| Package | Purpose |
|---|---|
| Flask | Web framework |
| scikit-learn | TF-IDF vectorizer + Logistic Regression |
| mysql-connector-python | MySQL database connection |
| nltk | (optional) text preprocessing |

---

## Key Difference from Rule-Based Classifier

| Feature | Rule-Based (v1) | TF-IDF + ML (this project) |
|---|---|---|
| Classification method | Keyword matching | Trained Logistic Regression |
| Learns from data | No | Yes (via `.pkl` model) |
| Database integration | No | Yes (MySQL) |
| Architecture | Single file | Modular (Blueprints + `src/`) |
| Model persistence | None | `classifier_model.pkl` |
