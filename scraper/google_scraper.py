from typing import List
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

class GoogleSearchScraper:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('SERPAPI_API_KEY')

    def search(self, query: str, num_results: int = 2) -> List[dict]:
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
                # Filter out social media and video sites
                "exclude_domains": "youtube.com,facebook.com,twitter.com,instagram.com,tiktok.com"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            organic_results = results.get("organic_results", [])
            return [
                {
                    "title": result["title"],
                    "url": result["link"],
                    "snippet": result.get("snippet", "")
                }
                for result in organic_results[:num_results]
            ]
        except Exception as e:
            print(f"Error searching Google: {str(e)}")
            return [] 