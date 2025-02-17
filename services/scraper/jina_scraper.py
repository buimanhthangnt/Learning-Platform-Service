from typing import Optional
import os
import requests


class JinaContentExtractor:
    def __init__(self):
        self.base_url = "https://r.jina.ai/"

    def extract_content(self, url: str) -> Optional[str]:
        print("Getting content from ", url)
        response = requests.get(f"{self.base_url}{url}")
        print("Web content: ", response.text)
        return response.text
