from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import os

nltk.download("stopwords")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(BASE_DIR, "model", "helpfulness_model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "model", "vectorizer.pkl")

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()


class ReviewInput(BaseModel):
    text: str


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = text.split()
    tokens = [w for w in tokens if w not in stop_words]
    tokens = [w for w in tokens if len(w) > 2]
    tokens = [stemmer.stem(w) for w in tokens]

    return " ".join(tokens)


@app.get("/")
def home():
    return {"message": "Review Helpfulness Predictor API is running"}


@app.post("/predict")
def predict_review(data: ReviewInput):
    processed_text = preprocess_text(data.text)

    # simple rule: very short reviews are usually not informative
    if len(processed_text.split()) < 3:
        return {
            "review": data.text,
            "processed_text": processed_text,
            "prediction": "Not Helpful",
            "confidence": 0.5
        }

    text_vector = vectorizer.transform([processed_text])
    prediction = model.predict(text_vector)[0]
    probability = model.predict_proba(text_vector)[0]

    result = "Helpful" if prediction == 1 else "Not Helpful"

    return {
        "review": data.text,
        "processed_text": processed_text,
        "prediction": result,
        "confidence": round(float(max(probability)), 3)
    }