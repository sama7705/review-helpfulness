import os
import pickle
import re
from collections import Counter
from typing import Optional

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(title="AI Review Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

DATA_PATH = os.path.join(PROJECT_DIR, "data", "clean_reviews.csv")
MODEL_PATH = os.path.join(PROJECT_DIR, "model", "helpfulness_model.pkl")
VECTORIZER_PATH = os.path.join(PROJECT_DIR, "model", "vectorizer.pkl")


df = pd.read_csv(DATA_PATH)

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(VECTORIZER_PATH, "rb") as f:
    vectorizer = pickle.load(f)


class ReviewInput(BaseModel):
    review: Optional[str] = None
    text: Optional[str] = None


class SearchInput(BaseModel):
    query: str


def get_review_text(data: ReviewInput):
    return data.review or data.text or ""


STOP_WORDS = {
    "the", "and", "for", "with", "this", "that", "you", "your", "are", "was",
    "were", "have", "has", "had", "but", "not", "from", "they", "them", "its",
    "into", "about", "after", "before", "because", "there", "their", "would",
    "could", "should", "game", "review", "play", "played", "playing", "very",
    "also", "really", "just", "like", "will", "can", "get", "got", "one",
    "two", "much", "many", "more", "most", "some", "than", "then", "alot",
    "used", "check", "different"
}

POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "fun", "best", "love", "liked",
    "awesome", "positive", "recommend", "enjoy", "smooth", "beautiful",
    "fast", "easy", "helpful", "perfect", "fantastic", "responsive",
    "satisfied", "cheap", "worth", "wonderful", "nice", "friendly",
    "comfortable", "reliable", "impressive", "quality", "quick", "clean",
    "safe", "strong", "useful", "clear", "detailed", "simple", "fair",
    "organized", "trusted", "accurate"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "boring", "bug", "bugs", "crash", "crashes",
    "hate", "negative", "broken", "poor", "worst", "refund", "lag", "toxic",
    "slow", "expensive", "scam", "fraud", "disappointed", "dirty",
    "problem", "problems", "issues", "issue", "annoying", "fake", "late",
    "uncomfortable", "unusable", "waste", "damaged", "horrible",
    "delay", "delayed", "spam", "rude", "error", "errors", "difficult",
    "confusing", "missing", "weak", "useless", "cheat", "cheaters"
}

DETAIL_WORDS = {
    "because", "experience", "customer", "service", "delivery", "price",
    "prices", "problem", "quality", "support", "website", "products",
    "product", "details", "refund", "order", "shipping", "booking",
    "hotel", "room", "payment", "account", "received", "arrived",
    "clear", "process", "platform", "company", "compare", "decision"
}


def clean_words(text: str):
    return re.findall(r"[a-zA-Z]+", str(text).lower())


def get_prediction(review_text: str):
    text_vector = vectorizer.transform([review_text])
    raw_prediction = int(model.predict(text_vector)[0])
    probability = model.predict_proba(text_vector)[0]

    not_helpful_prob = round(float(probability[0]), 3)
    helpful_prob = round(float(probability[1]), 3)

    words = clean_words(review_text)
    word_count = len(words)

    detail_score = sum(1 for word in words if word in DETAIL_WORDS)
    positive_count = sum(1 for word in words if word in POSITIVE_WORDS)
    negative_count = sum(1 for word in words if word in NEGATIVE_WORDS)

    prediction = raw_prediction
    decision_method = "ML model"

    # Rule 1: very short reviews are usually not helpful
    if word_count <= 5:
        prediction = 0
        decision_method = "Short review override"

    # Rule 2: if ML is uncertain but the review has useful details, mark helpful
    elif helpful_prob >= 0.40 and word_count >= 18 and detail_score >= 3:
        prediction = 1
        decision_method = "Hybrid ML + detail-based rule"

    # Rule 3: detailed complaints are often helpful because they explain the problem
    elif helpful_prob >= 0.35 and word_count >= 25 and negative_count >= 2 and detail_score >= 2:
        prediction = 1
        decision_method = "Hybrid ML + detailed complaint rule"

    confidence_gap = abs(helpful_prob - not_helpful_prob)

    if confidence_gap < 0.10:
        confidence_level = "Low Confidence"
    elif confidence_gap < 0.25:
        confidence_level = "Medium Confidence"
    else:
        confidence_level = "High Confidence"

    return {
        "prediction": "Helpful" if prediction == 1 else "Not Helpful",
        "raw_model_prediction": "Helpful" if raw_prediction == 1 else "Not Helpful",
        "not_helpful_probability": not_helpful_prob,
        "helpful_probability": helpful_prob,
        "confidence_level": confidence_level,
        "confidence_gap": round(confidence_gap, 3),
        "decision_method": decision_method,
        "detail_score": detail_score,
        "positive_word_count": positive_count,
        "negative_word_count": negative_count,
        "word_count": word_count
    }


def label_name(value):
    return "Helpful" if int(value) == 1 else "Not Helpful"


def get_sentiment(text: str):
    words = clean_words(text)

    positive_count = sum(1 for word in words if word in POSITIVE_WORDS)
    negative_count = sum(1 for word in words if word in NEGATIVE_WORDS)

    total = positive_count + negative_count

    if total == 0:
        return {
            "label": "Neutral",
            "score": 0,
            "positive_words": positive_count,
            "negative_words": negative_count
        }

    sentiment_score = round((positive_count - negative_count) / total, 2)

    if sentiment_score >= 0.30:
        label = "Positive"
    elif sentiment_score <= -0.30:
        label = "Negative"
    else:
        label = "Mixed"

    return {
        "label": label,
        "score": sentiment_score,
        "positive_words": positive_count,
        "negative_words": negative_count
    }


def extract_keywords(text: str, limit: int = 8):
    words = re.findall(r"[a-zA-Z]{4,}", str(text).lower())

    useful_words = [
        word for word in words
        if word not in STOP_WORDS
    ]

    keywords = [
        word for word, count in Counter(useful_words).most_common(limit)
        if len(word) > 3
    ]

    return keywords


def summarize_text(text: str, max_length: int = 250):
    text = str(text).strip()

    if not text:
        return "No review text provided."

    sentences = re.split(r"(?<=[.!?])\s+", text)

    scored_sentences = []

    for sentence in sentences:
        words = clean_words(sentence)

        sentiment_score = sum(
            1 for word in words
            if word in POSITIVE_WORDS or word in NEGATIVE_WORDS
        )

        detail_score = sum(
            1 for word in words
            if word in DETAIL_WORDS
        )

        length_score = min(len(words) / 20, 1)

        total_score = sentiment_score + detail_score + length_score

        scored_sentences.append((sentence, total_score))

    scored_sentences.sort(key=lambda x: x[1], reverse=True)

    summary = scored_sentences[0][0] if scored_sentences else text

    if len(summary) > max_length:
        summary = summary[:max_length].rsplit(" ", 1)[0] + "..."

    return summary


def generate_ai_notes(review_text: str, prediction: str, sentiment: str, decision_method: str):
    words = clean_words(review_text)
    word_count = len(words)
    detail_score = sum(1 for word in words if word in DETAIL_WORDS)

    notes = []

    if word_count <= 5:
        notes.append("The review is very short, so it is classified as not helpful.")
    elif word_count >= 40:
        notes.append("The review contains strong detail for analysis.")
    elif word_count >= 18:
        notes.append("The review contains moderate detail.")
    else:
        notes.append("The review is short, so the prediction may be less confident.")

    if detail_score >= 3:
        notes.append("The review includes useful information such as service, delivery, price, product, or support details.")

    if sentiment == "Mixed":
        notes.append("The review contains both positive and negative signals.")
    elif sentiment == "Positive":
        notes.append("The review contains mostly positive expressions.")
    elif sentiment == "Negative":
        notes.append("The review contains mostly negative expressions.")
    else:
        notes.append("The review does not contain strong sentiment words.")

    notes.append(f"Final decision method: {decision_method}.")

    return notes


@app.get("/")
def home():
    return {
        "message": "AI Review Intelligence API is running",
        "status": "active"
    }


@app.post("/predict")
def predict(data: ReviewInput):
    review_text = get_review_text(data)
    return get_prediction(review_text)


@app.get("/stats")
def stats():
    games = df["item_name"].value_counts()

    return {
        "total_reviews": int(len(df)),
        "helpful_reviews": int((df["helpful_label"] == 1).sum()),
        "not_helpful_reviews": int((df["helpful_label"] == 0).sum()),
        "average_rating": round(float(df["rating"].mean()), 2),
        "number_of_games": int(df["item_name"].nunique()),
        "most_reviewed_item": games.index[0] if not games.empty else "N/A",
        "games": games.head(10).to_dict(),
    }


@app.post("/search")
def search(data: SearchInput):
    query = data.query.lower().strip()

    if not query:
        return []

    results = df[
        df["clean_text"].str.contains(query, na=False, regex=False)
    ].head(10)

    output = []

    for _, row in results.iterrows():
        review_text = str(row["review_text"])
        prediction = get_prediction(review_text)

        output.append({
            "review_id": int(row["review_id"]),
            "item_name": row["item_name"],
            "review_text": review_text,
            "rating": int(row["rating"]),
            "helpful_votes": int(row["helpful_votes"]),
            "dataset_label": label_name(row["helpful_label"]),
            "ai_prediction": prediction["prediction"],
            "helpful_probability": prediction["helpful_probability"],
            "not_helpful_probability": prediction["not_helpful_probability"],
            "confidence_level": prediction["confidence_level"],
            "decision_method": prediction["decision_method"],
        })

    return output


@app.get("/comparison")
def comparison():
    helpful_df = df[df["helpful_label"] == 1]
    not_helpful_df = df[df["helpful_label"] == 0]
    total_reviews = len(df)

    return {
        "helpful": {
            "count": int(len(helpful_df)),
            "percentage": round(float(len(helpful_df) / total_reviews * 100), 2),
            "average_rating": round(float(helpful_df["rating"].mean()), 2),
            "average_word_count": round(float(helpful_df["word_count"].mean()), 2),
        },
        "not_helpful": {
            "count": int(len(not_helpful_df)),
            "percentage": round(float(len(not_helpful_df) / total_reviews * 100), 2),
            "average_rating": round(float(not_helpful_df["rating"].mean()), 2),
            "average_word_count": round(float(not_helpful_df["word_count"].mean()), 2),
        },
        "explanation": (
            "Helpful and not helpful reviews are compared using count, percentage, "
            "average rating, and average word count. This supports the product's "
            "comparison layer and shows how review behavior differs between classes."
        ),
    }


@app.post("/analyze")
def analyze(data: ReviewInput):
    review_text = get_review_text(data)

    prediction = get_prediction(review_text)
    sentiment = get_sentiment(review_text)
    keywords = extract_keywords(review_text)
    summary = summarize_text(review_text)

    return {
        **prediction,
        "sentiment": sentiment["label"],
        "sentiment_score": sentiment["score"],
        "sentiment_positive_word_count": sentiment["positive_words"],
        "sentiment_negative_word_count": sentiment["negative_words"],
        "keywords": keywords,
        "summary": summary,
        "ai_notes": generate_ai_notes(
            review_text,
            prediction["prediction"],
            sentiment["label"],
            prediction["decision_method"]
        )
    }