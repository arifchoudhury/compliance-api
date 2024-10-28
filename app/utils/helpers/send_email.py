import boto3
# from celery import Celery
from flask import current_app
# from app.extensions import celery

# Initialize Celery and other extensions (as shown before)
# celery = Celery(__name__)

# # Task to send email using AWS SES
# @celery.task
def send_email_task(to_email, subject, body):
    ses = boto3.client(
        'ses',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_REGION']
    )
    
    try:
        response = ses.send_email(
            Source=current_app.config['AWS_SES_EMAIL_SOURCE'],
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body}
                }
            }
        )
        current_app.logger.info(f"Email sent")
        return response
    except Exception as e:
        # Handle any exceptions that occur during the email sending process
        current_app.logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return None
