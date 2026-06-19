from __future__ import annotations

import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from app.core.config import settings
from app.core.exceptions import AppException


def send_registration_code(email: str, code: str) -> None:
    if not settings.smtp_host or not settings.smtp_from_email:
        raise AppException("邮件服务尚未配置，请联系管理员")

    message = EmailMessage()
    message["Subject"] = f"{settings.smtp_from_name} 注册验证码"
    message["From"] = formataddr((settings.smtp_from_name, settings.smtp_from_email))
    message["To"] = email
    message.set_content(
        f"你的注册验证码是：{code}\n\n"
        f"验证码在 {settings.email_code_expire_minutes} 分钟内有效。如非本人操作，请忽略此邮件。"
    )

    html_content = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 40px; border-radius: 16px; background-color: #ffffff; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.04); border: 1px solid #f3f4f6;">
        <div style="text-align: center; margin-bottom: 32px;">
            <h2 style="color: #111827; font-size: 24px; font-weight: 600; margin: 0; letter-spacing: -0.025em;">验证您的邮箱</h2>
        </div>
        <p style="color: #4b5563; font-size: 15px; line-height: 1.6; margin: 0 0 24px 0; text-align: center;">
            欢迎使用 <strong>{settings.smtp_from_name}</strong>。请使用以下验证码完成验证：
        </p>
        <div style="text-align: center; margin-bottom: 32px;">
            <div style="display: inline-block; background-color: #f9fafb; color: #111827; font-size: 32px; font-weight: 700; letter-spacing: 0.25em; padding: 16px 32px; border-radius: 12px; border: 1px solid #e5e7eb; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);">
                {code}
            </div>
        </div>
        <div style="border-top: 1px solid #f3f4f6; padding-top: 24px; text-align: center;">
            <p style="color: #9ca3af; font-size: 13px; line-height: 1.5; margin: 0;">
                验证码在 <strong>{settings.email_code_expire_minutes} 分钟</strong> 内有效。<br>
                如非本人操作，请忽略此邮件。
            </p>
        </div>
    </div>
    <div style="text-align: center; margin-top: 24px;">
        <p style="color: #d1d5db; font-size: 12px; margin: 0;">&copy; {settings.smtp_from_name}. All rights reserved.</p>
    </div>
    """
    message.add_alternative(html_content, subtype='html')

    try:
        smtp_class = smtplib.SMTP_SSL if settings.smtp_use_ssl else smtplib.SMTP
        with smtp_class(settings.smtp_host, settings.smtp_port, timeout=settings.smtp_timeout) as server:
            if not settings.smtp_use_ssl and settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_username:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise AppException("验证码发送失败，请稍后重试") from exc
