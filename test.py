from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, VisitWebpageTool, FinalAnswerTool, \
                        PythonInterpreterTool, ToolCallingAgent
from smolagents import LiteLLMModel
from llm.gemini_llm import GeminiLLM
from dotenv import load_dotenv
from deep_research.run import answer_single_question
from scraper.youtube_scraper import YouTubeScraper
from scraper.duckduckgo_scraper import DuckDuckGoScraper
from deep_research.text_web_browser import SimpleTextBrowser


from google import genai
from google.genai import types
import os

load_dotenv()


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents='I am a programmer, I want to learn about LLM and how to apply it in my own projects. Provide me necessary knowledge and youtube video urls (not just the keywords) to start learning',
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                google_search=types.GoogleSearch()
            )
        ]
    )
)
print(response.text)
exit()

# browser = SimpleTextBrowser()
# browser._duckduckgo_search("llm")
# exit()
# load_dotenv()

# model = GeminiLLM().llm
# def custom

# search_agent = ToolCallingAgent(
#     tools=[DuckDuckGoSearchTool(), VisitWebpageTool()],
#     model=model,
#     name="search_agent",
#     description="This is an agent that can do web search.",
# )

# manager_agent = CodeAgent(
#     tools=[],
#     model=model,
#     managed_agents=[search_agent],
# )
# manager_agent.run(
#     "If the US keeps its 2024 growth rate, how many years will it take for the GDP to double?"
# )

# exit()

# model = LiteLLMModel("anthropic/claude-3-5-sonnet-latest", temperature=0.2, max_tokens=10)
# model = GeminiLLM().llm.invoke

# scraper = YouTubeScraper()
# videos = scraper.search_video("how to use LLM", 2)
# print(videos)

# exit()
model = "gemini-1.5-flash"
question = "I am a programmer, I want to learn about LLM and how to apply it in my own projects. Provide me necessary knowledge and youtube videos to start learning"
# question = "I want to learn to use LLM, my background is not good. Provide me necessary knowledge to start learning"

answer_single_question(question, model)
