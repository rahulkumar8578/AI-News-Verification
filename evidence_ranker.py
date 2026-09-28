import re
from urllib.parse import urlparse
from datetime import datetime


# ============================================================
# TEXT UTILITIES
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = str(text)

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def tokenize(text):

    text = clean_text(text).lower()

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text
    )

    # Remove very common words
    stop_words = {
        "the",
        "is",
        "are",
        "was",
        "were",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "for",
        "with",
        "by",
        "from",
        "this",
        "that",
        "has",
        "have",
        "had",
        "be",
        "been",
        "will",
        "would",
        "can",
        "could",
        "should"
    }

    return set(
        word
        for word in words
        if len(word) >= 3
        and word not in stop_words
    )


# ============================================================
# DOMAIN INFORMATION
# ============================================================

def get_domain(url):

    if not url:
        return ""

    try:

        domain = urlparse(
            url
        ).netloc.lower()

        domain = domain.replace(
            "www.",
            ""
        )

        return domain

    except Exception:

        return ""


# ============================================================
# SOURCE RELIABILITY
# ============================================================

def source_reliability(url):

    domain = get_domain(
        url
    )

    if not domain:
        return 1.0


    # --------------------------------------------------------
    # OFFICIAL GOVERNMENT
    # --------------------------------------------------------

    official_domains = [

        "pib.gov.in",
        "indiapost.gov.in",
        "india.gov.in",
        "mygov.in",
        "nic.in",
        "mha.gov.in",
        "mea.gov.in",
        "mohfw.gov.in",
        "education.gov.in",
        "finance.gov.in"
    ]


    for item in official_domains:

        if (
            domain == item
            or domain.endswith(
                "." + item
            )
        ):

            return 1.60


    # --------------------------------------------------------
    # FACT CHECK SOURCES
    # --------------------------------------------------------

    fact_check_domains = [

        "altnews.in",
        "boomlive.in",
        "factly.in",
        "newsmeter.in",
        "vishvasnews.com",
        "afp.com"
    ]


    for item in fact_check_domains:

        if (
            domain == item
            or domain.endswith(
                "." + item
            )
        ):

            return 1.50


    # --------------------------------------------------------
    # TRUSTED NEWS
    # --------------------------------------------------------

    trusted_news = [

        "reuters.com",
        "bbc.com",
        "bbc.co.uk",
        "thehindu.com",
        "indianexpress.com",
        "hindustantimes.com",
        "ndtv.com",
        "timesofindia.indiatimes.com",
        "newsonair.gov.in",
        "indiatoday.in",
        "theprint.in",
        "news18.com"
    ]


    for item in trusted_news:

        if (
            domain == item
            or domain.endswith(
                "." + item
            )
        ):

            return 1.25


    return 1.0


# ============================================================
# FACT CHECK TERMS
# ============================================================

FACT_CHECK_TERMS = [

    "fact check",
    "fact-check",
    "factcheck",
    "pib fact check",
    "debunked",
    "debunks",
    "refuted",
    "refutes"
]


# ============================================================
# SUPPORT TERMS
# ============================================================

SUPPORT_TERMS = [

    "confirmed",
    "officially confirmed",
    "announced",
    "official announcement",
    "verified",
    "approved",
    "according to official",
    "government confirmed",
    "pib confirmed"
]


# ============================================================
# REFUTATION TERMS
#
# IMPORTANT:
# These terms are NOT used to increase evidence ranking.
# They are only reported as metadata.
# ============================================================

REFUTATION_TERMS = [

    "fake",
    "false",
    "fraudulent",
    "fabricated",
    "debunked",
    "refuted",
    "misleading",
    "hoax",
    "scam",
    "no connection",
    "no association",
    "not associated",
    "not affiliated",
    "does not exist",
    "doesn't exist",
    "not true",
    "untrue"
]


# ============================================================
# KEYWORD MATCHING
# ============================================================

def count_keyword_matches(
    text,
    terms
):

    text = clean_text(
        text
    ).lower()

    matches = []

    for term in terms:

        if term in text:

            matches.append(
                term
            )

    return matches


# ============================================================
# CLAIM / EVIDENCE OVERLAP
# ============================================================

def calculate_overlap(
    claim,
    evidence
):

    claim_words = tokenize(
        claim
    )

    evidence_words = tokenize(
        evidence
    )

    if not claim_words:

        return 0.0


    common = (
        claim_words.intersection(
            evidence_words
        )
    )


    return (
        len(common)
        /
        len(claim_words)
    )


# ============================================================
# IMPORTANT WORD MATCH
# ============================================================

def calculate_important_overlap(
    claim,
    evidence
):

    claim_words = tokenize(
        claim
    )

    evidence_words = tokenize(
        evidence
    )

    if not claim_words:

        return 0.0


    common = (
        claim_words.intersection(
            evidence_words
        )
    )


    # Require at least some meaningful
    # claim information to appear.
    if len(claim_words) <= 3:

        return (
            len(common)
            /
            len(claim_words)
        )


    if len(common) < 2:

        return 0.0


    return (
        len(common)
        /
        len(claim_words)
    )


# ============================================================
# DATE PARSING
# ============================================================

def parse_date(value):

    if not value:

        return None


    value = clean_text(
        value
    )


    formats = [

        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%B %d, %Y",
        "%b %d, %Y"
    ]


    for fmt in formats:

        try:

            return datetime.strptime(
                value,
                fmt
            )

        except Exception:

            pass


    return None


# ============================================================
# RECENCY SCORE
# ============================================================

def recency_score(
    date_value
):

    date = parse_date(
        date_value
    )

    if date is None:

        return 1.0


    now = datetime.now()

    days = max(
        0,
        (now - date).days
    )


    if days <= 7:

        return 1.20


    if days <= 30:

        return 1.15


    if days <= 90:

        return 1.10


    if days <= 365:

        return 1.05


    return 1.0


# ============================================================
# EVIDENCE SCORE
# ============================================================

def calculate_evidence_score(
    claim,
    result,
    nli_scores=None
):

    title = clean_text(
        result.get(
            "title",
            ""
        )
    )


    content = clean_text(
        result.get(
            "content",
            ""
        )
    )


    url = clean_text(
        result.get(
            "url",
            ""
        )
    )


    date = result.get(
        "published_date",
        ""
    )


    evidence = (
        title
        + ". "
        + content
    )


    # --------------------------------------------------------
    # SOURCE RELIABILITY
    # --------------------------------------------------------

    reliability = source_reliability(
        url
    )


    # --------------------------------------------------------
    # CLAIM OVERLAP
    # --------------------------------------------------------

    overlap = calculate_overlap(
        claim,
        evidence
    )


    important_overlap = calculate_important_overlap(
        claim,
        evidence
    )


    # --------------------------------------------------------
    # KEYWORDS
    # --------------------------------------------------------

    fact_matches = count_keyword_matches(
        evidence,
        FACT_CHECK_TERMS
    )


    refutation_matches = count_keyword_matches(
        evidence,
        REFUTATION_TERMS
    )


    support_matches = count_keyword_matches(
        evidence,
        SUPPORT_TERMS
    )


    # --------------------------------------------------------
    # NLI
    # --------------------------------------------------------

    entailment = 0.0
    contradiction = 0.0
    neutral = 1.0


    if nli_scores:

        entailment = float(
            nli_scores.get(
                "entailment",
                0
            )
        )


        contradiction = float(
            nli_scores.get(
                "contradiction",
                0
            )
        )


        neutral = float(
            nli_scores.get(
                "neutral",
                0
            )
        )


    # --------------------------------------------------------
    # RECENCY
    # --------------------------------------------------------

    recency = recency_score(
        date
    )


    # ========================================================
    # NEW RANKING FORMULA
    # ========================================================

    score = 0.0


    # Main importance:
    # Is the article actually about the claim?
    score += important_overlap * 50


    # General word overlap
    score += overlap * 15


    # Reliable source
    score += reliability * 10


    # NLI support
    score += entailment * 20


    # NLI contradiction
    #
    # Only a small contribution.
    # This prevents an irrelevant article
    # from becoming top-ranked simply
    # because NLI predicted contradiction.
    score += contradiction * 5


    # Support words have a small effect.
    score += min(
        len(support_matches),
        2
    ) * 2


    # Fact-check keywords do NOT receive
    # a ranking bonus.
    #
    # Refutation keywords do NOT receive
    # a ranking bonus.


    # Recency
    score *= recency


    # --------------------------------------------------------
    # RELEVANCE PENALTY
    # --------------------------------------------------------

    if important_overlap < 0.20:

        score *= 0.30


    if important_overlap < 0.10:

        score *= 0.10


    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {

        "score":
            round(
                score,
                4
            ),

        "reliability":
            round(
                reliability,
                2
            ),

        "claim_overlap":
            round(
                overlap * 100,
                2
            ),

        "important_overlap":
            round(
                important_overlap * 100,
                2
            ),

        "fact_check_matches":
            fact_matches,

        "refutation_matches":
            refutation_matches,

        "support_matches":
            support_matches,

        "entailment":
            round(
                entailment * 100,
                2
            ),

        "contradiction":
            round(
                contradiction * 100,
                2
            ),

        "neutral":
            round(
                neutral * 100,
                2
            ),

        "recency_multiplier":
            round(
                recency,
                2
            )
    }


# ============================================================
# RANK EVIDENCE
# ============================================================

def rank_evidence(
    claim,
    results,
    nli_function
):

    ranked = []

    seen_urls = set()

    domain_counts = {}


    # ========================================================
    # PROCESS RESULTS
    # ========================================================

    for result in results:

        url = clean_text(
            result.get(
                "url",
                ""
            )
        )


        domain = get_domain(
            url
        )


        # ----------------------------------------------------
        # DUPLICATE URL
        # ----------------------------------------------------

        if (
            url
            and url in seen_urls
        ):

            continue


        if url:

            seen_urls.add(
                url
            )


        # ----------------------------------------------------
        # TITLE / CONTENT
        # ----------------------------------------------------

        title = clean_text(
            result.get(
                "title",
                ""
            )
        )


        content = clean_text(
            result.get(
                "content",
                ""
            )
        )


        if (
            not title
            and not content
        ):

            continue


        evidence = (
            title
            + ". "
            + content
        )


        # ----------------------------------------------------
        # QUICK RELEVANCE CHECK
        # ----------------------------------------------------

        overlap = calculate_important_overlap(
            claim,
            evidence
        )


        # Ignore extremely unrelated
        # search results.

        if overlap < 0.05:

            print(
                "Skipping low relevance:",
                title
            )

            continue


        # ----------------------------------------------------
        # NLI
        # ----------------------------------------------------

        try:

            nli_scores = nli_function(
                claim,
                evidence[:3000]
            )


        except Exception as error:

            print(
                "NLI ranking error:",
                error
            )


            nli_scores = {

                "entailment": 0.0,

                "contradiction": 0.0,

                "neutral": 1.0
            }


        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        score_data = calculate_evidence_score(

            claim,

            result,

            nli_scores
        )


        # ----------------------------------------------------
        # DOMAIN DIVERSITY
        # ----------------------------------------------------

        if domain:

            domain_counts[
                domain
            ] = (
                domain_counts.get(
                    domain,
                    0
                )
                + 1
            )


        # First article from a domain:
        # full score.

        # Repeated articles from same domain:
        # reduced score.

        count = domain_counts.get(
            domain,
            1
        )


        if count == 2:

            score_data["score"] *= 0.80


        elif count == 3:

            score_data["score"] *= 0.60


        elif count >= 4:

            score_data["score"] *= 0.45


        score_data["score"] = round(
            score_data["score"],
            4
        )


        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        ranked.append({

            **result,

            "evidence_score":
                score_data
        })


    # ========================================================
    # SORT
    # ========================================================

    ranked.sort(

        key=lambda item:
            item[
                "evidence_score"
            ][
                "score"
            ],

        reverse=True
    )


    # ========================================================
    # DEBUG OUTPUT
    # ========================================================

    print()
    print("=" * 60)
    print("EVIDENCE RANKING")
    print("=" * 60)


    for index, item in enumerate(
        ranked[:15],
        start=1
    ):

        score_data = item[
            "evidence_score"
        ]


        print(
            f"{index}. "
            f"{item.get('title', '')}"
        )


        print(
            "   Domain:",
            get_domain(
                item.get(
                    "url",
                    ""
                )
            )
        )


        print(
            "   Score:",
            score_data.get(
                "score",
                0
            )
        )


        print(
            "   Relevance:",
            score_data.get(
                "important_overlap",
                0
            ),
            "%"
        )


        print(
            "   Entailment:",
            score_data.get(
                "entailment",
                0
            ),
            "%"
        )


        print(
            "   Contradiction:",
            score_data.get(
                "contradiction",
                0
            ),
            "%"
        )


        print()


    print("=" * 60)


    return ranked