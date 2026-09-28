# AI News Verification System

AI News Verification System is a Flask-based web application that checks whether a news article or claim is likely to be **REAL, FAKE, or UNCERTAIN**.

The system combines:

- Machine Learning
- NLP preprocessing
- TF-IDF text classification
- Web-based news search
- Claim verification
- Evidence collection
- Flask web interface

The project is optimized to run on low-resource hosting platforms such as the Render Free tier.

---

## Features

- Fake news detection using a trained Machine Learning model
- Headline and news content analysis
- NLP text preprocessing
- TF-IDF feature extraction
- REAL / FAKE prediction
- Web search for supporting evidence
- Claim verification
- Confidence score
- Verification reason
- Evidence/source display
- Flask REST API
- Responsive web interface
- Lightweight deployment configuration

---

## How the System Works

The system follows this workflow:

```text
User enters news
        ↓
Headline + News Content
        ↓
NLP Preprocessing
        ↓
TF-IDF Vectorization
        ↓
Machine Learning Model
        ↓
ML Prediction
        ↓
Web Search
        ↓
Evidence Collection
        ↓
Claim Verification
        ↓
Final Result
        ↓
REAL / FAKE / UNCERTAIN
