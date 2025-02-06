import argparse
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import List
from huggingface_hub import login
import pandas as pd
from dotenv import load_dotenv
from deep_research.reformulator import prepare_response
from deep_research.run_agents import (
    get_single_file_description,
    get_zip_description,
)
from deep_research.text_inspector_tool import TextInspectorTool
from deep_research.text_web_browser import (
    ArchiveSearchTool,
    FinderTool,
    FindNextTool,
    PageDownTool,
    PageUpTool,
    SearchInformationTool,
    SimpleTextBrowser,
    VisitTool,
)
from deep_research.visual_qa import visualizer
from tqdm import tqdm

from smolagents import (
    MANAGED_AGENT_PROMPT,
    CodeAgent,
    HfApiModel,
    LiteLLMModel,
    Model,
    ToolCallingAgent,
)
import litellm

litellm.drop_params=True


AUTHORIZED_IMPORTS = [
    "requests",
    "zipfile",
    "os",
    "pandas",
    "numpy",
    "sympy",
    "json",
    "bs4",
    "pubchempy",
    "xml",
    "yahoo_finance",
    "Bio",
    "sklearn",
    "scipy",
    "pydub",
    "io",
    "PIL",
    "chess",
    "PyPDF2",
    "pptx",
    "torch",
    "datetime",
    "fractions",
    "csv",
]
load_dotenv(override=True)
login(os.getenv("HF_TOKEN"))

append_answer_lock = threading.Lock()

### IMPORTANT: EVALUATION SWITCHES

print("Make sure you deactivated Tailscale VPN, else some URLs will be blocked!")

USE_OPEN_MODELS = False

SET = "validation"

custom_role_conversions = {"tool-call": "assistant", "tool-response": "user"}

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"

BROWSER_CONFIG = {
    "viewport_size": 1024 * 5,
    "downloads_folder": "downloads_folder",
    "request_kwargs": {
        "headers": {"User-Agent": user_agent},
        "timeout": 300,
    },
    "serpapi_key": os.getenv("SERPAPI_API_KEY"),
}

os.makedirs(f"./{BROWSER_CONFIG['downloads_folder']}", exist_ok=True)


def create_agent_hierarchy(model: Model):
    text_limit = 20000
    ti_tool = TextInspectorTool(model, text_limit)

    browser = SimpleTextBrowser(**BROWSER_CONFIG)

    WEB_TOOLS = [
        SearchInformationTool(browser),
        VisitTool(browser),
        PageUpTool(browser),
        PageDownTool(browser),
        FinderTool(browser),
        FindNextTool(browser),
        ArchiveSearchTool(browser),
        TextInspectorTool(model, text_limit),
    ]
    text_webbrowser_agent = ToolCallingAgent(
        model=model,
        tools=WEB_TOOLS,
        max_steps=2,
        verbosity_level=2,
        planning_interval=3,
        name="search_agent",
        description="""A team member that will search the internet to answer your question.
    Ask him for all your questions that require browsing the web.
    Provide him as much context as possible, in particular if you need to search on a specific timeframe!
    And don't hesitate to provide him with a complex search task, like finding a difference between two webpages.
    Your request must be a real sentence, not a google search! Like "Find me this information (...)" rather than a few keywords.
    """,
        provide_run_summary=True,
        managed_agent_prompt=MANAGED_AGENT_PROMPT
        + """You can navigate to .txt online files.
    If a non-html page is in another format, especially .pdf or a Youtube video, use tool 'inspect_file_as_text' to inspect it.
    Additionally, if after some searching you find out that you need more information to answer the question, you can use `final_answer` with your request for clarification as argument to request for more information.""",
    )

    manager_agent = CodeAgent(
        model=model,
        tools=[visualizer, ti_tool],
        max_steps=1,
        verbosity_level=2,
        additional_authorized_imports=AUTHORIZED_IMPORTS,
        planning_interval=1,
        managed_agents=[text_webbrowser_agent],
    )
    return manager_agent


def append_answer(entry: dict, jsonl_file: str) -> None:
    jsonl_file = Path(jsonl_file)
    jsonl_file.parent.mkdir(parents=True, exist_ok=True)
    with append_answer_lock, open(jsonl_file, "a", encoding="utf-8") as fp:
        fp.write(json.dumps(entry) + "\n")
    assert os.path.exists(jsonl_file), "File not found!"
    print("Answer exported to file:", jsonl_file.resolve())


def answer_single_question(question, model):
    # model = LiteLLMModel(
    #     model,
    #     custom_role_conversions=custom_role_conversions,
    #     max_completion_tokens=8192,
    #     reasoning_effort="high",
    # )
    model = HfApiModel()
    document_inspection_tool = TextInspectorTool(model, 100000)

    agent = create_agent_hierarchy(model)

    augmented_question = """You have one question to answer. It is paramount that you provide a correct answer.
Give it all you can: I know for a fact that you have access to all the relevant tools to solve it and find the correct answer (the answer does exist). Failure or 'I cannot answer' or 'None found' will not be tolerated, success will be rewarded.
Run verification steps if that's needed, you must make sure you find the correct answer!
Here is the task:
""" + question

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # try:
    # Run agent 🚀
    final_result = agent.run(augmented_question)

    agent_memory = agent.write_memory_to_messages(summary_mode=True)

    final_result = prepare_response(augmented_question, agent_memory, reformulation_model=model)

    output = str(final_result)
    for memory_step in agent.memory.steps:
        memory_step.model_input_messages = None
    intermediate_steps = [str(step) for step in agent.memory.steps]

    # Check for parsing errors which indicate the LLM failed to follow the required format
    parsing_error = True if any(["AgentParsingError" in step for step in intermediate_steps]) else False

    # check if iteration limit exceeded
    iteration_limit_exceeded = True if "Agent stopped due to iteration limit or time limit." in output else False
    raised_exception = False

    # except Exception as e:
    #     print("Error on ", augmented_question, e)
    #     output = None
    #     intermediate_steps = []
    #     parsing_error = False
    #     iteration_limit_exceeded = False
    #     exception = e
    #     raised_exception = True
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    annotated_example = {
        "agent_name": "Gemini",
        # "question": example["question"],
        "augmented_question": augmented_question,
        "prediction": output,
        "intermediate_steps": intermediate_steps,
        "parsing_error": parsing_error,
        "iteration_limit_exceeded": iteration_limit_exceeded,
        "agent_error": str(exception) if raised_exception else None,
        "start_time": start_time,
        "end_time": end_time,
    }
    # append_answer(annotated_example, answers_file)
    print(annotated_example)


def get_examples_to_answer(answers_file, eval_ds) -> List[dict]:
    print(f"Loading answers from {answers_file}...")
    try:
        done_questions = pd.read_json(answers_file, lines=True)["question"].tolist()
        print(f"Found {len(done_questions)} previous results!")
    except Exception as e:
        print("Error when loading records: ", e)
        print("No usable records! ▶️ Starting new.")
        done_questions = []
    return [line for line in eval_ds.to_list() if line["question"] not in done_questions]


def main():
    args = parse_args()
    print(f"Starting run with arguments: {args}")

    answers_file = f"output/{SET}/{args.run_name}.jsonl"
    tasks_to_run = get_examples_to_answer(answers_file, eval_ds)

    with ThreadPoolExecutor(max_workers=args.concurrency) as exe:
        futures = [
            exe.submit(answer_single_question, example, args.model_id, answers_file, visualizer)
            for example in tasks_to_run
        ]
        for f in tqdm(as_completed(futures), total=len(tasks_to_run), desc="Processing tasks"):
            f.result()

    # for example in tasks_to_run:
    #     answer_single_question(example, args.model_id, answers_file, visualizer)
    print("All tasks processed.")


if __name__ == "__main__":
    main()