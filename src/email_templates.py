"""
Email Template Generator Module
Generates email templates for manager notifications about flagged users
"""

from datetime import datetime
import pandas as pd


def generate_manager_notification(user_name: str, user_email: str, risk_category: str, 
                                   last_login_days: int, access_level: str, 
                                   manager_name: str = "Manager") -> str:
    """Generate an email template for notifying a manager about a flagged user."""
    
    today = datetime.now().strftime("%B %d, %Y")
    
    template = f"""Subject: Action Required: Review Access for {user_name}

Dear {manager_name},

This is an automated notification from the Google Workspace Cleanup Planner regarding a user account that requires your review.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USER DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Name: {user_name}
• Email: {user_email}
• Current Access Level: {access_level}
• Last Login: {last_login_days} days ago
• Risk Category: {risk_category}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTION REQUESTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please review this user's access and confirm one of the following:

[ ] KEEP ACCESS - User still requires current access level
[ ] REDUCE ACCESS - User should have reduced permissions
[ ] REMOVE ACCESS - User no longer needs access
[ ] TRANSFER OWNERSHIP - Transfer files to another user before removal

Please respond to this email with your decision by [INSERT DEADLINE].

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This notification was generated on {today}.
For questions, please contact your IT administrator.

Best regards,
IT Security Team
"""
    return template


def generate_review_reminder(user_count: int, deadline: str = "end of this week") -> str:
    """Generate a reminder email for pending reviews."""
    
    template = f"""Subject: Reminder: {user_count} User Access Reviews Pending

Dear Team,

This is a friendly reminder that you have {user_count} user access review(s) pending.

Please complete your reviews by {deadline} to ensure compliance with our security policies.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUICK ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Log in to the Workspace Cleanup Planner
2. Review flagged users in the "AI Cleanup Plan" tab
3. Make your decisions and export the results
4. Forward approved changes to IT for implementation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for helping keep our workspace secure!

Best regards,
IT Security Team
"""
    return template


def generate_bulk_notification(df: pd.DataFrame, manager_name: str = "Manager") -> str:
    """Generate a bulk email for multiple flagged users."""
    
    today = datetime.now().strftime("%B %d, %Y")
    user_count = len(df)
    
    # Build user table
    user_rows = []
    for _, row in df.iterrows():
        name = row.get('Name', 'Unknown')
        email = row.get('Email', 'N/A')
        risk = row.get('RiskCategory', 'Unknown')
        days = row.get('LastLoginDays', 'N/A')
        user_rows.append(f"• {name} ({email}) - {risk} - Last login: {days} days ago")
    
    users_list = "\n".join(user_rows)
    
    template = f"""Subject: Action Required: {user_count} Users Need Access Review

Dear {manager_name},

The Google Workspace Cleanup Planner has identified {user_count} user(s) that require your review.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USERS REQUIRING REVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{users_list}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Review each user's current access requirements
2. Determine if access should be kept, reduced, or removed
3. Reply to this email with your decisions
4. IT will implement approved changes

Please respond by [INSERT DEADLINE].

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generated on {today}
For questions, contact your IT administrator.

Best regards,
IT Security Team
"""
    return template


def get_template_options() -> list:
    """Return list of available template types."""
    return [
        "Individual Manager Notification",
        "Bulk Manager Notification", 
        "Review Reminder"
    ]
