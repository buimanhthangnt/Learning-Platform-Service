from typing import List
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


class DuckDuckGoScraper:
    def __init__(self):
        self.base_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search(self, query: str, num_results: int = 2) -> List[dict]:
        try:
            # Format search query
            params = {
                'q': query,
                'kl': 'us-en'  # Language/region
            }
            
            # Make request to DuckDuckGo
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=params,
                timeout=10
            )
            response.raise_for_status()
            
            # Parse results
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Extract search results
            for result in soup.select('.result')[:num_results]:
                title_elem = result.select_one('.result__title')
                snippet_elem = result.select_one('.result__snippet')
                link_elem = result.select_one('.result__url')
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    url = link_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    # Filter out unwanted domains
                    excluded_domains = ['youtube.com', 'facebook.com', 'twitter.com', 'instagram.com', 'tiktok.com']
                    if not any(domain in url.lower() for domain in excluded_domains):
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
            
            return results

        except Exception as e:
            print(f"Error searching DuckDuckGo: {str(e)}")
            return [] 