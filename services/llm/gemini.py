from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from services.llm.base import BaseLLM


class GeminiLLM(BaseLLM):
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            convert_system_message_to_human=True
        )
        self.setup_memory(self.llm)
        

    def invoke(self, messages):
        return self.llm.invoke(messages)
