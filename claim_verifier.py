import re
from urllib.parse import urlparse

OFFICIAL_DOMAINS = [
    "pib.gov.in", "india.gov.in", "mygov.in", "nic.in", "mha.gov.in",
    "mea.gov.in", "mohfw.gov.in", "education.gov.in", "finance.gov.in",
    "isro.gov.in", "rbi.org.in", "eci.gov.in"
]

FACT_CHECK_DOMAINS = [
    "altnews.in", "boomlive.in", "factly.in", "newsmeter.in",
    "vishvasnews.com", "afp.com", "snopes.com", "politifact.com"
]

TRUSTED_NEWS_DOMAINS = [
    "reuters.com", "bbc.com", "bbc.co.uk", "thehindu.com",
    "indianexpress.com", "hindustantimes.com", "ndtv.com",
    "indiatoday.in", "theprint.in", "news18.com"
]

STOP_WORDS = {
    "the", "is", "are", "was", "were", "a", "an", "and", "or", "of",
    "to", "in", "on", "for", "with", "by", "from", "this", "that",
    "has", "have", "had", "be", "been", "being", "will", "would",
    "can", "could", "should", "about", "into", "after", "before",
    "than", "their", "they", "them", "its", "it", "as", "at", "under",
    "over", "from", "who", "what", "when", "where", "which", "while"
}

REFUTATION_TERMS = [
    "fake", "false", "fraudulent", "fabricated", "debunked", "refuted",
    "misleading", "hoax", "scam", "not true", "untrue", "not genuine",
    "does not exist", "doesn't exist", "no such scheme", "no such scheme exists",
    "not launched", "did not launch", "never launched", "not issued",
    "did not issue", "never issued", "denied", "denies", "disproved"
]

REFUTATION_PATTERNS = [
    r"\b(?:claim|claims|message|messages|post|posts|report|reports|news|story|viral message|viral post)\b.{0,100}\b(?:fake|false|fraudulent|fabricated|debunked|refuted|misleading|hoax|scam|untrue|not true|not genuine)\b",
    r"\b(?:fake|false|fraudulent|fabricated|debunked|refuted|misleading|hoax|scam|untrue|not true|not genuine)\b.{0,100}\b(?:claim|claims|message|messages|post|posts|report|reports|news|story)\b",
    r"\b(?:fact check|fact-check|factcheck|fact check unit|pib fact check)\b.{0,160}\b(?:fake|false|debunked|refuted|misleading|not true|untrue)\b",
    r"\b(?:does not exist|doesn't exist|no such scheme|no such scheme exists|not launched|did not launch|never launched|not issued|did not issue|never issued)\b"
]

SUPPORT_PATTERNS = [
    r"\b(?:confirmed|confirms|officially announced|officially reported|verified|successfully launched|successfully completed)\b",
    r"\b(?:according to|reported by|announced by)\b"
]


def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def tokenize(text):
    words = re.findall(r"[a-zA-Z0-9]+", clean_text(text).lower())
    return {word for word in words if len(word) >= 3 and word not in STOP_WORDS}


def get_domain(url):
    if not url:
        return ""
    try:
        return urlparse(str(url)).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def domain_matches(domain, domain_list):
    domain = domain.lower()
    return any(domain == item or domain.endswith("." + item) for item in domain_list)


def source_reliability(url):
    domain = get_domain(url)
    if domain_matches(domain, OFFICIAL_DOMAINS):
        return 1.70
    if domain_matches(domain, FACT_CHECK_DOMAINS):
        return 1.60
    if domain_matches(domain, TRUSTED_NEWS_DOMAINS):
        return 1.30
    return 1.0


def phrase_match(claim, evidence):
    claim = clean_text(claim).lower()
    evidence = clean_text(evidence).lower()
    if len(claim) < 10:
        return False
    return claim in evidence


def calculate_similarity(claim, evidence):
    claim_words = tokenize(claim)
    evidence_words = tokenize(evidence)
    if not claim_words:
        return 0.0
    return len(claim_words.intersection(evidence_words)) / len(claim_words)


def calculate_bigram_similarity(claim, evidence):
    claim_words = re.findall(r"[a-zA-Z0-9]+", clean_text(claim).lower())
    evidence_words = re.findall(r"[a-zA-Z0-9]+", clean_text(evidence).lower())
    if len(claim_words) < 2 or len(evidence_words) < 2:
        return 0.0
    claim_bigrams = set(zip(claim_words, claim_words[1:]))
    evidence_bigrams = set(zip(evidence_words, evidence_words[1:]))
    return len(claim_bigrams & evidence_bigrams) / len(claim_bigrams)


def find_refutation_terms(text):
    text = clean_text(text).lower()
    return [term for term in REFUTATION_TERMS if term in text]


def detect_explicit_refutation(text):
    text = clean_text(text).lower()
    matches = []
    for pattern in REFUTATION_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            matches.append(pattern)
    return len(matches) > 0


def detect_support_language(text):
    text = clean_text(text).lower()
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in SUPPORT_PATTERNS)


def analyze_claim(claim, evidence):
    similarity = calculate_similarity(claim, evidence)
    bigram_similarity = calculate_bigram_similarity(claim, evidence)
    exact_match = phrase_match(claim, evidence)
    explicit_refutation = detect_explicit_refutation(evidence)
    support_language = detect_support_language(evidence)

    if explicit_refutation:
        contradiction = min(1.0, 0.78 + similarity * 0.20)
        entailment = min(0.25, similarity * 0.25)
    else:
        contradiction = 0.0
        entailment = min(1.0, similarity * 0.65 + bigram_similarity * 0.25)
        if exact_match:
            entailment = max(entailment, 0.78)
        if support_language and similarity >= 0.30:
            entailment = min(1.0, entailment + 0.10)

    neutral = max(0.0, 1.0 - max(entailment, contradiction))

    return {
        "entailment": entailment,
        "contradiction": contradiction,
        "neutral": neutral,
        "similarity": similarity,
        "bigram_similarity": bigram_similarity,
        "exact_match": exact_match,
        "explicit_refutation": explicit_refutation,
        "support_language": support_language
    }


def evaluate_article(claim, result):
    title = clean_text(result.get("title", ""))
    content = clean_text(result.get("content") or result.get("raw_content") or "")
    url = clean_text(result.get("url", ""))
    published_date = clean_text(result.get("published_date", ""))

    evidence = f"{title}. {content}".strip()
    analysis = analyze_claim(claim, evidence[:7000])

    domain = get_domain(url)
    official = domain_matches(domain, OFFICIAL_DOMAINS)
    fact_check = domain_matches(domain, FACT_CHECK_DOMAINS)
    trusted_news = domain_matches(domain, TRUSTED_NEWS_DOMAINS)
    reliability = source_reliability(url)

    similarity = analysis["similarity"]
    entailment = analysis["entailment"]
    contradiction = analysis["contradiction"]
    exact_match = analysis["exact_match"]
    explicit_refutation = analysis["explicit_refutation"]

    relevance = (
        0.55 * similarity
        + 0.25 * analysis["bigram_similarity"]
        + 0.20 * (1.0 - analysis["neutral"])
    )

    if exact_match:
        relevance = min(1.0, relevance + 0.25)

    if explicit_refutation:
        relevance = min(1.0, max(relevance, similarity * 0.75))

    support_score = (
        entailment * 100
        + similarity * 20
        + analysis["bigram_similarity"] * 15
        + (20 if exact_match else 0)
        + (12 if official else 0)
        + (8 if trusted_news else 0)
    )

    contradiction_score = contradiction * 100

    if explicit_refutation:
        contradiction_score += 25
    if official and explicit_refutation:
        contradiction_score += 25
    if fact_check and explicit_refutation:
        contradiction_score += 20

    return {
        "title": title,
        "content": content,
        "url": url,
        "domain": domain,
        "published_date": published_date,
        "similarity": similarity,
        "bigram_similarity": analysis["bigram_similarity"],
        "relevance": relevance,
        "exact_match": exact_match,
        "entailment": entailment,
        "contradiction": contradiction,
        "neutral": analysis["neutral"],
        "explicit_refutation": explicit_refutation,
        "support_language": analysis["support_language"],
        "reliability": reliability,
        "official": official,
        "fact_check": fact_check,
        "trusted_news": trusted_news,
        "refutation_terms": find_refutation_terms(evidence),
        "support_score": support_score,
        "contradiction_score": contradiction_score
    }


def build_evidence(item):
    return {
        "title": item["title"],
        "url": item["url"],
        "domain": item["domain"],
        "published_date": item["published_date"],
        "entailment": round(item["entailment"], 4),
        "contradiction": round(item["contradiction"], 4),
        "neutral": round(item["neutral"], 4),
        "similarity": round(item["similarity"], 4),
        "relevance": round(item["relevance"], 4)
    }


def make_result(status, confidence, reason, evidence):
    return {
        "status": status,
        "confidence": max(0, min(99, int(confidence))),
        "reason": reason,
        "evidence": evidence
    }


def verify_claim(claim, search_data):
    claim = clean_text(claim)

    if not claim:
        return make_result("UNCERTAIN", 0, "No claim provided.", [])

    if not isinstance(search_data, dict):
        return make_result("UNCERTAIN", 0, "Invalid web search data.", [])

    results = search_data.get("results", [])
    if not isinstance(results, list) or not results:
        return make_result("UNCERTAIN", 0, "No web results found.", [])

    evaluated = []

    for result in results:
        if not isinstance(result, dict):
            continue
        try:
            item = evaluate_article(claim, result)
            if item["relevance"] >= 0.12:
                evaluated.append(item)
        except Exception as error:
            print("Article evaluation error:", error)

    if not evaluated:
        return make_result(
            "UNCERTAIN",
            50,
            "No sufficiently relevant web evidence was found.",
            []
        )

    evaluated.sort(
        key=lambda item: (
            item["relevance"] * item["reliability"],
            item["contradiction_score"],
            item["support_score"]
        ),
        reverse=True
    )

    top_articles = evaluated[:10]
    evidence = [build_evidence(item) for item in top_articles]

    explicit_refutations = [
        item for item in evaluated
        if item["explicit_refutation"] and item["similarity"] >= 0.25
    ]

    official_refutations = [
        item for item in explicit_refutations
        if item["official"]
    ]

    factcheck_refutations = [
        item for item in explicit_refutations
        if item["fact_check"]
    ]

    strong_contradictions = [
        item for item in evaluated
        if item["contradiction"] >= 0.78 and item["relevance"] >= 0.35
    ]

    strong_support = [
        item for item in evaluated
        if item["entailment"] >= 0.65
        and item["relevance"] >= 0.35
        and not item["explicit_refutation"]
    ]

    official_support = [
        item for item in strong_support
        if item["official"]
    ]

    trusted_support = [
        item for item in strong_support
        if item["trusted_news"]
    ]

    if official_refutations:
        item = max(official_refutations, key=lambda x: x["contradiction_score"])
        confidence = min(98, max(88, item["contradiction_score"] * 0.95))
        return make_result(
            "FALSE",
            confidence,
            "The claim is explicitly contradicted by relevant official evidence.",
            evidence
        )

    if factcheck_refutations:
        item = max(factcheck_refutations, key=lambda x: x["contradiction_score"])
        confidence = min(97, max(85, item["contradiction_score"] * 0.92))
        return make_result(
            "FALSE",
            confidence,
            "A relevant fact-check source explicitly identifies the claim as false or misleading.",
            evidence
        )

    if explicit_refutations:
        item = max(explicit_refutations, key=lambda x: x["contradiction_score"] * x["reliability"])
        if item["contradiction_score"] >= 95:
            confidence = min(94, max(78, item["contradiction_score"] * 0.88))
            return make_result(
                "FALSE",
                confidence,
                "Relevant web evidence explicitly refutes the claim.",
                evidence
            )

    if len(strong_contradictions) >= 2:
        top = max(strong_contradictions, key=lambda x: x["contradiction_score"] * x["reliability"])
        confidence = min(93, max(75, top["contradiction_score"] * 0.82))
        return make_result(
            "FALSE",
            confidence,
            "Multiple relevant sources provide contradictory evidence.",
            evidence
        )

    if official_support:
        item = max(official_support, key=lambda x: x["entailment"] * x["relevance"])
        confidence = min(97, max(80, item["entailment"] * 100))
        return make_result(
            "TRUE",
            confidence,
            "The claim is supported by relevant official evidence.",
            evidence
        )

    if trusted_support:
        item = max(trusted_support, key=lambda x: x["entailment"] * x["relevance"])
        confidence = min(94, max(72, item["entailment"] * 100))
        return make_result(
            "TRUE",
            confidence,
            "Relevant trusted-news evidence supports the claim.",
            evidence
        )

    if strong_support:
        top = max(strong_support, key=lambda x: x["entailment"] * x["relevance"] * x["reliability"])
        confidence = min(91, max(68, top["entailment"] * 100))
        return make_result(
            "TRUE",
            confidence,
            "Relevant web evidence strongly supports the claim.",
            evidence
        )

    return make_result(
        "UNCERTAIN",
        50,
        "The available web evidence is mixed or insufficient for a reliable decision.",
        evidence
    )
