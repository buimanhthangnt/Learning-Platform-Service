from typing import List
import os
from googleapiclient.discovery import build
from datetime import timedelta
import isodate
from dotenv import load_dotenv

class YouTubeScraper:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def format_duration(self, duration: str) -> str:
        try:
            duration_obj = isodate.parse_duration(duration)
            if isinstance(duration_obj, timedelta):
                total_seconds = int(duration_obj.total_seconds())
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                return f"{minutes}:{seconds:02d}"
            return "Unknown duration"
        except:
            return "Unknown duration"

    def format_view_count(self, view_count: str) -> str:
        try:
            count = int(view_count)
            if count >= 1000000:
                return f"{count/1000000:.1f}M views"
            elif count >= 1000:
                return f"{count/1000:.1f}K views"
            return f"{count} views"
        except:
            return "Unknown views"

    def search_video(self, query: str, max_results: int = 2) -> List[dict]:
        try:
            # Add "tutorial" to the query if not present
            if "tutorial" not in query.lower():
                query = f"{query} tutorial"

            # Search for videos
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                videoEmbeddable='true',
                relevanceLanguage='en'
            ).execute()

            videos = []
            for item in search_response.get('items', []):
                if item['id']['kind'] == 'youtube#video':
                    video_id = item['id']['videoId']
                    
                    # Get video details
                    video_response = self.youtube.videos().list(
                        part='contentDetails,statistics',
                        id=video_id
                    ).execute()
                    
                    if video_response['items']:
                        video_details = video_response['items'][0]
                        duration = self.format_duration(
                            video_details['contentDetails']['duration']
                        )
                        view_count = self.format_view_count(
                            video_details['statistics']['viewCount']
                        )
                        
                        video = {
                            "type": "video",
                            "title": item['snippet']['title'],
                            "description": item['snippet']['description'],
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "thumbnail": item['snippet']['thumbnails']['high']['url'],
                            "source": "YouTube",
                            "duration": duration,
                            "views": view_count,
                            "channelTitle": item['snippet']['channelTitle']
                        }
                        videos.append(video)

            return videos
        except Exception as e:
            print(f"Error searching YouTube: {str(e)}")
            return [] 