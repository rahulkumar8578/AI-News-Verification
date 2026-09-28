from news_search import search_news


query = "NASA successful satellite launch"

results = search_news(query)


for i, result in enumerate(results, start=1):

    print("\n" + "=" * 60)
    print("SOURCE", i)
    print("=" * 60)

    print("Title:", result["title"])
    print("URL:", result["url"])
    print("Content:", result["content"][:500])