from typing import List
import os
import requests
from dotenv import load_dotenv

class BingSearchScraper:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('BING_API_KEY')
        self.endpoint = "https://api.bing.microsoft.com/v7.0/search"

    def search(self, query: str, count: int = 5) -> List[dict]:
        try:
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            params = {
                "q": query,
                "count": count,
                "responseFilter": "Webpages",
                "freshness": "Month"
            }
            response = requests.get(self.endpoint, headers=headers, params=params)
            response.raise_for_status()
            
            search_results = response.json()
            return [
                {
                    "title": page["name"],
                    "url": page["url"],
                    "snippet": page["snippet"]
                }
                for page in search_results.get("webPages", {}).get("value", [])
            ]
        except Exception as e:
            print(f"Error searching Bing: {str(e)}")
            return [] 