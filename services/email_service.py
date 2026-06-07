"""
email_service.py
----------------
Reusable SMTP-based email notification utility for the Achievement Management System.

Configuration is read from environment variables (or a .env file loaded by python-dotenv):

    MAIL_SERVER   - SMTP host                  (default: smtp.gmail.com)
    MAIL_PORT     - SMTP port                  (default: 587)
    MAIL_USE_TLS  - Use STARTTLS               (default: true)
    MAIL_USERNAME - Sender email address
    MAIL_PASSWORD - Sender email password / app-password
    MAIL_SENDER   - Display name + address     (default: MAIL_USERNAME)

Usage
-----
    from services.email_service import send_achievement_notification

    send_achievement_notification(
        student_email="student@example.com",
        student_name="Alice",
        event_name="National Hackathon",
        achievement_type="HACKATHON",
        position="1st",
    )

The function is intentionally fire-and-forget: it logs failures but never
raises exceptions so that a missing email configuration never crashes the
main application flow.
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_smtp_config() -> dict:
    """Read SMTP configuration from environment variables."""
    return {
        "server":   os.environ.get("MAIL_SERVER",   "smtp.gmail.com"),
        "port":     int(os.environ.get("MAIL_PORT", "587")),
        "use_tls":  os.environ.get("MAIL_USE_TLS", "true").lower() == "true",
        "username": os.environ.get("MAIL_USERNAME", ""),
        "password": os.environ.get("MAIL_PASSWORD", ""),
        "sender":   os.environ.get("MAIL_SENDER",   os.environ.get("MAIL_USERNAME", "")),
    }


def _send_email(to_address: str, subject: str, html_body: str) -> bool:
    """
    Low-level helper that connects to the SMTP server and sends one email.

    Returns True on success, False on any failure (after logging the error).
    """
    cfg = _get_smtp_config()

    if not cfg["username"] or not cfg["password"]:
        logger.warning(
            "Email not sent: MAIL_USERNAME or MAIL_PASSWORD is not configured. "
            "Set these environment variables to enable notifications."
        )
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = cfg["sender"]
    msg["To"]      = to_address
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(cfg["server"], cfg["port"], timeout=10) as smtp:
            if cfg["use_tls"]:
                smtp.starttls()
            smtp.login(cfg["username"], cfg["password"])
            smtp.sendmail(cfg["sender"], to_address, msg.as_string())
        logger.info("Achievement notification email sent to %s", to_address)
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error(
            "SMTP authentication failed. Check MAIL_USERNAME and MAIL_PASSWORD."
        )
    except smtplib.SMTPException as exc:
        logger.error("SMTP error while sending to %s: %s", to_address, exc)
    except OSError as exc:
        logger.error(
            "Network error sending email to %s: %s", to_address, exc
        )
    return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def send_achievement_notification(
    student_email: str,
    student_name: str,
    event_name: str,
    achievement_type: str,
    position: str,
) -> bool:
    """
    Send an email to a student when a new achievement is recorded for them.

    Parameters
    ----------
    student_email    : str  Recipient's email address.
    student_name     : str  Student's display name.
    event_name       : str  Name of the event / competition.
    achievement_type : str  Category code (e.g. 'HACKATHON', 'CODING').
    position         : str  Position achieved (e.g. '1st', 'Participant').

    Returns
    -------
    bool  True if the email was dispatched successfully, False otherwise.
    """
    subject = "New Achievement Added to Your Profile \U0001f3c6"

    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>New Achievement</title>
    </head>
    <body style="margin:0;padding:0;background-color:#f4f6f9;font-family:'Segoe UI',Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0"
             style="background-color:#f4f6f9;padding:40px 0;">
        <tr>
          <td align="center">
            <table width="600" cellpadding="0" cellspacing="0"
                   style="background:#ffffff;border-radius:12px;
                          box-shadow:0 4px 20px rgba(0,0,0,0.08);
                          overflow:hidden;max-width:600px;">

              <!-- Header -->
              <tr>
                <td style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                           padding:36px 40px;text-align:center;">
                  <h1 style="margin:0;color:#ffffff;font-size:24px;font-weight:700;
                             letter-spacing:0.5px;">
                    Achievement Management System
                  </h1>
                  <p style="margin:8px 0 0;color:rgba(255,255,255,0.85);font-size:14px;">
                    Celebrating Your Success
                  </p>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td style="padding:36px 40px;">
                  <p style="margin:0 0 16px;font-size:16px;color:#2d3748;">
                    Hello <strong>{student_name}</strong>,
                  </p>
                  <p style="margin:0 0 24px;font-size:15px;color:#4a5568;line-height:1.6;">
                    Great news! A new achievement has been recorded on your profile.
                    Keep up the excellent work!
                  </p>

                  <!-- Achievement Card -->
                  <table width="100%" cellpadding="0" cellspacing="0"
                         style="background:#f7f8fc;border-radius:10px;
                                border:1px solid #e2e8f0;margin-bottom:28px;">
                    <tr>
                      <td style="padding:24px 28px;">
                        <p style="margin:0 0 6px;font-size:11px;font-weight:700;
                                   text-transform:uppercase;letter-spacing:1.2px;
                                   color:#667eea;">
                          Achievement Details
                        </p>
                        <table width="100%" cellpadding="0" cellspacing="0">
                          <tr>
                            <td style="padding:10px 0;border-bottom:1px solid #e2e8f0;">
                              <span style="color:#718096;font-size:13px;">Event</span><br>
                              <strong style="color:#2d3748;font-size:15px;">{event_name}</strong>
                            </td>
                          </tr>
                          <tr>
                            <td style="padding:10px 0;border-bottom:1px solid #e2e8f0;">
                              <span style="color:#718096;font-size:13px;">Category</span><br>
                              <strong style="color:#2d3748;font-size:15px;">{achievement_type}</strong>
                            </td>
                          </tr>
                          <tr>
                            <td style="padding:10px 0;">
                              <span style="color:#718096;font-size:13px;">Position</span><br>
                              <strong style="color:#667eea;font-size:18px;">{position}</strong>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>

                  <p style="margin:0 0 28px;font-size:14px;color:#718096;line-height:1.6;">
                    Log in to the Achievement Management System to view your full profile
                    and download your certificate.
                  </p>

                  <!-- CTA Button -->
                  <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
                    <tr>
                      <td style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                                 border-radius:8px;">
                        <a href="#" style="display:inline-block;padding:14px 32px;
                                           color:#ffffff;font-size:15px;font-weight:600;
                                           text-decoration:none;">
                          View My Profile
                        </a>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="background:#f7f8fc;padding:20px 40px;text-align:center;
                           border-top:1px solid #e2e8f0;">
                  <p style="margin:0;font-size:12px;color:#a0aec0;">
                    This is an automated notification from
                    <strong>Achievement Management System</strong>.<br>
                    Please do not reply to this email.
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

    return _send_email(student_email, subject, html_body)
