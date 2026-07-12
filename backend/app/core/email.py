import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from ..config import settings


def _dotenv_value(key: str) -> str:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return ""
    for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip().lstrip("\ufeff")
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == key:
            return value.strip().strip('"').strip("'")
    return ""


def _smtp_settings() -> dict:
    user = settings.SMTP_USER or os.getenv("SMTP_USER", "") or _dotenv_value("SMTP_USER")
    password = settings.SMTP_PASSWORD or os.getenv("SMTP_PASSWORD", "") or _dotenv_value("SMTP_PASSWORD")
    host = settings.SMTP_HOST or os.getenv("SMTP_HOST", "") or _dotenv_value("SMTP_HOST") or "smtp.zoho.com"
    port = settings.SMTP_PORT or int(os.getenv("SMTP_PORT", "") or _dotenv_value("SMTP_PORT") or 587)
    return {"user": user, "password": password, "host": host, "port": int(port)}


def send_html_email(
    recipients: list[str],
    subject: str,
    html_body: str,
    sender_email: str | None = None,
    sender_name: str | None = None,
) -> str | None:
    clean_recipients = [email.strip() for email in recipients if (email or "").strip()]
    if not clean_recipients:
        return "No hay destinatarios activos"

    smtp = _smtp_settings()
    if not smtp["user"] or not smtp["password"]:
        return "SMTP sin configurar. Define SMTP_USER y SMTP_PASSWORD en .env"

    from_email = (sender_email or smtp["user"]).strip()
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{sender_name} <{from_email}>" if sender_name else from_email
    message["To"] = ", ".join(clean_recipients)
    message.set_content("Se requiere un cliente de correo compatible con HTML.")
    message.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(smtp["host"], smtp["port"]) as client:
            client.starttls()
            client.login(smtp["user"], smtp["password"])
            client.send_message(message)
    except Exception as exc:
        return f"Error SMTP: {exc.__class__.__name__}"
    return None
