from celery import Celery

celery_app = Celery("worker", broker="amqp://guest@queue//", backend="amqp://guest@queue//")

celery_app.conf.task_routes = {
    "app.worker.test_celery": "main-queue",
    "app.worker.summarize_text": "main-queue",
}
#celery_app.conf.task_reject_on_worker_lost = True
