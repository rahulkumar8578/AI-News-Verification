import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)

# NLP preprocessing function
from nlp_processor import preprocess_text


# ============================================================
# 1. LOAD DATASET
# ============================================================

DATASET_PATH = r"D:/DATASETS/news_dataset.csv"

df = pd.read_csv(DATASET_PATH)

print("\nDataset loaded successfully.")
print("Dataset shape:", df.shape)


# ============================================================
# 2. SELECT REQUIRED COLUMNS
# ============================================================

required_columns = [
    "title",
    "text",
    "subject",
    "date",
    "label"
]

df = df[required_columns]


# ============================================================
# 3. HANDLE MISSING VALUES
# ============================================================

df = df.dropna(subset=["label", "text"])

df["title"] = df["title"].fillna("")
df["subject"] = df["subject"].fillna("")
df["date"] = df["date"].fillna("")


# ============================================================
# 4. KEEP ONLY REAL AND FAKE NEWS
# ============================================================

df["label"] = df["label"].astype(str).str.upper().str.strip()

df = df[
    df["label"].isin(["REAL", "FAKE"])
]


# ============================================================
# 5. REMOVE DUPLICATE NEWS
# ============================================================

df = df.drop_duplicates(
    subset=["title", "text"]
).reset_index(drop=True)


print("\nAfter cleaning:")
print("Dataset shape:", df.shape)

print("\nClass distribution:")
print(df["label"].value_counts())


# ============================================================
# 6. COMBINE TITLE + NEWS TEXT
# ============================================================

df["content"] = (
    df["title"].astype(str)
    + " "
    + df["text"].astype(str)
)


# ============================================================
# 7. NLP PREPROCESSING
# ============================================================

print("\nApplying NLP preprocessing...")

df["processed_content"] = df["content"].apply(
    preprocess_text
)

print("NLP preprocessing completed.")

print("\nOriginal text:")
print(df["content"].iloc[0][:500])

print("\nProcessed text:")
print(df["processed_content"].iloc[0][:500])


# ============================================================
# 8. REMOVE EMPTY PROCESSED TEXT
# ============================================================

df = df[
    df["processed_content"].str.strip() != ""
].reset_index(drop=True)


# ============================================================
# 9. FEATURES AND TARGET
# ============================================================

X = df["processed_content"]
y = df["label"]


# ============================================================
# 10. TRAIN-TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# 11. TF-IDF VECTORIZATION
# ============================================================

print("\nCreating TF-IDF features...")

vectorizer = TfidfVectorizer(
    max_df=0.7
)

X_train_tfidf = vectorizer.fit_transform(
    X_train
)

X_test_tfidf = vectorizer.transform(
    X_test
)

print(
    "TF-IDF training shape:",
    X_train_tfidf.shape
)

print(
    "TF-IDF testing shape:",
    X_test_tfidf.shape
)


# ============================================================
# 12. TRAIN LINEAR SVM MODEL
# ============================================================

print("\nTraining Linear SVM model...")

model = LinearSVC(
    random_state=42
)

model.fit(
    X_train_tfidf,
    y_train
)

print("Model training completed.")


# ============================================================
# 13. MODEL PREDICTION
# ============================================================

y_pred = model.predict(
    X_test_tfidf
)


# ============================================================
# 14. ACCURACY
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n===================================")
print("MODEL PERFORMANCE")
print("===================================")

print(
    f"Accuracy: {accuracy:.4f}"
)

print(
    f"Accuracy Percentage: {accuracy * 100:.2f}%"
)


# ============================================================
# 15. CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred
    )
)


# ============================================================
# 16. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=["FAKE", "REAL"]
)

print("\nConfusion Matrix:")
print(cm)


# Display confusion matrix
disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["FAKE", "REAL"]
)

disp.plot()

plt.title(
    "Fake News Detection - Confusion Matrix"
)

plt.tight_layout()

plt.show()


# ============================================================
# 17. CHECK TRAIN-TEST OVERLAP
# ============================================================

train_set = set(X_train)
test_set = set(X_test)

overlap = train_set.intersection(
    test_set
)

print(
    "\nExact train-test overlap:",
    len(overlap)
)


# ============================================================
# 18. CHECK DUPLICATES IN TRAINING DATA
# ============================================================

duplicate_count = X_train.duplicated().sum()

print(
    "Duplicate texts in training data:",
    duplicate_count
)


# ============================================================
# 19. REMOVE DUPLICATES FROM TRAINING DATA
# ============================================================

if duplicate_count > 0:

    print(
        "\nRemoving duplicate training texts..."
    )

    train_df = pd.DataFrame({
        "text": X_train.values,
        "label": y_train.values
    })

    train_df = train_df.drop_duplicates(
        subset=["text"]
    )

    X_train = train_df["text"]
    y_train = train_df["label"]

    print(
        "Training samples after duplicate removal:",
        len(X_train)
    )

    # Recreate TF-IDF
    vectorizer = TfidfVectorizer(
        max_df=0.7
    )

    X_train_tfidf = vectorizer.fit_transform(
        X_train
    )

    X_test_tfidf = vectorizer.transform(
        X_test
    )

    # Retrain model
    model = LinearSVC(
        random_state=42
    )

    model.fit(
        X_train_tfidf,
        y_train
    )

    # New prediction
    y_pred = model.predict(
        X_test_tfidf
    )

    # New accuracy
    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    print(
        f"\nAccuracy after duplicate removal: "
        f"{accuracy * 100:.2f}%"
    )

    print("\nUpdated Classification Report:")

    print(
        classification_report(
            y_test,
            y_pred
        )
    )

    print("\nUpdated Confusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            y_pred,
            labels=["FAKE", "REAL"]
        )
    )


# ============================================================
# 20. SAVE MODEL AND VECTORIZER
# ============================================================

print("\nSaving trained model...")

joblib.dump(
    model,
    "fake_news_model.pkl"
)

joblib.dump(
    vectorizer,
    "tfidf_vectorizer.pkl"
)

print(
    "fake_news_model.pkl saved successfully."
)

print(
    "tfidf_vectorizer.pkl saved successfully."
)


# ============================================================
# 21. LOAD SAVED MODEL
# ============================================================

print("\nLoading saved model...")

saved_model = joblib.load(
    "fake_news_model.pkl"
)

saved_vectorizer = joblib.load(
    "tfidf_vectorizer.pkl"
)

print("Saved model loaded successfully.")


# ============================================================
# 22. TEST SAMPLE PREDICTIONS
# ============================================================

test_samples = [
    "The government announced a new policy today.",
    "Scientists discovered a new method to improve clean energy.",
    "This fake news example contains completely false information."
]


print("\n===================================")
print("SAMPLE NEWS PREDICTIONS")
print("===================================")


for news in test_samples:

    # Apply SAME NLP preprocessing
    processed_news = preprocess_text(
        news
    )

    # Convert processed text to TF-IDF
    news_tfidf = saved_vectorizer.transform(
        [processed_news]
    )

    # Predict
    prediction = saved_model.predict(
        news_tfidf
    )[0]

    print("\nOriginal News:")
    print(news)

    print("\nProcessed News:")
    print(processed_news)

    print("\nPrediction:")
    print(prediction)

    # Decision score
    if hasattr(saved_model, "decision_function"):

        score = saved_model.decision_function(
            news_tfidf
        )[0]

        print(
            "Decision Score:",
            round(float(score), 4)
        )


# ============================================================
# 23. FINAL MESSAGE
# ============================================================

print("\n===================================")
print("TRAINING COMPLETED SUCCESSFULLY")
print("===================================")

print(
    f"Final Accuracy: {accuracy * 100:.2f}%"
)

print(
    "Model: LinearSVC"
)

print(
    "Feature Extraction: TF-IDF"
)

print(
    "NLP Preprocessing: NLTK"
)

print(
    "Saved Files:"
)

print(
    "1. fake_news_model.pkl"
)

print(
    "2. tfidf_vectorizer.pkl"
)