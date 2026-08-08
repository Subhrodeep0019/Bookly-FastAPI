from fastapi_mail import (FastMail, ConnectionConfig,
                          MessageSchema, MessageType)
from .config import setting
from pathlib import Path
from typing import List, Any

BASE_DIR = Path(__file__).resolve().parent

conf = ConnectionConfig(
    MAIL_USERNAME = setting.MAIL_USERNAME,
    MAIL_PASSWORD = setting.MAIL_PASSWORD,
    MAIL_FROM = setting.MAIL_FROM,
    MAIL_FROM_NAME= setting.MAIL_FROM_NAME,
    MAIL_PORT = setting.MAIL_PORT,
    MAIL_SERVER = setting.MAIL_SERVER,
    MAIL_STARTTLS = setting.MAIL_STARTTLS,
    MAIL_SSL_TLS = setting.MAIL_SSL_TLS,
    USE_CREDENTIALS = setting.USE_CREDENTIALS,
    VALIDATE_CERTS = setting.VALIDATE_CERTS,
    TEMPLATE_FOLDER= Path(BASE_DIR, "templates")
)



mail =  FastMail(conf)

def create_msg(recipients: List[str], sub: str, template_body: dict[str, Any]):
    message = MessageSchema(
        subject= sub,
        recipients= recipients,
        template_body= template_body,
        subtype= MessageType.html
    )
    return message
