# Email Notifications & Reminders Setup Guide

## Overview

MomCare now includes a powerful email notification system that allows users to set up automated email reminders for medications, wellness check-ins, appointments, and other important tasks.

## Features

- ✅ Create scheduled email reminders
- ✅ Support for one-time and recurring reminders (daily/weekly)
- ✅ Edit and manage reminders from dashboard
- ✅ Send test emails to verify configuration
- ✅ Automatic email sending via background scheduler
- ✅ Track when reminders were last sent

## Setup Instructions

### 1. Install Dependencies

The email feature uses Python's built-in `smtplib` module (no additional packages needed).

```bash
# Already included in requirements.txt, but ensure you have:
pip install Flask
```

### 2. Configure Email Provider

Choose your email provider and get the SMTP credentials:

#### Option A: Gmail
1. Go to https://myaccount.google.com/apppasswords
2. Create an "App Password" for Mail/Windows Mail
3. Use these credentials:
   - MAIL_SERVER: smtp.gmail.com
   - MAIL_PORT: 587
   - MAIL_USERNAME: your-email@gmail.com
   - MAIL_PASSWORD: your-app-password

#### Option B: Office 365 / Outlook
- MAIL_SERVER: smtp.office365.com
- MAIL_PORT: 587
- MAIL_USERNAME: your-email@outlook.com
- MAIL_PASSWORD: your-password

#### Option C: Custom SMTP Server
- Obtain credentials from your email host

### 3. Set Environment Variables

Create a `.env` file in the project root (or set these in your deployment environment):

```bash
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@momcare.com
MOMCARE_SECRET=your-secret-key-here
```

**On Windows (PowerShell):**
```powershell
$env:MAIL_SERVER = "smtp.gmail.com"
$env:MAIL_PORT = "587"
$env:MAIL_USE_TLS = "True"
$env:MAIL_USERNAME = "your-email@gmail.com"
$env:MAIL_PASSWORD = "your-app-password"
$env:MAIL_DEFAULT_SENDER = "noreply@momcare.com"
```

**On Linux/Mac (Bash):**
```bash
export MAIL_SERVER="smtp.gmail.com"
export MAIL_PORT="587"
export MAIL_USE_TLS="True"
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="your-app-password"
export MAIL_DEFAULT_SENDER="noreply@momcare.com"
```

### 4. Run the Application

Start Flask with the environment variables:

```bash
# With environment configured, run:
python app.py
```

### 5. Access Email Reminders Page

1. Log in to your MomCare account
2. Navigate to **Email Reminders** (or visit `/email-reminders`)
3. Test your configuration by clicking **"Send Test Email"**

## Using Email Reminders

### Creating a Reminder

1. Fill in the form:
   - **Title**: Brief name for the reminder (e.g., "Take Vitamins")
   - **Message**: Detailed message (e.g., "Time to take your daily vitamins")
   - **Scheduled Time**: When to send the email
   - **Repeat**: Select recurring option (Once/Daily/Weekly)

2. Click **"Create Reminder"**

### Managing Reminders

- **Edit**: Click the "Edit" button to update title, message, time, or recurrence
- **Delete**: Click the "Delete" button to remove a reminder
- **Deactivate**: Uncheck "Active" in edit mode to pause without deleting

### Test Email

Before setting up important reminders, verify your email works:
1. Click **"Send Test Email"** button
2. Check your inbox (and spam folder)
3. If you receive the test email, you're good to go!

## Scheduling Background Email Sends

For reminders to be automatically sent at scheduled times, you need to run the background scheduler.

### Option 1: Run Manually

```bash
python send_scheduled_emails.py
```

### Option 2: Schedule with Cron (Linux/Mac)

Edit your crontab:
```bash
crontab -e
```

Add this line to check and send reminders every 5 minutes:
```
*/5 * * * * cd /path/to/MomCare && python send_scheduled_emails.py
```

Every 1 minute:
```
* * * * * cd /path/to/MomCare && python send_scheduled_emails.py
```

### Option 3: Schedule with Task Scheduler (Windows)

1. Open Task Scheduler (Win + R, then `taskschd.msc`)
2. Click "Create Basic Task"
3. Name: "MomCare Email Reminders"
4. Trigger: Set to repeat every 5 minutes
5. Action:
   - Program: `C:\Python\python.exe` (or your Python path)
   - Arguments: `send_scheduled_emails.py`
   - Start in: `C:\path\to\MomCare`

### Option 4: Use APScheduler (Python)

For production deployments, integrate APScheduler into `app.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from send_scheduled_emails import process_reminders

def init_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(process_reminders, 'interval', minutes=5)
    scheduler.start()

if __name__ == '__main__':
    init_scheduler()
    app.run(debug=True)
```

## Database Schema

### email_reminders table

```sql
CREATE TABLE email_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    scheduled_time TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    is_recurring INTEGER DEFAULT 0,
    recurrence_type TEXT,  -- 'once', 'daily', 'weekly'
    last_sent_at TEXT,
    created_at TEXT,
    updated_at TEXT,
    UNIQUE(user_email, title, scheduled_time)
);
```

## API Endpoints

### Get All Reminders
```
GET /api/email-reminders
Response: {"email_reminders": [...]}
```

### Create Reminder
```
POST /api/email-reminders
Body: {
    "title": "Medication",
    "message": "Take your pill",
    "scheduled_time": "2026-03-27T09:00:00",
    "is_recurring": true,
    "recurrence_type": "daily"
}
```

### Update Reminder
```
PUT /api/email-reminders/{id}
Body: {...same as create...}
```

### Delete Reminder
```
DELETE /api/email-reminders/{id}
```

### Send Test Email
```
POST /api/send-test-email
Response: {"success": true, "message": "Test email sent to..."}
```

## Troubleshooting

### "No test email received"

1. **Check spam/junk folder** - SMTP emails sometimes get filtered
2. **Verify credentials** - Test Gmail app password or SMTP credentials separately
3. **Check firewall** - Ensure outbound SMTP (port 587) is allowed
4. **Review logs** - Check console output for error messages

### "Email configuration not set up"

- Ensure environment variables are correctly set
- Verify `MAIL_USERNAME` and `MAIL_PASSWORD` are not empty

### "Reminders not sending automatically"

- Ensure `send_scheduled_emails.py` is running
- Check scheduler logs for errors
- Verify reminders are marked `is_active = 1` in database

### Gmail "Less secure app" error

- Use App Passwords instead (recommended)
- Or enable "Less secure app access" (not recommended)
- Avoid using 2FA passwords directly

## Security Considerations

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use app-specific passwords** - For Gmail, create app passwords instead of using main password
3. **HTTPS only** - In production, only serve over HTTPS
4. **Limit endpoint access** - Email reminders require authentication
5. **Validate inputs** - All user inputs are validated on server-side

## Example Use Cases

### Medication Reminders
- Title: "Morning Vitamins"
- Message: "Time to take your daily vitamin supplements"
- Scheduled: 8:00 AM daily

### Wellness Check-ins
- Title: "Daily Wellness Check"
- Message: "How are you feeling today? Check your mood and wellness in MomCare"
- Scheduled: 8:00 PM daily

### Appointment Reminders
- Title: "Doctor Appointment"
- Message: "Your appointment with Dr. Smith is tomorrow at 2:00 PM"
- Scheduled: 24 hours before appointment

### Hydration Reminder
- Title: "Drink Water"
- Message: "Remember to stay hydrated! Drink a glass of water"
- Scheduled: 10:00 AM, 1:00 PM, 4:00 PM daily

## Future Enhancements

- SMS notifications (Twilio integration)
- Push notifications (mobile app)
- Email template customization
- Reminder acknowledgment tracking
- Smart retry logic for failed sends
- Timezone-aware scheduling
- Analytics dashboard

## Support

For issues or questions:
1. Check the logs in console output
2. Review this guide
3. Check environment variable configuration
4. Verify email provider credentials

---

**Last Updated**: March 2026
