from celery_app import celery

@celery.task
def check_for_violations():
    print("Checking for drone violations...")
    return "Violation check complete."