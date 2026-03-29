import sqlite3
from datetime import datetime
import os
import smtplib
from email.message import EmailMessage

def test_worker():
    try:
        conn = sqlite3.connect('users.db', timeout=30)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        now = datetime.now()

        # Get reminders that are due
        cur.execute(
            'SELECT id, user_email, title, message FROM reminder_items WHERE remind_at IS NOT NULL AND remind_at <= ? AND email_sent = 0',
            (now.strftime('%Y-%m-%d %H:%M:%S'),)
        )

        due_reminders = cur.fetchall()
        print(f'Found {len(due_reminders)} due reminders')

        for reminder in due_reminders:
            user_email = reminder['user_email']
            title = reminder['title']
            message = reminder['message'] or ''

            print(f'[TEST] Processing reminder: {title} for {user_email}')

            # Send email
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            smtp_user = os.environ.get('SMTP_USERNAME', 'kimmy.guiriba46@gmail.com')
            smtp_pass = os.environ.get('SMTP_PASSWORD', 'jvuabrvpvkxwknlh')

            if smtp_user and smtp_pass:
                print(f'[TEST EMAIL] Attempting to send to {user_email} with user {smtp_user}')
                subject = f'Reminder: {title}'
                body = f'Hello,\n\n{message if message else "This is your scheduled reminder."}\n\nBest regards,\nMomCare Team'

                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From'] = smtp_user
                msg['To'] = user_email
                msg.set_content(body)

                try:
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
                    server.quit()
                    print(f'[TEST EMAIL] SUCCESS: Sent "{title}" to {user_email}')
                except Exception as e:
                    print(f'[TEST EMAIL ERROR] Failed to send to {user_email}: {e}')
            else:
                print(f'[TEST EMAIL] No credentials configured')

            # Mark as sent
            cur.execute('UPDATE reminder_items SET email_sent = 1 WHERE id = ?', (reminder['id'],))
            conn.commit()

        conn.close()
    except Exception as e:
        print(f'[TEST WORKER ERROR] {e}')

if __name__ == "__main__":
    test_worker()