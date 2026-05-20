# AI-Powered Review Helpfulness Prediction System

An intelligent full-stack review analytics platform that combines:

- Information Retrieval (IR)
- Machine Learning
- Natural Language Processing (NLP)
- AI-powered review analysis

The system predicts whether a review is helpful or not while also performing sentiment analysis, keyword extraction, summarization, and IR-based search.

---

# Features

## Product Layer

### Dashboard Overview
- Total reviews
- Helpful vs not helpful statistics
- Average rating
- Most reviewed item
- Review analytics

### AI Review Analysis
- Helpfulness prediction
- Sentiment analysis
- Confidence analysis
- AI-generated summary
- Keyword extraction
- Hybrid AI reasoning

### IR Search Engine
- Search reviews by keywords
- Retrieve relevant reviews
- AI prediction for retrieved reviews
- Review filtering and comparison

### Insights & Comparison
- Helpful vs not helpful comparison
- Average rating analysis
- Word count analysis
- Review behavior insights

---

# AI Integration Layer

The system integrates multiple AI/NLP tasks:

- TF-IDF feature extraction
- Logistic Regression classification
- Naive Bayes comparison
- Sentiment analysis
- Keyword extraction
- Text summarization
- Hybrid rule-based AI reasoning

---

# Technologies Used

## Backend
- FastAPI
- Python
- Scikit-learn
- Pandas
- NLTK

## Frontend
- HTML
- CSS
- JavaScript

## Machine Learning
- TF-IDF Vectorization
- Logistic Regression
- Multinomial Naive Bayes

---

# Dataset

The dataset was collected from Steam reviews using Selenium-based scraping while respecting robots.txt rules.

Collected data includes:
- Review text
- Rating
- Helpful votes
- Review metadata
- Game/item name

---

# Machine Learning Pipeline

1. Data Collection
2. Data Cleaning
3. Text Preprocessing
4. Feature Extraction using TF-IDF
5. Model Training
6. AI Analysis Integration
7. Full-stack Deployment

---

# Data Preprocessing

The preprocessing pipeline includes:

- Lowercasing
- Removing URLs
- Removing HTML tags
- Removing punctuation
- Removing numbers
- Stopword removal
- Stemming using Porter Stemmer
- Duplicate removal
- Empty review filtering

---

# Feature Extraction

Extracted features include:

- TF-IDF vectors
- Word count
- Text length
- Helpfulness score
- Sentiment signals
- Keywords

---

# Model Evaluation

## Logistic Regression
- Test Accuracy: ~98%
- Cross Validation Accuracy: ~94%

## Naive Bayes
- Test Accuracy: ~99%

Evaluation metrics:
- Accuracy
- Precision
- Recall
- F1-score
- Confusion Matrix
- Cross Validation

---

# Hybrid AI System

The final system uses a hybrid AI approach:

- Machine Learning prediction
- Rule-based intelligence
- Sentiment-aware analysis
- Detail-aware helpfulness detection

This improves real-world review understanding.

---

# API Endpoints

## GET /
Health check endpoint

## GET /stats
Returns dashboard statistics

## POST /predict
Predicts review helpfulness

## POST /analyze
Performs:
- prediction
- sentiment analysis
- summarization
- keyword extraction

## POST /search
IR-based review search

## GET /comparison
Returns helpful vs not helpful analytics

---

# Project Structure

```bash
review-helpfulness/
│
├── backend/
├── frontend/
├── data/
├── model/
├── scripts/
├── notebooks/
└── README.md
```

---

# Running the Project

## Backend

```bash
cd backend
python -m uvicorn app:app --reload --port 8001
```

## Frontend

```bash
cd frontend
python -m http.server 5500
```

Frontend:
http://127.0.0.1:5500

Backend:
http://127.0.0.1:8001

---

# Future Improvements

- Deep Learning models
- Real-time review streaming
- Transformer-based summarization
- Recommendation systems
- Multi-language support

---

# Authors
Developed as an AI + Information Retrieval academic project.