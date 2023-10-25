from typing import Any
import tempfile
import shutil

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import UploadFile, File
from app import models, schemas
from app.api import deps
from app.core.celery_app import celery_app
from celery.result import AsyncResult

router = APIRouter()

@router.post("/text", status_code=201)
async def question_text(
    terms: str,
    question: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Question text with LLM
    """
    task = celery_app.send_task("app.worker.question_text", args=[question, terms])
    return {"id": task.id}


@router.post("/file", status_code=201)
async def question_file(
    file: UploadFile = File(...),
    question: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Question file with LLM
    """
    # Get the file size (in bytes)
    file.file.seek(0, 2)
    file_size = file.file.tell()

    # move the cursor back to the beginning
    await file.seek(0)

    if file_size > 2 * 1024 * 1024:
        # more than 2 MB
        raise HTTPException(status_code=400, detail="File too large, only files up to 2 MB are supported")

    # check the content type (MIME type)
    content_type = file.content_type
    if content_type not in ["text/plain", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file type, only text/plain or pdf "
                            "and application/pdf are supported")

    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp.flush()
        with open(tmp.name, "r", encoding="iso-8859-1") as f:
            contents = f.read()

    task = celery_app.send_task(
        "app.worker.question_text",
        args=[contents, question]
    )
    return {"id": task.id}


@router.post("/url", status_code=201)
async def question_url(
    url: str,
    question: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Question content of a web page
    """
    task = celery_app.send_task(
        "app.worker.question_url",
        args=[url, question]
    )
    return {"id": task.id}


@router.get("/task")
async def get_question_result(
    id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get the result of Question text with LLM by id
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


@router.delete("/task")
async def delete_question_task(
    id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete the task of Questionng text with LLM by id
    """
    task = AsyncResult(id, app=celery_app)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    task = AsyncResult(id)
    task.revoke(terminate=True)
