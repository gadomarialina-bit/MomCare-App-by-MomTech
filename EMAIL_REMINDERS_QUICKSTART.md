# Email Reminders - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Set Environment Variables (2 min)

**For Gmail:**
```powershell
# PowerShell (Windows)
$env:MAIL_SERVER = "smtp.gmail.com"
$env:MAIL_PORT = "587"
$env:MAIL_USE_TLS = "True"
$env:MAIL_USERNAME = "your-email@gmail.com"
$env:MAIL_PASSWORD = "your-app-password"
$env:MAIL_DEFAULT_SENDER = "noreply@momcare.com"
```

> **Note**: For Gmail, go to https://myaccount.google.com/apppasswords and create an App Password (not your regular password).

### Step 2: Start the App (1 min)

```bash
python app.py
```

### Step 3: Test It (2 min)

1. Go to http://localhost:5000 and log in
2. Click **Email Reminders** in the menu
3. Click **Send Test Email** button
4. Check your inbox (or spam folder)

### Step 4: Create a Reminder (Optional)

Fill in:
- **Title**: "Test Reminder"
- **Message**: "This is my first email reminder!"
- **Time**: Set to 5 minutes from now
- Click **Create Reminder**

## 🔄 Enable Automatic Sending

For reminders to be sent automatically at scheduled times:

### Option A: Run Manually (Testing)
```bash
python send_scheduled_emails.py
```

### Option B: Automate with Cron (Linux/Mac)
```bash
crontab -e
# Add this line to check every 5 minutes:
*/5 * * * * cd /path/to/MomCare && python send_scheduled_emails.py
```

### Option C: Automate with Task Scheduler (Windows)
1. Open Task Scheduler
2. Create Basic Task
3. Set to run every 5 minutes
4. Command: `python send_scheduled_emails.py`
5. Working directory: Your MomCare folder

## ✨ Features

✅ Create one-time reminders
✅ Create daily/weekly recurring reminders
✅ Edit reminders anytime
✅ Delete reminders
✅ Send test emails
✅ Track when reminders were last sent
✅ Enable/disable without deleting

## 🎯 Common Use Cases

### Daily Medication Reminder
```
Title: Take Medication
Message: Time to take your daily medications
Time: 8:00 AM
Repeat: Daily
```

### Evening Wellness Check
```
Title: How are you feeling?
Message: Update your mood and wellness in MomCare
Time: 8:00 PM
Repeat: Daily
```

### Appointment Reminder (24 hours before)
```
Title: Doctor Appointment Tomorrow
Message: You have an appointment at 2:00 PM
Time: [24 hours before appointment]
Repeat: Once
```

## 🔍 Troubleshooting

### Test Email Not Received?
1. ✓ Check spam/junk folder first
2. ✓ Verify Gmail app password (if using Gmail)
3. ✓ Make sure all environment variables are set
4. ✓ Run: `python send_scheduled_emails.py` manually to see errors

### Reminders Not Sending?
1. ✓ Is the scheduler running? (`python send_scheduled_emails.py`)
2. ✓ Is the reminder marked as Active?
3. ✓ Is scheduled time in the past?

### Can't See Email Reminders Page?
1. ✓ Make sure you're logged in
2. ✓ Try refreshing the page
3. ✓ Check browser console for errors (F12)

## 📖 For More Details

See `EMAIL_REMINDERS_SETUP.md` for:
- Detailed setup for each email provider
- Complete API documentation
- Troubleshooting guide
- Security information

## 🚀 That's It!

You now have working email reminders in MomCare!

---

**Need help?** Check the logs when running `send_scheduled_emails.py` for detailed error messages.
