from celery_app import celery

@celery.task
def check_for_violations():
    print("Checking for drone violations...")
    # Here you would implement the logic to check for violations
    # quesring an API, "in the main we already implemented a fastapi endpoint"
    # should implement a class that handle the logic for checking violations
    

    return "Violation check complete."