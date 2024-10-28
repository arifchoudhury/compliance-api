from flask import current_app
from app import celery
from app.utils.helpers import send_email_task

@celery.task
def send_forgot_password_email(email, subject, body):
    print("sending forgot password email")
    
    _ = send_email_task(
        email, subject, body
    )