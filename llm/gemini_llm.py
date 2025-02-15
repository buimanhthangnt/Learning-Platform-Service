from typing import List, Dict, Any, Optional
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
        1. Each topic has 3-4 specific learning points
        2. Learning point titles are specific and searchable
        3. Search queries are optimized for finding tutorial videos
        4. Topics follow a logical progression
        5. Descriptions are clear and concise
        6. The number of topics is between 3 and 4
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

    async def process_web_content(self, content: str, topic: str, context: str) -> Optional[str]:
        try:
            system_prompt = f"""Extract and summarize relevant information about '{topic}' from the following content.
            Context: {context}
            
            Focus on:
            1. Key concepts and definitions
            2. Important principles
            3. Practical applications
            4. Examples and explanations
            
            Format the output as a clear, concise explanation that complements the learning point.
            If the content is not relevant to the learning point, just return empty string.
            """
            
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
            system_prompt = f"""Create clear and engaging learning material about '{topic}' from the following content.
            Context: {context}
            
            Format the content in markdown with the following structure:

            # {topic}
            [Brief introduction to the topic - 2-3 sentences]

            ## Core Concepts
            [Brief paragraph explaining the foundational ideas]

            ### Key Concepts:
            * **[First concept]**: [Clear explanation]
            * **[Second concept]**: [Clear explanation]
            * **[Third concept]**: [Clear explanation]

            ## Important Points
            * [First key point with explanation]
            * [Second key point with explanation]
            * [Third key point with explanation]

            ## Practical Examples

            ### Example 1: [Example Title]
            [Detailed explanation of the first example]
            
            > **Note**: [Important observation or tip about the example]

            ### Example 2: [Example Title]
            [Detailed explanation of the second example]

            ## Summary
            [Concise summary paragraph highlighting main points]

            ---

            **Key Takeaways:**
            1. [First takeaway]
            2. [Second takeaway]
            3. [Third takeaway]

            Formatting guidelines:
            - Use markdown headers (#, ##, ###)
            - Use bold (**) for emphasis
            - Use bullet points (*) for lists
            - Use numbered lists (1., 2., etc.) for steps
            - Use blockquotes (>) for important notes
            - Keep paragraphs short and clear
            - Use simple, engaging language
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]

            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            print(f"Error processing learning content: {str(e)}")
            return None 