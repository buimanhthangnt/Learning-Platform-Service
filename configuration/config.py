import os
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
        self.HF_TOKEN = os.getenv("HF_TOKEN")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.SECRET_KEY = os.getenv("SECRET_KEY")


app_config = Config()
