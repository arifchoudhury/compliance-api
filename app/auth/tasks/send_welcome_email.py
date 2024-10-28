from flask import current_app
from app import celery
from app.utils.helpers import send_email_task

@celery.task
def send_welcome_email(email, fullname):

    print(f"Sending welcome email to {fullname} at {email}")
    _ = send_email_task(
        email, "Welcome", "Welcome!!!"
    )
        
