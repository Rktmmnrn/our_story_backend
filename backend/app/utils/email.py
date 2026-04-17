"""
Async email sender using aiosmtplib.
Only used for couple invitation emails.
"""
import logging

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings


logger = logging.getLogger(__name__)


def _build_invite_html(inviter_name: str, invite_link: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <style>
        body {{ font-family: Arial, sans-serif; background: #fdf0f4; margin: 0; padding: 0; }}
        .container {{ max-width: 560px; margin: 40px auto; background: #fff;
                      border-radius: 12px; overflow: hidden;
                      box-shadow: 0 4px 24px rgba(199,75,120,0.1); }}
        .header {{ background: #C74B78; padding: 36px; text-align: center; }}
        .header h1 {{ color: #fff; margin: 0; font-size: 28px; }}
        .header p {{ color: #f9c6d8; margin: 8px 0 0; }}
        .body {{ padding: 36px; color: #333; line-height: 1.7; }}
        .btn {{ display: inline-block; margin: 24px 0; padding: 14px 36px;
                background: #C74B78; color: #fff; border-radius: 8px;
                text-decoration: none; font-size: 16px; font-weight: bold; }}
        .footer {{ padding: 20px 36px; font-size: 12px; color: #aaa;
                   border-top: 1px solid #f0e0e6; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>♡ Notre Histoire</h1>
          <p>Application de souvenirs en couple</p>
        </div>
        <div class="body">
          <p>Bonjour,</p>
          <p><strong>{inviter_name}</strong> vous invite à partager votre histoire
          ensemble sur <strong>Notre Histoire</strong>.</p>
          <p>Cliquez sur le bouton ci-dessous pour rejoindre et commencer à
          archiver vos plus beaux souvenirs.</p>
          <p style="text-align:center;">
            <a class="btn" href="{invite_link}">Rejoindre notre histoire ♡</a>
          </p>
          <p style="color:#888; font-size:13px;">
            Ce lien expire dans <strong>24 heures</strong>.<br>
            Si vous ne connaissez pas {inviter_name}, ignorez cet email.
          </p>
        </div>
        <div class="footer">
          Notre Histoire — Parce que chaque instant compte.
        </div>
      </div>
    </body>
    </html>
    """


async def send_invite_email(
    recipient_email: str,
    inviter_name: str,
    invite_link: str,
) -> bool:
    """
    Sends a couple invitation email.
    Returns True on success, False on failure (non-blocking).
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{inviter_name} vous invite sur Notre Histoire ♡"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = recipient_email

    plain_text = (
        f"Bonjour,\n\n"
        f"{inviter_name} vous invite à partager votre histoire sur Notre Histoire.\n\n"
        f"Rejoignez-les ici : {invite_link}\n\n"
        f"Ce lien expire dans 24 heures.\n"
    )

    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(_build_invite_html(inviter_name, invite_link), "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info(f"Invitation email sent to {recipient_email}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send invitation email to {recipient_email}: {exc}")
        return False