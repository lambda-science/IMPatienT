import time
from app import create_app
from rq import get_current_job
from app import db
from app.models import Task, User, Image
import sys
import json
from flask import render_template
from app.email import send_email

app = create_app()
app.app_context().push()


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()
        task = Task.objects(rq_id=job.get_id()).first()
        # task.user.add_notification(
        #     "task_progress", {"task_id": job.get_id(), "progress": progress}
        # )
        if progress >= 100:
            task.complete = True
        task.save()


def export_data(user_id):
    try:
        user = User.objects(id=user_id).first()
        _set_task_progress(0)
        data = []
        i = 0
        total_images = len(Image.objects.all())
        for image in Image.objects.all():
            data.append(
                {"image_name": image.image_name, "image_path": image.image_path}
            )
            time.sleep(5)
            i += 1
            _set_task_progress(100 * i // total_images)
        send_email(
            "[IMPatienT] Your Data",
            sender=app.config["ADMINS_EMAIL"][0],
            recipients=[user.email],
            text_body=render_template("email/export_data.txt", user=user),
            html_body=render_template("email/export_data.html", user=user),
            attachments=[
                (
                    "image.json",
                    "application/json",
                    json.dumps({"image": data}, indent=4),
                )
            ],
            sync=True,
        )
    except:
        app.logger.error("Unhandled exception", exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)
