from pathlib import Path

from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings


config = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME='Constantine Zagorodnyi',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates'
)

async def send_email(email: EmailStr, host: str):
    try:
        verification_token = await auth_service.create_verification_token({'sub': email})
        message = MessageSchema(
            subject='MyHW13: Verify your email',
            recipients=[email],
            template_body={'host': host, 'token': verification_token},
            subtype=MessageType.html
        )
        fm = FastMail(config)
        await fm.send_message(message, template_name='verification_email.html')
    except ConnectionErrors as err:
        print(err)
    
