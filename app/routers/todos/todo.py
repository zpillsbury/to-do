from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models import GenericException
from app.utils.auth import validate_access
from app.utils.config import db

from .models import CreateTodo, SuccessResult, Todo, TodoId, UpdateTodo

router = APIRouter(
    prefix="/todo",
    tags=["TODO"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": GenericException,
        }
    },
)

security = HTTPBearer()


@router.post("")
async def create_to_do(
    new_todo: CreateTodo,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user: Annotated[None | str, Depends(validate_access)],
) -> TodoId:
    """
    Create a new todo
    """
    data = new_todo.model_dump() | {"user": user} | {"completed": False}
    result = await db.todos.insert_one(data)

    id = str(result.inserted_id)

    return TodoId(id=id)


@router.get("")
async def get_all_todos(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user: Annotated[None | str, Depends(validate_access)],
) -> list[Todo]:
    """
    Get all todos
    """
    results = []
    async for doc in db.todos.find({"user": user}):
        results.append(
            Todo(
                id=str(doc.get("_id")),
                user=doc.get("user"),
                title=doc.get("title"),
                description=doc.get("description"),
                completed=doc.get("completed"),
            )
        )

    return results


@router.get("{todo_id}")
async def get_one_todo(
    todo_id: str,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user: Annotated[None | str, Depends(validate_access)],
) -> Todo:
    """
    Get todo by ID
    """
    todo_object_id = ObjectId(todo_id)

    doc = await db.todos.find_one({"_id": todo_object_id, "user": user})
    if not doc:
        raise HTTPException(status_code=404, detail="Todo not found")

    return Todo(
        id=str(doc.get("_id")),
        user=doc.get("user"),
        title=doc.get("title"),
        description=doc.get("description"),
        completed=doc.get("completed"),
    )


@router.patch("{todo_id}")
async def update_one_todo(
    todo_id: str,
    todo_update: UpdateTodo,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user: Annotated[None | str, Depends(validate_access)],
) -> SuccessResult:
    """
    Update todo by ID
    """
    todo_object_id = ObjectId(todo_id)

    update_data = todo_update.model_dump(exclude_unset=True)

    update_result = await db.todos.update_one(
        {"_id": todo_object_id, "user": user}, {"$set": update_data}
    )

    if update_result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found."
        )

    return SuccessResult(success=True)


@router.delete("{todo_id}")
async def delete_one_todo(
    todo_id: str,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user: Annotated[None | str, Depends(validate_access)],
) -> SuccessResult:
    """
    Delete todo by ID
    """
    todo_object_id = ObjectId(todo_id)

    delete_result = await db.todos.delete_one({"_id": todo_object_id, "user": user})

    if delete_result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found."
        )

    return SuccessResult(success=True)
