from typing import List, Dict, Any
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from .base import BaseLLM

class GeminiLLM(BaseLLM):
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            convert_system_message_to_human=True
        )
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        system_prompt = """You are an intelligent learning assistant, helping users define their learning goals 
        and create structured learning paths. Provide clear, concise, and helpful responses. 
        Consider the full conversation context when responding."""
        
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
        system_prompt = """You are a course creation assistant. Based on the user's requirements from their chat messages,
        create a detailed course outline. The output should be a valid JSON object with the following structure:

        {
            "title": "Course title",
            "description": "Comprehensive course description",
            "difficulty": "beginner|intermediate|advanced",
            "estimatedDuration": "Total estimated duration",
            "topics": [
                {
                    "id": "topic-1",
                    "title": "Main topic title",
                    "description": "Topic overview",
                    "order": 1,
                    "learningPoints": [
                        {
                            "id": "point-1",
                            "title": "Specific concept or skill to learn",
                            "description": "Detailed explanation of what needs to be learned",
                            "searchQuery": "Specific search term for finding a good tutorial video"
                        }
                    ]
                }
            ]
        }

        Make sure:
        1. Each topic has 3-5 specific learning points
        2. Learning point titles are specific and searchable
        3. Search queries are optimized for finding tutorial videos
        4. Topics follow a logical progression
        5. Descriptions are clear and concise
        """

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

    async def generate_lesson_detail(self, topic: str, content: Dict[str, str]) -> Dict[str, Any]:
        system_prompt = """You are a lesson content creator. Create a detailed lesson plan for the given topic.
        The output should be a valid JSON object with the following structure:

        {
            "id": "unique-id",
            "title": "Lesson title",
            "description": "Detailed lesson description",
            "topics": [
                {
                    "id": "topic-id",
                    "title": "Topic title",
                    "description": "Topic description",
                    "duration": "Estimated duration"
                }
            ],
            "resources": [
                {
                    "id": "resource-id",
                    "type": "video|article|reference",
                    "title": "Resource title",
                    "url": "Resource URL",
                    "duration": "Resource duration (for videos)",
                    "source": "Source name",
                    "description": "Resource description"
                }
            ],
            "exercises": [
                {
                    "question": "Practice question",
                    "answer": "Detailed answer/explanation"
                }
            ],
            "duration": "Total lesson duration"
        }

        Create practical, engaging content that helps learners understand and apply the concepts.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a detailed lesson plan for: {topic}\nContext: {json.dumps(content)}"}
        ]

        response = self.llm.invoke(messages)
        
        try:
            # Extract JSON from response
            json_str = response.content
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            return json.loads(json_str)
        except Exception as e:
            raise Exception(f"Failed to parse lesson detail: {str(e)}") 