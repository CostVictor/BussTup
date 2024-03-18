from app import celery

@celery.task
def teste(a, b):
  return a + b
