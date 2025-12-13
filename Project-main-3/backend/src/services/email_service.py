"""
Email service using SendGrid.
"""
import sendgrid
from sendgrid.helpers.mail import Mail
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SendGrid."""
    
    def __init__(self, api_key: str, from_email: str):
        """
        Initialize email service.
        
        Args:
            api_key: SendGrid API key
            from_email: From email address
        """
        if not api_key:
            logger.warning("SendGrid API key not provided, email service will not work")
            self.sg = None
        else:
            try:
                self.sg = sendgrid.SendGridAPIClient(api_key=api_key)
            except Exception as e:
                logger.error(f"Failed to initialize SendGrid: {e}")
                self.sg = None
        
        self.from_email = from_email
    
    def send_group_intro_email(self, group: Dict):
        """
        Send introduction email to all group members.
        
        Args:
            group: Match/group dictionary
        """
        if not self.sg:
            logger.warning("SendGrid not initialized, skipping email")
            return
        
        members = group.get('members', [])
        course = group.get('course', '')
        suggested_time = group.get('suggested_meeting_time', '')
        group_id = group.get('group_id', '')
        
        for member in members:
            try:
                member_email = member.get('email') or f"{member.get('pennkey')}@upenn.edu"
                member_name = member.get('name') or member.get('pennkey', 'Student')
                
                # Generate email content
                html_content = self._generate_group_intro_html(
                    group, member_name, member_email
                )
                
                message = Mail(
                    from_email=self.from_email,
                    to_emails=member_email,
                    subject=f"Your {course} Study Group is Ready!",
                    html_content=html_content
                )
                
                response = self.sg.send(message)
                logger.info(f"Sent group intro email to {member_email} (status: {response.status_code})")
                
            except Exception as e:
                logger.error(f"Error sending email to {member.get('email')}: {e}")
    
    def send_feedback_reminder(self, match: Dict, days_after: int = 5):
        """
        Send feedback reminder after match.
        
        Args:
            match: Match dictionary
            days_after: Days after match to send reminder
        """
        if not self.sg:
            logger.warning("SendGrid not initialized, skipping email")
            return
        
        members = match.get('members', [])
        course = match.get('course', '')
        match_id = match.get('match_id', '')
        
        for member in members:
            try:
                member_email = member.get('email') or f"{member.get('pennkey')}@upenn.edu"
                member_name = member.get('name') or member.get('pennkey', 'Student')
                
                html_content = self._generate_feedback_reminder_html(
                    match, member_name, match_id
                )
                
                message = Mail(
                    from_email=self.from_email,
                    to_emails=member_email,
                    subject="How did your study group go?",
                    html_content=html_content
                )
                
                response = self.sg.send(message)
                logger.info(f"Sent feedback reminder to {member_email} (status: {response.status_code})")
                
            except Exception as e:
                logger.error(f"Error sending feedback reminder to {member.get('email')}: {e}")
    
    def _generate_group_intro_html(self, group: Dict, member_name: str, member_email: str) -> str:
        """Generate HTML email template for group introduction."""
        members = group.get('members', [])
        course = group.get('course', '')
        suggested_time = group.get('suggested_meeting_time', '')
        group_id = group.get('group_id', '')
        
        # Format time for display
        time_display = suggested_time.replace('_', ' ') if suggested_time else 'TBD'
        
        # List other members
        other_members_html = ''
        for member in members:
            if member.get('email') != member_email:
                name = member.get('name') or member.get('pennkey', '')
                email = member.get('email') or f"{member.get('pennkey')}@upenn.edu"
                other_members_html += f"""
                <li>
                    <strong>{name}</strong> - {email}
                </li>
                """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #01256E; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .group-info {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #01256E; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>GroupMeet</h1>
                    <p>Your Study Group is Ready!</p>
                </div>
                <div class="content">
                    <p>Hi {member_name},</p>
                    <p>Great news! We've matched you with a study group for <strong>{course}</strong>.</p>
                    
                    <div class="group-info">
                        <h3>Your Study Group (Group #{group_id})</h3>
                        <p><strong>Suggested Meeting Time:</strong> {time_display}</p>
                        <h4>Group Members:</h4>
                        <ul>
                            {other_members_html}
                        </ul>
                    </div>
                    
                    <p><strong>Next Steps:</strong></p>
                    <ol>
                        <li>Reach out to your group members to coordinate your first meeting</li>
                        <li>Confirm the meeting time and location</li>
                        <li>Come prepared with study materials</li>
                    </ol>
                    
                    <p>Good luck with your studies!</p>
                </div>
                <div class="footer">
                    <p>GroupMeet - Penn Study Group Matching</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _generate_feedback_reminder_html(self, match: Dict, member_name: str, match_id: str) -> str:
        """Generate HTML email template for feedback reminder."""
        course = match.get('course', '')
        feedback_url = f"https://groupmeet.upenn.edu/feedback?match_id={match_id}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #01256E; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #01256E; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>GroupMeet</h1>
                    <p>How did your study group go?</p>
                </div>
                <div class="content">
                    <p>Hi {member_name},</p>
                    <p>We hope your study group for <strong>{course}</strong> has been helpful!</p>
                    <p>Your feedback helps us improve future matches. Please take a moment to rate your experience:</p>
                    
                    <div style="text-align: center;">
                        <a href="{feedback_url}" class="button">Share Feedback</a>
                    </div>
                    
                    <p>Thank you for using GroupMeet!</p>
                </div>
                <div class="footer">
                    <p>GroupMeet - Penn Study Group Matching</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

