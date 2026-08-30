import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable


class EmailService:
    """
    Thin wrapper around SMTP sending, used only after an email has
    been human-approved.

    Configure via environment variables:
      SMTP_HOST, SMTP_PORT (default 587), SMTP_USERNAME, SMTP_PASSWORD,
      SMTP_FROM_EMAIL (defaults to SMTP_USERNAME), SMTP_USE_TLS
      (default "true")

    send_email() is synchronous / blocking (smtplib has no async API).
    Call it via run_in_threadpool from async FastAPI routes rather
    than awaiting it directly, the same way the rest of this codebase
    runs the LLM agent calls off the event loop.
    """

    def __init__(self):
        self.host = os.getenv("SMTP_HOST")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", self.username)
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    def send_email(
        self,
        recipients: Iterable[str],
        subject: str,
        body: str,
    ) -> dict:

        recipients = list(recipients)

        if not recipients:
            return {
                "status": "skipped",
                "reason": "no recipients",
            }

        if not self.host or not self.username or not self.password:
            raise RuntimeError(
                "SMTP is not configured. Set SMTP_HOST, SMTP_USERNAME "
                "and SMTP_PASSWORD environment variables."
            )

        message = MIMEMultipart()
        message["From"] = self.from_email
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(self.host, self.port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.from_email, recipients, message.as_string())

        return {
            "status": "sent",
            "recipient_count": len(recipients),
        }
