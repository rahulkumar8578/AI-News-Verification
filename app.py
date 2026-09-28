from flask import (
    Flask,
    request,
    jsonify,
    render_template
)

import joblib

from news_search import search_news
from claim_verifier import verify_claim

# ============================================================
# NLP PREPROCESSING
# ============================================================

from nlp_processor import preprocess_text


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# LOAD ML MODEL
# ============================================================

print("=" * 60)
print("Loading fake news classification model...")
print("=" * 60)

model = joblib.load(
    "fake_news_model.pkl"
)

vectorizer = joblib.load(
    "tfidf_vectorizer.pkl"
)

print("Fake news classification model loaded!")
print("=" * 60)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# PREDICT
# ============================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    try:

        # ====================================================
        # GET JSON DATA
        # ====================================================

        data = request.get_json()

        if not data:

            return jsonify({

                "error":
                    "No data received."

            }), 400


        # ====================================================
        # GET HEADLINE
        # ====================================================

        headline = str(
            data.get(
                "headline",
                ""
            )
        ).strip()


        # ====================================================
        # GET NEWS CONTENT
        # ====================================================

        news = str(
            data.get(
                "news",
                ""
            )
        ).strip()


        # ====================================================
        # VALIDATION
        # ====================================================

        if not headline and not news:

            return jsonify({

                "error":
                    "Please enter a headline or news content."

            }), 400


        # ====================================================
        # COMBINE HEADLINE + NEWS
        # ====================================================

        combined_text = (
            headline
            + " "
            + news
        ).strip()


        # ====================================================
        # ML MODEL PREDICTION
        # ====================================================

        print()
        print("=" * 60)
        print("STARTING ML MODEL PREDICTION")
        print("=" * 60)

        print(
            "Original News:",
            combined_text[:500]
        )


        # ====================================================
        # NLP PREPROCESSING
        # ====================================================
        # IMPORTANT:
        # Same NLP preprocessing used during model training
        # is applied here before TF-IDF prediction.
        # ====================================================

        processed_text = preprocess_text(
            combined_text
        )

        print(
            "NLP Processed Text:",
            processed_text[:500]
        )


        # ====================================================
        # CONVERT TEXT INTO TF-IDF
        # ====================================================

        tfidf_text = vectorizer.transform(
            [processed_text]
        )


        # ====================================================
        # PREDICT REAL / FAKE
        # ====================================================

        model_prediction = model.predict(
            tfidf_text
        )[0]


        # Convert prediction to string
        model_prediction = str(
            model_prediction
        ).upper()


        # ====================================================
        # ML DECISION SCORE
        # ====================================================

        decision_score = 0.0

        if hasattr(
            model,
            "decision_function"
        ):

            decision_score = model.decision_function(
                tfidf_text
            )[0]


        print(
            "ML MODEL PREDICTION:",
            model_prediction
        )

        print(
            "ML DECISION SCORE:",
            decision_score
        )

        print("=" * 60)


        # ====================================================
        # CLAIM FOR WEB VERIFICATION
        # ====================================================

        claim = headline

        if not claim:

            claim = news[:500]


        # ====================================================
        # WEB SEARCH
        # ====================================================

        print()
        print("=" * 60)
        print("STARTING WEB SEARCH")
        print("=" * 60)

        print(
            "Headline:",
            headline
        )

        print(
            "Claim:",
            claim
        )

        print("=" * 60)


        search_data = search_news(
            headline,
            news
        )


        # ====================================================
        # WEB CLAIM VERIFICATION
        # ====================================================

        print()
        print("=" * 60)
        print("STARTING WEB VERIFICATION")
        print("=" * 60)


        verification = verify_claim(
            claim,
            search_data
        )


        # ====================================================
        # WEB PREDICTION
        # ====================================================

        web_prediction = verification.get(
            "status",
            "UNCERTAIN"
        )


        web_prediction = str(
            web_prediction
        ).upper()


        web_confidence = verification.get(
            "confidence",
            50
        )


        web_reason = verification.get(
            "reason",
            "Unable to verify the claim."
        )


        # ====================================================
        # FINAL TERMINAL OUTPUT
        # ====================================================

        print()
        print("=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)

        print()

        print(
            "ML MODEL PREDICTION :",
            model_prediction
        )

        print(
            "WEB PREDICTION      :",
            web_prediction
        )

        print(
            "WEB CONFIDENCE      :",
            web_confidence,
            "%"
        )

        print(
            "WEB REASON          :",
            web_reason
        )

        print()
        print("=" * 60)


        # ====================================================
        # SEND BOTH RESULTS TO FRONTEND
        # ====================================================

        return jsonify({

            # =================================================
            # ML MODEL
            # =================================================

            "model_prediction":
                model_prediction,

            "decision_score":
                float(
                    decision_score
                ),


            # =================================================
            # WEB VERIFICATION
            # =================================================

            "web_prediction":
                web_prediction,

            "web_confidence":
                int(
                    web_confidence
                ),

            "web_reason":
                web_reason,


            # =================================================
            # WEB SEARCH INFORMATION
            # =================================================

            "web_answer":
                search_data.get(
                    "answer",
                    ""
                ),

            "search_queries":
                search_data.get(
                    "queries",
                    []
                ),

            "sources":
                search_data.get(
                    "results",
                    []
                ),


            # =================================================
            # VERIFIED EVIDENCE
            # =================================================

            "verification_evidence":
                verification.get(
                    "evidence",
                    []
                )
        })


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as error:

        print()
        print("=" * 60)
        print("PREDICTION ERROR")
        print("=" * 60)

        print(
            str(error)
        )

        print("=" * 60)


        return jsonify({

            "error":
                str(error)

        }), 500


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI NEWS VERIFICATION SYSTEM")
    print("=" * 60)

    print(
        "Server running at:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print("=" * 60)


    app.run(
        debug=True
    )