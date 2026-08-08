from celery import Celery
from src.mail import mail, create_msg
from asgiref.sync import async_to_sync

c_app = Celery()
c_app.config_from_object('src.config')


@c_app.task()
def send_mail(emails: list[str], subject: str, temp_body: dict, temp_name: str):
    email_message = create_msg(
        recipients=emails,
        sub=subject,
        template_body=temp_body
    )

    # mail.send_message is async,
    # so inorder to run async fn in sync fn we need this
    async_to_sync(mail.send_message)(
        message = email_message,
        template_name = temp_name
    )
