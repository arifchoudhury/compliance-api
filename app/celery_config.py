# app/celery_config.py

from celery import Celery

def make_celery(app):
    """
    Create a new Celery object, tie the Celery config to the Flask app config,
    and define the Flask application context for Celery tasks.
    """
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
