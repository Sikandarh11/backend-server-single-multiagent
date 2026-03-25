import os
import smtplib
from email.message import EmailMessage
from email.utils import parseaddr

from dotenv import load_dotenv

_ = load_dotenv()


def send_email(recipient, subject, body):
    """Send a real email via SMTP using .env credentials."""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_username or "")
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    if not all([smtp_host, smtp_username, smtp_password, smtp_from]):
        return (
            "Email failed: Missing SMTP config. "
            "Set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM in .env"
        )

    _, parsed_recipient = parseaddr(recipient)
    if not parsed_recipient or "@" not in parsed_recipient:
        return f"Email failed: Invalid recipient address '{recipient}'."

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_from
    msg["To"] = parsed_recipient
    msg.set_content(body)

    try:
        if smtp_use_tls:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20) as server:
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
    except Exception as exc:
        return f"Email failed: {exc}"

    return f"Sent! Email delivered to {parsed_recipient} with subject: {subject}"
