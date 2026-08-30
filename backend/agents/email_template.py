import html
import logging

logger = logging.getLogger(__name__)

BRAND_NAME = "Nexa Bank"
BRAND_PRIMARY_COLOR = "#0b3d66"   # dark navy, matches the logo background
BRAND_ACCENT_COLOR = "#4fb3e8"    # light blue accent, matches the "N" icon


def _body_text_to_html(body: str) -> str:
    """
    The AI-generated email body (from EmailGeneratorTool) is plain
    text with blank-line-separated paragraphs. Convert that into
    simple HTML paragraphs so it renders nicely inside the template
    instead of collapsing all whitespace, without needing the
    generator itself to know anything about HTML.
    """

    paragraphs = [p.strip() for p in body.strip().split("\n\n") if p.strip()]

    html_paragraphs = []

    for paragraph in paragraphs:
        # Preserve single line breaks within a paragraph (e.g. a
        # signature block) as <br>, escaping first so the body text
        # can never inject markup into the email.
        escaped = html.escape(paragraph).replace("\n", "<br>")
        html_paragraphs.append(f'<p style="margin:0 0 16px;">{escaped}</p>')

    return "".join(html_paragraphs)


def render_email_html(subject: str, body: str) -> str:
    """
    Wraps an AI-generated subject/body in Nexa Bank's branded HTML
    email template. The logo is referenced as cid:nexa_bank_logo,
    which email_service.py attaches inline — see
    agents/assets/nexa_bank_logo.png.
    """

    body_html = _body_text_to_html(body)
    escaped_subject = html.escape(subject)

    return f"""\
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{escaped_subject}</title>
        </head>
        <body style="margin:0; padding:0; background-color:#f3f4f6; font-family: Arial, Helvetica, sans-serif;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6; padding:24px 0;">
            <tr>
                <td align="center">
                <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                    <td style="background-color:{BRAND_PRIMARY_COLOR}; padding:20px 32px;">
                        <!-- The logo file is the full brand lockup (icon +
                            "Nexa Bank" wordmark) at a 349x136 native
                            aspect ratio, not a standalone square icon.
                            Sizing it to that ratio (not a forced square)
                            and not adding a separate text label next to
                            it, since the wordmark is already baked into
                            the image. -->
                        <img src="cid:nexa_bank_logo" alt="{BRAND_NAME}" width="164" height="64" style="display:block;">
                    </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                    <td style="padding:32px; color:#1f2937; font-size:15px; line-height:1.6;">
                        {body_html}
                    </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                    <td style="background-color:#f9fafb; padding:20px 32px; border-top:1px solid #e5e7eb;">
                        <p style="margin:0; color:#6b7280; font-size:12px; line-height:1.5;">
                        This email was sent by {BRAND_NAME}. If you weren't expecting this message, please contact our support team.<br>
                        &copy; {BRAND_NAME}. All rights reserved.
                        </p>
                    </td>
                    </tr>

                </table>
                </td>
            </tr>
            </table>
        </body>
        </html>
        """