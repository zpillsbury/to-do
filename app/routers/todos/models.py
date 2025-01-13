from typing import Optional

from pydantic import BaseModel


class Todo(BaseModel):
    id: str
    user: str
    title: str
    description: str
    completed: bool


class CreateTodo(BaseModel):
    title: str
    description: Optional[str]


class UpdateTodo(BaseModel):
    title: Optional[str]
    description: Optional[str]
    completed: Optional[bool]


class TodoId(BaseModel):
    id: str


class SuccessResult(BaseModel):
    success: bool
