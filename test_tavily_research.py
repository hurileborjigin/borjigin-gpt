# test_tavily_research.py
from dotenv import load_dotenv
import os
from tavily import TavilyClient
import json

load_dotenv()

def test_tavily_search():
    """Test what Tavily actually returns"""
    
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    # Test company research
    company = "IntraFind"
    
    print("=" * 80)
    print(f"Testing Tavily Search for: {company}")
    print("=" * 80)
    
    # Test 1: Company Overview
    print("\n1️⃣ COMPANY OVERVIEW SEARCH")
    print("-" * 80)
    
    overview_query = f"{company} company overview mission values products services"
    overview_results = client.search(
        query=overview_query,
        search_depth="advanced",
        max_results=5
    )
    
    print(f"Query: {overview_query}")
    print(f"\nResults found: {len(overview_results.get('results', []))}")
    
    for i, result in enumerate(overview_results.get('results', [])[:3], 1):
        print(f"\n--- Result {i} ---")
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"URL: {result.get('url', 'N/A')}")
        print(f"Score: {result.get('score', 'N/A')}")
        print(f"Content Preview: {result.get('content', 'N/A')[:300]}...")
    
    # Test 2: Company Culture
    print("\n\n2️⃣ COMPANY CULTURE SEARCH")
    print("-" * 80)
    
    culture_query = f"{company} company culture work environment employee reviews benefits"
    culture_results = client.search(
        query=culture_query,
        search_depth="advanced",
        max_results=5
    )
    
    print(f"Query: {culture_query}")
    print(f"\nResults found: {len(culture_results.get('results', []))}")
    
    for i, result in enumerate(culture_results.get('results', [])[:3], 1):
        print(f"\n--- Result {i} ---")
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Content Preview: {result.get('content', 'N/A')[:300]}...")
    
    # Test 3: Recent News
    print("\n\n3️⃣ RECENT NEWS SEARCH")
    print("-" * 80)
    
    news_query = f"{company} latest news announcements 2024 2025"
    news_results = client.search(
        query=news_query,
        search_depth="advanced",
        max_results=5,
        days=90  # Last 90 days
    )
    
    print(f"Query: {news_query}")
    print(f"\nResults found: {len(news_results.get('results', []))}")
    
    for i, result in enumerate(news_results.get('results', [])[:3], 1):
        print(f"\n--- Result {i} ---")
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Published: {result.get('published_date', 'N/A')}")
        print(f"Content Preview: {result.get('content', 'N/A')[:300]}...")
    
    # Save full results for inspection
    print("\n\n" + "=" * 80)
    print("Saving full results to tavily_test_results.json")
    print("=" * 80)
    
    with open("tavily_test_results.json", "w") as f:
        json.dump({
            "overview": overview_results,
            "culture": culture_results,
            "news": news_results
        }, f, indent=2)
    
    print("✅ Results saved! Check tavily_test_results.json for full details")

if __name__ == "__main__":
    test_tavily_search()