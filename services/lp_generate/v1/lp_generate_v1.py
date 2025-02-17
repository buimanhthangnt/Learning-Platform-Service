from typing import List, Dict, Any, Optional
from configuration.constants import *
import json
from services.scraper.youtube_scraper import YouTubeScraper


class LPGenerateV1:
    def __init__(self, llm_model):
        self.llm = llm_model
        self.conversation = self.llm.conversation
        self.youtube_scraper = YouTubeScraper()


    async def chat(self, messages: List[Dict[str, str]]) -> str:
        system_prompt = LP_GENERATE_V1_CHAT_PROMPT
        
        # Build conversation history
        conversation_history = ""
        for msg in messages[:-1]:  # All messages except the latest
            if msg["role"] == "user":
                conversation_history += f"Human: {msg['content']}\n"
            else:
                conversation_history += f"Assistant: {msg['content']}\n"
        
        # Add system prompt and latest message
        latest_message = messages[-1]["content"]
        prompt = f"{system_prompt}\n\nConversation history:\n{conversation_history}\nHuman: {latest_message}\nAssistant:"
        
        response = await self.conversation.apredict(input=prompt)
        return response.strip()


    async def generate_course_outline(self, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        system_prompt = LP_GENERATE_V1_COURSE_OUTLINE_PROMPT

        chat_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a course outline based on this conversation:\n{chat_context}"}
        ]

        response = self.llm.invoke(messages)
        print(response)
        
        try:
            json_str = response.content
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            return json.loads(json_str)
        except Exception as e:
            raise Exception(f"Failed to parse course outline: {str(e)}")


    async def generate_topic_with_resources(self, outline):
        # Process each topic and learning point
        topics_with_resources = []
        for topic in outline["topics"]:
            learning_points_with_resources = []
            
            for point in topic["learningPoints"]:
                print(f"Processing learning point: {point['title']}")
                
                # Get YouTube videos
                videos = self.youtube_scraper.search_video(
                    point["searchQuery"],
                    max_results=2
                )
                
                # # Get DuckDuckGo search results instead of Google
                # articles = duckduckgo_scraper.search(point["searchQuery"])
                # print("articles: ", articles)
                
                # # Extract and process content from web pages
                # web_contents = []
                # all_content = ""
                
                # for article in articles:
                #     content = web_scraper.extract_content(article["url"])
                #     if content:
                #         all_content += f"\n\nSource: {article['title']}\n{content}"
                
                # if all_content:
                #     # Process combined content with LLM
                #     processed_content = await lp_generate.process_learning_content(
                #         content=all_content,
                #         topic=point["title"],
                #         context=point["description"]
                #     )
                #     print("processed_content: ", processed_content)
                
                # Combine resources
                processed_content = ""

                learning_point_with_resources = {
                    **point,
                    "resources": videos,
                    "content": processed_content if processed_content else ""
                }
                learning_points_with_resources.append(learning_point_with_resources)
            
            topics_with_resources.append({
                **topic,
                "learningPoints": learning_points_with_resources
            })
        return topics_with_resources


    async def generate_lesson_detail(self, topic: str, content: Dict[str, str]) -> Dict[str, Any]:
        system_prompt = LP_GENERATE_V1_LESSION_DETAIL_PROMPT

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a detailed lesson plan for: {topic}\nContext: {json.dumps(content)}"}
        ]

        response = self.llm.invoke(messages)
        
        try:
            json_str = response.content
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            return json.loads(json_str)
        except Exception as e:
            raise Exception(f"Failed to parse lesson detail: {str(e)}")


    async def process_web_content(self, content: str, topic: str, context: str) -> Optional[str]:
        try:
            system_prompt = LP_GENERATE_V1_PROCESS_WEB_CONTENT_PROMPT(topic, context)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]

            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            print(f"Error processing web content: {str(e)}")
            return None 


    async def process_learning_content(self, content: str, topic: str, context: str) -> Optional[str]:
        try:
            system_prompt = LP_GENERATE_V1_PROCESS_LEARNING_CONTENT_PROMPT(topic, context, topic)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]

            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            print(f"Error processing learning content: {str(e)}")
            return None 

