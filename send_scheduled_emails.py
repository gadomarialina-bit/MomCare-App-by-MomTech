#!/usr/bin/env python3
"""
Email Reminder Scheduler
This script checks for pending email reminders and sends them.
Run this periodically (e.g., via cron: */5 * * * * python send_scheduled_emails.py)
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add parent directory to path to import from app
sys.path.insert(0, str(Path(__file__).parent))

DB_PATH = Path(__file__).parent / 'users.db'

# Email configuration from environment
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@momcare.com')


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def send_email(to_email, subject, body, html_body=None):
    """Send email using SMTP."""
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print(f"Email not configured. Would send to {to_email}: {subject}")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = MAIL_DEFAULT_SENDER
        msg['To'] = to_email
        
        msg.attach(MIMEText(body, 'plain'))
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            if MAIL_USE_TLS:
                server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✓ Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        print(f"✗ Error sending email to {to_email}: {str(e)}")
        return False


def get_pending_reminders():
    """Get reminders that are due to be sent."""
    conn = get_db()
    cur = conn.cursor()
    
    now = datetime.utcnow()
    
    try:
        # Get active reminders where scheduled_time is in the past
        cur.execute('''
            SELECT id, user_email, title, message, scheduled_time, 
                   is_recurring, recurrence_type
            FROM email_reminders 
            WHERE is_active = 1 
            AND datetime(scheduled_time) <= datetime(?)
            ORDER BY scheduled_time ASC
        ''', (now.isoformat(),))
        
        reminders = [dict(row) for row in cur.fetchall()]
        conn.close()
        return reminders
    except Exception as e:
        print(f"Error querying reminders: {e}")
        conn.close()
        return []


def update_reminder_sent(reminder_id, next_scheduled_time=None):
    """Update reminder after sending."""
    conn = get_db()
    cur = conn.cursor()
    
    try:
        now = datetime.utcnow().isoformat()
        
        if next_scheduled_time:
            # Recurring reminder: update scheduled_time
            cur.execute('''
                UPDATE email_reminders 
                SET last_sent_at = ?, scheduled_time = ?
                WHERE id = ?
            ''', (now, next_scheduled_time, reminder_id))
        else:
            # One-time reminder: mark as inactive
            cur.execute('''
                UPDATE email_reminders 
                SET last_sent_at = ?, is_active = 0
                WHERE id = ?
            ''', (now, reminder_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating reminder {reminder_id}: {e}")
        conn.close()
        return False


def calculate_next_send_time(scheduled_time_str, recurrence_type):
    """Calculate next send time for recurring reminders."""
    try:
        current = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
        
        if recurrence_type == 'daily':
            return (current + timedelta(days=1)).isoformat()
        elif recurrence_type == 'weekly':
            return (current + timedelta(weeks=1)).isoformat()
        else:
            return None
    except Exception as e:
        print(f"Error calculating next send time: {e}")
        return None


def send_reminder_email(reminder):
    """Send email for a reminder."""
    user_email = reminder['user_email']
    title = reminder['title']
    message = reminder['message']
    
    subject = f"MomCare Reminder: {title}"
    body = f"{message}\n\n---\nMomCare - Your Personal Wellness Assistant"
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #007bff;">MomCare Reminder</h2>
                <h3>{title}</h3>
                <p style="font-size: 16px; line-height: 1.6;">
                    {message}
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #999; font-size: 12px;">
                    MomCare - Your Personal Wellness Assistant
                </p>
            </div>
        </body>
    </html>
    """
    
    return send_email(user_email, subject, body, html_body)


def process_reminders():
    """Main function to process pending reminders."""
    print(f"\n[{datetime.utcnow().isoformat()}] Starting email reminder processor...")
    
    reminders = get_pending_reminders()
    
    if not reminders:
        print("No pending reminders to send.")
        return
    
    print(f"Found {len(reminders)} pending reminder(s)")
    
    sent_count = 0
    failed_count = 0
    
    for reminder in reminders:
        print(f"\nProcessing reminder: {reminder['id']} - {reminder['title']}")
        
        # Send the email
        if send_reminder_email(reminder):
            sent_count += 1
            
            # Update reminder
            next_time = None
            if reminder['is_recurring']:
                next_time = calculate_next_send_time(
                    reminder['scheduled_time'],
                    reminder['recurrence_type']
                )
            
            update_reminder_sent(reminder['id'], next_time)
            
            if next_time:
                print(f"  Recurring reminder rescheduled for: {next_time}")
            else:
                print(f"  One-time reminder completed (marked as inactive)")
        else:
            failed_count += 1
            print(f"  Failed to send email")
    
    print(f"\n[{datetime.utcnow().isoformat()}] Finished!")
    print(f"Summary: {sent_count} sent, {failed_count} failed")


if __name__ == '__main__':
    process_reminders()
