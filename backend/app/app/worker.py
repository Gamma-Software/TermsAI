from raven import Client

from app.core.celery_app import celery_app
from app.core.config import settings
from app.llm.chains import summarize_chain_exec, summarize_chain_url_exec


client_sentry = Client(settings.SENTRY_DSN)


@celery_app.task(reject_on_worker_lost=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task(reject_on_worker_lost=True)
def summarize_text(text: str) -> str:
    summary = summarize_chain_exec(text)
    return summary


@celery_app.task(reject_on_worker_lost=True)
def summarize_url(url: str) -> str:
    summary = summarize_chain_url_exec(url)
    return summary

