from typing import List, Dict, Any
import uuid
from datetime import datetime
from .base import BaseLLM

class MockupLLM(BaseLLM):
    async def generate_course_outline(self, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "title": "Complete Python Programming: From Basics to Advanced",
            "description": "Master Python programming with this comprehensive course. Perfect for beginners and intermediate developers, this course covers everything from basic syntax to advanced concepts like web development, data science, and machine learning with Python. Through hands-on projects and practical examples, you'll gain the skills needed to build real-world applications.",
            "objectives": [
                "Write clean, efficient Python code following best practices",
                "Master object-oriented programming principles in Python",
                "Work with essential Python libraries for data science (NumPy, Pandas)",
                "Build web applications using Python frameworks",
                "Implement machine learning algorithms using Python",
                "Create real-world projects to apply your knowledge"
            ],
            "prerequisites": [
                "Basic computer skills",
                "Understanding of basic programming concepts (helpful but not required)",
                "Willingness to practice and learn"
            ],
            "totalDuration": "40 hours",
            "lessons": [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Getting Started with Python",
                    "description": "Introduction to Python programming and development environment setup",
                    "duration": "4 hours"
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Python Data Structures",
                    "description": "Deep dive into Python's built-in data structures and their applications",
                    "duration": "6 hours"
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Control Flow and Functions",
                    "description": "Learn about loops, conditionals, and function definitions in Python",
                    "duration": "5 hours"
                }
            ]
        }

    async def generate_lesson_detail(self, topic: str, content: Dict[str, Any]) -> Dict[str, Any]:
        if "Getting Started" in topic:
            return {
                "id": str(uuid.uuid4()),
                "title": "Getting Started with Python",
                "description": "Begin your Python journey with a comprehensive introduction to the language. This lesson covers the fundamentals of Python programming, from setting up your development environment to writing your first Python program.",
                "topics": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Introduction to Python",
                        "description": "Python is a high-level, interpreted programming language known for its simplicity and readability. Learn about Python's features and why it's one of the most popular programming languages today.",
                        "duration": "30 minutes"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Setting Up Your Development Environment",
                        "description": "Learn how to install Python and set up a code editor. We'll also cover virtual environments and package management.",
                        "duration": "45 minutes"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Basic Python Syntax",
                        "description": "Understand Python's syntax, including variables, data types, and basic operations.",
                        "duration": "1 hour"
                    }
                ],
                "resources": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "video",
                        "title": "Python for Beginners - Full Course",
                        "url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
                        "duration": "4 hours",
                        "source": "freeCodeCamp",
                        "description": "Comprehensive Python tutorial covering all the basics you need to get started."
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "video",
                        "title": "Python Crash Course",
                        "url": "https://www.youtube.com/watch?v=JJmcL1N2KQs",
                        "duration": "30 minutes",
                        "source": "Traversy Media",
                        "description": "Quick introduction to Python basics"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "article",
                        "title": "Python Tutorial - W3Schools",
                        "url": "https://www.w3schools.com/python/",
                        "source": "W3Schools",
                        "description": "Interactive Python tutorial with examples and exercises"
                    }
                ],
                "exercises": [
                    {
                        "question": "What is Python and why is it popular?",
                        "answer": "Python is a high-level, interpreted programming language known for its simplicity and readability. It's popular because it's easy to learn, has a large standard library, active community support, and is used in many fields including web development, data science, and AI."
                    },
                    {
                        "question": "What are the key features of Python?",
                        "answer": "Key features of Python include: easy-to-read syntax, dynamic typing, automatic memory management, large standard library, and cross-platform compatibility. It supports multiple programming paradigms including procedural, object-oriented, and functional programming."
                    }
                ],
                "duration": "4 hours"
            }
        elif "Data Structures" in topic:
            return {
                "id": str(uuid.uuid4()),
                "title": "Python Data Structures",
                "description": "Learn about Python's built-in data structures and how to use them effectively in your programs.",
                "topics": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Lists and Tuples",
                        "description": "Understanding sequence data types in Python and their operations.",
                        "duration": "1.5 hours"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Dictionaries and Sets",
                        "description": "Working with key-value pairs and unique collections in Python.",
                        "duration": "1.5 hours"
                    }
                ],
                "resources": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "video",
                        "title": "Python Data Structures Tutorial",
                        "url": "https://www.youtube.com/watch?v=R-HLU9Fl5ug",
                        "duration": "2 hours",
                        "source": "freeCodeCamp",
                        "description": "Complete guide to Python data structures"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "article",
                        "title": "Python Data Structures Documentation",
                        "url": "https://docs.python.org/3/tutorial/datastructures.html",
                        "source": "Python.org",
                        "description": "Official Python documentation on data structures"
                    }
                ],
                "exercises": [
                    {
                        "question": "What are the main differences between lists and tuples in Python?",
                        "answer": "Lists are mutable (can be modified after creation) while tuples are immutable (cannot be modified after creation). Lists use square brackets [] and tuples use parentheses (). Lists are typically used for collections of similar items that may change, while tuples are used for collections that should remain constant."
                    }
                ],
                "duration": "6 hours"
            }
        else:
            return {
                "id": str(uuid.uuid4()),
                "title": topic,
                "description": f"Learn about {topic} in detail",
                "topics": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": f"Understanding {topic}",
                        "description": f"Comprehensive overview of {topic} concepts",
                        "duration": "1 hour"
                    }
                ],
                "resources": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "video",
                        "title": f"{topic} Tutorial",
                        "url": "https://www.youtube.com/watch?v=example",
                        "duration": "1 hour",
                        "source": "YouTube",
                        "description": f"Learn {topic} from scratch"
                    }
                ],
                "exercises": [
                    {
                        "question": f"Explain the main concepts of {topic}",
                        "answer": f"This is a detailed explanation of the key concepts in {topic}"
                    }
                ],
                "duration": "2 hours"
            }

    async def chat(self, message: str) -> str:
        return "I understand you want to learn programming. Let's create a personalized learning path for you!" 