import logging
import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable

from agents.email_template import render_email_html

logger = logging.getLogger(__name__)

LOGO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "assets",
    "nexa_bank_logo.png",
)


class EmailService:
    """
    Thin wrapper around SMTP sending, used only after an email has
    been human-approved. Sends the branded Nexa Bank HTML template
    (agents/email_template.py) with the logo embedded inline, with a
    plain-text fallback for clients that don't render HTML.

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

        logger.info(
            "EmailService initialized | host=%s | port=%s | configured=%s",
            self.host, self.port, bool(self.host and self.username and self.password),
        )

    def send_email(
        self,
        recipients: Iterable[str],
        subject: str,
        body: str,
    ) -> dict:

        recipients = list(recipients)

        logger.info(
            "EMAIL_SERVICE | send_email | recipients=%d | subject=%r",
            len(recipients), subject,
        )

        if not recipients:
            logger.warning("EMAIL_SERVICE | send_email | no recipients, skipping")
            return {
                "status": "skipped",
                "reason": "no recipients",
            }

        if not self.host or not self.username or not self.password:
            logger.error(
                "EMAIL_SERVICE | send_email | SMTP not configured "
                "(missing SMTP_HOST/SMTP_USERNAME/SMTP_PASSWORD)"
            )
            raise RuntimeError(
                "SMTP is not configured. Set SMTP_HOST, SMTP_USERNAME "
                "and SMTP_PASSWORD environment variables."
            )

        message = self._build_message(recipients, subject, body)

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_email, recipients, message.as_string())
        except Exception:
            logger.exception(
                "EMAIL_SERVICE | send_email | SMTP send failed | host=%s",
                self.host,
            )
            raise

        logger.info(
            "EMAIL_SERVICE | send_email | sent successfully | recipients=%d",
            len(recipients),
        )

        return {
            "status": "sent",
            "recipient_count": len(recipients),
        }

    def _build_message(
        self,
        recipients: list[str],
        subject: str,
        body: str,
    ) -> MIMEMultipart:
        """
        Builds a multipart/related message: an alternative part with
        both plain-text and branded HTML versions, plus the logo
        attached inline (referenced by the HTML via cid:nexa_bank_logo).
        """

        message = MIMEMultipart("related")
        message["From"] = self.from_email
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject

        alternative = MIMEMultipart("alternative")
        message.attach(alternative)

        # Plain-text fallback for clients that don't render HTML.
        alternative.attach(MIMEText(body, "plain"))

        # Branded HTML version.
        html_body = render_email_html(subject=subject, body=body)
        alternative.attach(MIMEText(html_body, "html"))

        # Inline logo, referenced by the HTML template as cid:nexa_bank_logo.
        try:
            with open(LOGO_PATH, "rb") as f:
                logo = MIMEImage(f.read())
                logo.add_header("Content-ID", "<nexa_bank_logo>")
                logo.add_header(
                    "Content-Disposition", "inline", filename="nexa_bank_logo.png"
                )
                message.attach(logo)
        except FileNotFoundError:
            logger.warning(
                "EMAIL_SERVICE | logo not found at %s, sending without it",
                LOGO_PATH,
            )

        return message