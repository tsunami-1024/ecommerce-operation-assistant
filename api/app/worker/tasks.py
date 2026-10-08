from app.services.generation_jobs import run_generation_job
from app.worker.celery_app import celery_app


@celery_app.task(name="generation.run_generation_job")
def run_generation_job_task(job_id: int) -> None:
    run_generation_job(job_id, worker_id="celery-worker")