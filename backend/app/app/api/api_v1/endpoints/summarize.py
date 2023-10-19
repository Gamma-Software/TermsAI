from typing import Any

from fastapi import APIRouter, Depends

from app import models, schemas
from app.api import deps
from app.core.celery_app import celery_app

router = APIRouter()


@router.post("/text", status_code=201)
def summarize_text(
    text: schemas.SummarizeText,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Summarize text with LLM
    """
    celery_app.send_task("app.workers.summarizer.summarize_text", args=[text.text])
    return {"msg": "Summarizing"}