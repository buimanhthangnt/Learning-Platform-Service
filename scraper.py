import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
import requests
from typing import Dict, List
import youtube_dl

class ContentScraper:
    def __init__(self):
        self.youtube_dl_opts = {
            'format': 'best',
            'extract_flat': True,
        }

    def scrape_content(self, topic: str) -> Dict:
        return {
            'videos': self._scrape_youtube(topic),
            'articles': self._scrape_medium(topic),
            'wikipedia': self._scrape_wikipedia(topic)
        }

    def _scrape_youtube(self, topic: str) -> List[str]:
        try:
            search_url = f"https://www.youtube.com/results?search_query={topic}"
            with youtube_dl.YoutubeDL(self.youtube_dl_opts) as ydl:
                results = ydl.extract_info(search_url, download=False)
                videos = []
                for entry in results['entries'][:3]:  # Get top 3 videos
                    videos.append({
                        'title': entry['title'],
                        'url': entry['webpage_url'],
                        'duration': entry['duration']
                    })
                return videos
        except Exception as e:
            print(f"Error scraping YouTube: {e}")
            return []

    def _scrape_medium(self, topic: str) -> List[str]:
        try:
            search_url = f"https://medium.com/search?q={topic}"
            response = requests.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            # Implement Medium scraping logic
            return articles
        except Exception as e:
            print(f"Error scraping Medium: {e}")
            return []

    def _scrape_wikipedia(self, topic: str) -> str:
        try:
            search_url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
            response = requests.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Implement Wikipedia scraping logic
            return ""
        except Exception as e:
            print(f"Error scraping Wikipedia: {e}")
            return "" 