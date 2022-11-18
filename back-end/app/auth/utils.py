import emails
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def password_match(v: str, values) -> str:
    if " " in v:
        raise ValueError("password space")
    if len(v) < settings.PASSWORD_MIN_LENGTH or len(v) > settings.PASSWORD_MAX_LENGTH:
        raise ValueError("password length")
    if v != values.get("password"):
        raise ValueError("password mismatch")
    for letter in v:
        if letter not in settings.PASSWORD_CHARS:
            raise ValueError("password special")
    return v


async def send_email(data: dict):
    email = emails.Message(
        subject=data["email_subject"],
        html=data["email_body"],
        mail_to=[data["to_email"]],
        mail_from=data["from"],
    )
    await email.send(
        smtp=data["smtp"],
    )
