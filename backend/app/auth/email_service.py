import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, raw_token: str) -> bool:
    """
    Sends an email containing the password reset link with the raw token.
    If SMTP is not configured or fails, logs the link clearly for dev/testing.
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
    
    subject = "Shadow AI Sentinel - Password Reset Request"
    body_text = f"""Hello,

You requested a password reset for your Shadow AI Sentinel account.
Click the link below (valid for {settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes):

{reset_url}

If you did not request this, please ignore this email.

— Shadow AI Sentinel Security Team
"""
    body_html = f"""
    <div style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 24px; border-radius: 8px;">
        <h2 style="color: #38bdf8; margin-top: 0;">Shadow AI Sentinel</h2>
        <p>You requested a password reset for your account.</p>
        <div style="margin: 20px 0;">
            <a href="{reset_url}" style="background-color: #0284c7; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Reset Password</a>
        </div>
        <p style="color: #94a3b8; font-size: 13px;">This link will expire in {settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes.<br>Or copy this URL: {reset_url}</p>
        <hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;">
        <p style="color: #64748b; font-size: 12px;">If you did not request this, you can safely disregard this email.</p>
    </div>
    """

    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.info(f"[DEV / DEMO EMAIL] Password reset requested for {to_email}. Reset link: {reset_url}")
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email
        msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, [to_email], msg.as_string())
        
        logger.info(f"Password reset email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email}: {e}")
        # Return true so we don't leak failures or user existence
        return False
