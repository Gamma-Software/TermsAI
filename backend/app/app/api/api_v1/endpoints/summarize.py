from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from app import models, schemas
from app.api import deps
from app.core.celery_app import celery_app
from celery.result import AsyncResult

router = APIRouter()


@router.post("/text", status_code=201)
async def summarize_text(
    text: schemas.SummarizeText,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Summarize text with LLM
    """
    task = celery_app.send_task("app.worker.summarize_text", args=[text.text])
    return {"id": task.id}



@router.get("/text")
async def get_summarize_result(
    id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get the result of summarizing text with LLM by id
    """
    task = AsyncResult(id, app=celery_app)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    # Get the status of the task
    if task.state == 'PENDING':
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Task is still pending")
    if task.state == 'FAILURE':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task failed")
    if task.state == 'SUCCESS':
        return {"status": task.state, "result": task.get()}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

@router.delete("/text")
async def delete_summarize_task(
    id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete the task of summarizing text with LLM by id
    """
    task = AsyncResult(id, app=celery_app)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    task = AsyncResult(id)
    task.revoke(terminate=True)