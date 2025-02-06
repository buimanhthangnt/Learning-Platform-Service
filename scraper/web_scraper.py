from typing import Optional
import requests
from bs4 import BeautifulSoup
import trafilatura

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def extract_content(self, url: str) -> Optional[str]:
        try:
            # Download webpage
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Extract main content using trafilatura
            content = trafilatura.extract(
                response.text,
                include_comments=False,
                include_tables=False,
                no_fallback=True
            )
            
            if not content:
                # Fallback to BeautifulSoup if trafilatura fails
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'aside']):
                    element.decompose()
                
                # Extract text from article or main content
                main_content = soup.find('article') or soup.find('main') or soup.find('body')
                if main_content:
                    content = main_content.get_text(separator=' ', strip=True)
            
            return content

        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None 