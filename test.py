from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, VisitWebpageTool, FinalAnswerTool, PythonInterpreterTool
from smolagents import LiteLLMModel
from llm.gemini_llm import GeminiLLM
from dotenv import load_dotenv
from deep_research.run import answer_single_question


load_dotenv()
# model = LiteLLMModel("anthropic/claude-3-5-sonnet-latest", temperature=0.2, max_tokens=10)
# model = GeminiLLM().llm.invoke
model = "gemini-1.5-flash"
# question = "I want to catch up with latest news in LLM in last 3 months. You must use tools provided to search, get urls from search results, get content from those website urls in search results. Then use that content to generate me a report and find me some youtube videos related to the news"
question = "I want to learn to use LLM, my background is not good. Provide me necessary knowledge to start learning"

answer_single_question(question, model)

# exit()

# def custom_model(messages, stop_sequences=["Task"]):
#     print("Calling Gemini....")
#     return model.invoke(messages)

  
# agent = CodeAgent(tools=[DuckDuckGoSearchTool(max_results=5), VisitWebpageTool(), FinalAnswerTool()], model=custom_model)

# agent.run(question)
