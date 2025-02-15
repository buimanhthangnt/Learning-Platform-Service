import requests 


class JinaWebScraper:
    def __init__(self):
        self.base_url = "https://r.jina.ai/"

    def get_web_content(self, url):
		try:
			response = requests.get(f"{self.base_url}{url}", timeout=10)
			return response.text
		except Exception as e:
			print(f"Error getting web content: {e}")
			return ""
