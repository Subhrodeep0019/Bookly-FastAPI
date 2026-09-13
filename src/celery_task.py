# from celery import Celery
# from src.mail import mail, create_msg
# from asgiref.sync import async_to_sync
#
# c_app = Celery()
# c_app.config_from_object('src.config')
#
#
# @c_app.task()
# def send_mail(emails: list[str], subject: str, temp_body: dict, temp_name: str):
#     email_message = create_msg(
#         recipients=emails,
#         sub=subject,
#         template_body=temp_body
#     )
#
#     # mail.send_message is async,
#     # so inorder to run async fn in sync fn we need this
#     async_to_sync(mail.send_message)(
#         message = email_message,
#         template_name = temp_name
#     )


import resend
from celery import Celery
from jinja2 import Environment, FileSystemLoader
from src.config import Settings

c_app = Celery()
c_app.config_from_object('src.config')

resend.api_key = Settings.RESEND_API_KEY

jinja_env = Environment(loader=FileSystemLoader("src/templates"))

@c_app.task()
def send_mail(emails: list[str], subject: str, temp_body: dict, temp_name: str):
    template = jinja_env.get_template(temp_name)
    html_content = template.render(**temp_body)

    return resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": emails,
        "subject": subject,
        "html": html_content,
    })