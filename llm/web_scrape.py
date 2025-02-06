import requests 


class JinaWebScraper:
    def __init__(self):
        self.base_url = "https://r.jina.ai/"

    def get_web_content(self, url):
        response = requests.get(f"{self.base_url}{url}")
        return response.text
