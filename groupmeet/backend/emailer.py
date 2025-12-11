"""
Email delivery system with pluggable transporters.
Currently uses console printing for MVP.
"""
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EmailTransporter(ABC):
    """Abstract base class for email transporters."""
    
    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email. Returns True if successful."""
        pass


class ConsoleEmailTransporter(EmailTransporter):
    """Console-based email transporter (for development/testing)."""
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Print email to console instead of sending."""
        print("\n" + "="*60)
        print("📧 SIMULATED EMAIL")
        print("="*60)
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print("-"*60)
        print(body)
        print("="*60 + "\n")
        logger.info(f"Simulated email sent to {to}")
        return True


class SendGridTransporter(EmailTransporter):
    """SendGrid email transporter (for production)."""
    
    def __init__(self, api_key: str, from_email: str):
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            self.sg = sendgrid.SendGridAPIClient(api_key=api_key)
            self.from_email = from_email
            logger.info("SendGrid transporter initialized")
        except ImportError:
            raise ImportError("sendgrid not installed. Run: pip3 install sendgrid")
        except Exception as e:
            logger.error(f"SendGrid initialization failed: {e}")
            raise
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email via SendGrid."""
        try:
            from sendgrid.helpers.mail import Mail
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to,
                subject=subject,
                html_content=body
            )
            response = self.sg.send(message)
            logger.info(f"Email sent to {to} via SendGrid: {response.status_code}")
            return response.status_code in [200, 201, 202]
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False


class SMTPTransporter(EmailTransporter):
    """SMTP email transporter."""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        logger.info("SMTP transporter initialized")
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email via SMTP."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent to {to} via SMTP")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False


def get_email_transporter(config) -> EmailTransporter:
    """
    Factory function to get the appropriate email transporter.
    
    Args:
        config: Configuration object
        
    Returns:
        EmailTransporter instance
    """
    provider = config.EMAIL_PROVIDER.lower()
    
    if provider == 'sendgrid':
        try:
            return SendGridTransporter(
                config.SENDGRID_API_KEY,
                config.FROM_EMAIL
            )
        except Exception as e:
            logger.warning(f"SendGrid init failed: {e}. Falling back to console.")
            return ConsoleEmailTransporter()
    
    elif provider == 'smtp':
        try:
            return SMTPTransporter(
                config.SMTP_SERVER,
                config.SMTP_PORT,
                config.SMTP_USERNAME,
                config.SMTP_PASSWORD,
                config.FROM_EMAIL
            )
        except Exception as e:
            logger.warning(f"SMTP init failed: {e}. Falling back to console.")
            return ConsoleEmailTransporter()
    
    else:
        # Default to console
        return ConsoleEmailTransporter()


def generate_match_email(student_name: str, match_url: str, group_members: List[Dict[str, Any]]) -> str:
    """
    Generate HTML email body for match notification.
    
    Args:
        student_name: Name of the student
        match_url: Unique URL to view match results
        group_members: List of group member dictionaries
    
    Returns:
        HTML email body
    """
    members_html = ""
    for member in group_members:
        members_html += f"""
        <li>
            <strong>{member.get('name', 'Unknown')}</strong> 
            ({member.get('email', 'N/A')})<br>
            <em>Preference: {member.get('study_preference', 'N/A')}</em>
        </li>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #007bff; 
                      color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
            .group-list {{ list-style: none; padding: 0; }}
            .group-list li {{ padding: 10px; margin: 5px 0; background-color: #f8f9fa; 
                            border-left: 3px solid #007bff; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🎓 Your Study Group Match is Ready!</h2>
            <p>Hi {student_name},</p>
            <p>Great news! We've matched you with a study group. Here are your group members:</p>
            <ul class="group-list">
                {members_html}
            </ul>
            <p>Click the button below to view your full match details, including shared availability and study preferences:</p>
            <a href="{match_url}" class="button">View My Match</a>
            <p>If you have any questions or need to make changes, please contact us.</p>
            <p>Good luck with your studies!</p>
            <p>— The GroupMeet Team</p>
        </div>
    </body>
    </html>
    """
    return html


def send_match_notification(
    transporter: EmailTransporter,
    student_email: str,
    student_name: str,
    match_url: str,
    group_members: List[Dict[str, Any]],
    config
) -> bool:
    """
    Send match notification email to a student.
    
    Args:
        transporter: Email transporter instance
        student_email: Student's email address
        student_name: Student's name
        match_url: URL to view match results
        group_members: List of group members
        config: Configuration object
        
    Returns:
        True if email sent successfully
    """
    subject = "🎓 Your Study Group Match is Ready!"
    body = generate_match_email(student_name, match_url, group_members)
    
    return transporter.send_email(student_email, subject, body)

