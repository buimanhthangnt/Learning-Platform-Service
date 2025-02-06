from typing import Optional
import os
import requests
from bs4 import BeautifulSoup
from jinasdk import JinaAPI
from dotenv import load_dotenv

class JinaContentExtractor:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('JINA_API_KEY')
        self.jina = JinaAPI(api_key=self.api_key)

    def extract_content(self, url: str) -> Optional[str]:
        try:
            # Fetch webpage content
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe']):
                element.decompose()
            
            # Extract main content
            content = soup.get_text(separator=' ', strip=True)
            
            # Use Jina to summarize and extract relevant information
            summary = self.jina.summarize(
                text=content,
                target_length=500,
                format='paragraph'
            )
            
            return summary
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None 