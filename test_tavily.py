from tavily import TavilyClient
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get Tavily API key
api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    print("Tavily API key not found!")
    exit()

# Create Tavily client
tavily = TavilyClient(api_key=api_key)

# Search the web
response = tavily.search(
    query="NASA latest news",
    search_depth="basic",
    max_results=5
)

# Display results
for result in response["results"]:
    print("\nTitle:", result["title"])
    print("URL:", result["url"])
    print("Content:", result["content"][:300])