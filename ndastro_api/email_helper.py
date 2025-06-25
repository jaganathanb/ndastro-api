"""Helper functions and classes for sending emails, rendering templates, and handling password reset tokens in the ndastro API."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import emails  # type: ignore[import-untyped]
import jwt
from jinja2 import Template
from jwt.exceptions import InvalidTokenError

from ndastro_api.core import security
from ndastro_api.core.config import settings
from ndastro_api.core.exceptions import EmailConfigurationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    """Data class representing the content and subject of an email.

    Attributes
    ----------
    html_content : str
        The HTML content of the email.
    subject : str
        The subject line of the email.

    """

    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    """Render an email template with the given context.

    Parameters
    ----------
    template_name : str
        The name of the template file to render.
    context : dict[str, Any]
        The context dictionary to use for rendering the template.

    Returns
    -------
    str
        The rendered HTML content as a string.

    """
    template_str = (Path(__file__).parent / "email-templates" / "build" / template_name).read_text()
    return Template(template_str).render(context)


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    """Send an email using the configured SMTP server.

    Parameters
    ----------
    email_to : str
        The recipient's email address.
    subject : str, optional
        The subject line of the email (default is an empty string).
    html_content : str, optional
        The HTML content of the email (default is an empty string).

    Raises
    ------
    EmailConfigurationError
        If email sending is not enabled in the settings.

    """
    if not settings.emails_enabled:
        raise EmailConfigurationError
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info("send email result: %s", response)


def generate_test_email(email_to: str) -> EmailData:
    """Generate a test email for the specified recipient.

    Args:
        email_to (str): The recipient's email address.

    Returns:
        EmailData: An object containing the HTML content and subject of the test email.

    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    """Generate the email content and subject for a password reset request.

    Args:
        email_to (str): The recipient's email address.
        email (str): The username or email of the user requesting the password reset.
        token (str): The password reset token to be included in the reset link.

    Returns:
        EmailData: An object containing the HTML content and subject for the reset password email.

    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str,
    username: str,
    password: str,
) -> EmailData:
    """Generate an email for new account creation with username and password.

    Parameters
    ----------
    email_to : str
        The recipient's email address.
    username : str
        The username for the new account.
    password : str
        The password for the new account.

    Returns
    -------
    EmailData
        The email content and subject for the new account notification.

    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.FRONTEND_HOST,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_token(email: str) -> str:
    """Generate a JWT token for password reset purposes for the given email address.

    The token includes an expiration time based on the configured number of hours,
    the issued-at time, and the subject (user's email). The token is signed using
    the application's secret key and specified algorithm.

    Args:
        email (str): The email address for which to generate the password reset token.

    Returns:
        str: The encoded JWT token as a string.

    """
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    return jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )


def verify_password_reset_token(token: str) -> str | None:
    """Verify a password reset token and return the associated email if valid.

    Parameters
    ----------
    token : str
        The JWT password reset token to verify.

    Returns
    -------
    str | None
        The email address if the token is valid, otherwise None.

    """
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None
