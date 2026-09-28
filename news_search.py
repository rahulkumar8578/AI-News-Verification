import os
from functools import lru_cache
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv(
    "TAVILY_API_KEY"
)

client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None


def generate_queries(
    headline="",
    news=""
):

    headline = str(
        headline or ""
    ).strip()

    news = str(
        news or ""
    ).strip()

    claim = headline

    if not claim:
        claim = news

    queries = []

    if claim:
        queries.append(
            f'"{claim}"'
        )

    if claim:
        queries.append(
            claim
        )

    if claim:
        queries.append(
            f"{claim} official"
        )

    if claim:
        queries.append(
            f"{claim} latest"
        )

    if claim:
        queries.append(
            f"{claim} news"
        )

    if news and news != claim:
        queries.append(
            news[:500]
        )

    unique_queries = []

    for query in queries:

        query = query.strip()

        if (
            query
            and query not in unique_queries
        ):

            unique_queries.append(
                query
            )

    return unique_queries[:6]


def run_search(
    query
):

    print()
    print(
        "Searching:",
        query
    )

    try:

        if client is None:
            return {"answer": "", "results": []}

        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=8,
            include_answer=True,
            include_raw_content=True
        )

        results = response.get(
            "results",
            []
        )

        cleaned_results = []

        for item in results:

            title = item.get(
                "title",
                ""
            )

            url = item.get(
                "url",
                ""
            )

            content = item.get(
                "content",
                ""
            )

            raw_content = item.get(
                "raw_content",
                ""
            )

            published_date = item.get(
                "published_date",
                ""
            )

            score = item.get(
                "score",
                0
            )

            final_content = (
                raw_content
                if raw_content
                else content
            )

            if not title and not final_content:
                continue

            cleaned_results.append({

                "title":
                    title,

                "url":
                    url,

                "content":
                    final_content,

                "published_date":
                    published_date,

                "score":
                    score
            })

        return {

            "answer":
                response.get(
                    "answer",
                    ""
                ),

            "results":
                cleaned_results
        }

    except Exception as error:

        print(
            "Tavily search error:",
            error
        )

        return {

            "answer":
                "",

            "results":
                []
        }


def _search_news(
    headline="",
    news=""
):

    print()
    print("=" * 60)
    print("WEB NEWS SEARCH")
    print("=" * 60)

    queries = generate_queries(
        headline,
        news
    )

    print()
    print(
        "Generated queries:"
    )

    for index, query in enumerate(
        queries,
        start=1
    ):

        print(
            f"{index}. {query}"
        )

    all_results = []
    answers = []

    for query in queries:

        search_data = run_search(
            query
        )

        if search_data.get(
            "answer"
        ):

            answers.append(
                search_data[
                    "answer"
                ]
            )

        all_results.extend(
            search_data.get(
                "results",
                []
            )
        )

    unique_results = []
    seen_urls = set()

    for result in all_results:

        url = result.get(
            "url",
            ""
        ).strip().lower()

        if url:

            if url in seen_urls:
                continue

            seen_urls.add(
                url
            )

        unique_results.append(
            result
        )

    unique_results.sort(
        key=lambda item: (
            float(
                item.get(
                    "score",
                    0
                ) or 0
            ),
            item.get(
                "url",
                ""
            ).lower(),
            item.get(
                "title",
                ""
            ).lower()
        ),
        reverse=True
    )

    unique_results = unique_results[:30]

    print()
    print("=" * 60)
    print(
        "TOTAL UNIQUE SEARCH RESULTS:",
        len(unique_results)
    )
    print("=" * 60)

    for index, result in enumerate(
        unique_results[:10],
        start=1
    ):

        print()
        print(
            f"{index}. {result.get('title', '')}"
        )

        print(
            "   URL:",
            result.get(
                "url",
                ""
            )
        )

        print(
            "   Tavily score:",
            result.get(
                "score",
                0
            )
        )

    return {

        "answer":
            answers[0]
            if answers
            else "",

        "results":
            unique_results,

        "queries":
            queries
    }


@lru_cache(maxsize=100)
def _cached_search_news(
    headline,
    news
):

    print()
    print("=" * 60)
    print("NEW WEB SEARCH")
    print("=" * 60)

    return _search_news(
        headline,
        news
    )


def search_news(
    headline="",
    news=""
):

    headline = " ".join(
        str(
            headline or ""
        ).split()
    ).strip()

    news = " ".join(
        str(
            news or ""
        ).split()
    ).strip()

    return _cached_search_news(
        headline,
        news
    )


if __name__ == "__main__":

    test_headline = (
        "Narendra Modi is the Prime Minister of India."
    )

    test_news = (
        "Narendra Modi is serving as the "
        "Prime Minister of India. "
        "He took oath for his third consecutive "
        "term as Prime Minister on 9 June 2024."
    )

    data = search_news(
        test_headline,
        test_news
    )

    print()
    print("=" * 60)
    print("SEARCH TEST COMPLETED")
    print("=" * 60)

    print(
        "Results:",
        len(
            data.get(
                "results",
                []
            )
        )
    )