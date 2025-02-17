from pydantic import BaseModel
from typing import List, Optional, Dict


class ChatMessage(BaseModel):
    message: str
    conversation: List[Dict[str, str]]


class Conversation(BaseModel):
    conversation: List[dict]


class UserCreate(BaseModel):
    email: str
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

