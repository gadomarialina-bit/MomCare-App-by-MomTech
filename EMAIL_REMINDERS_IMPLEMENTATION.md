# MomCare Email Notifications & Reminders - Implementation Summary

## What Was Added

### ✅ Core Features Implemented

1. **Email Reminder Management System**
   - Create, update, delete, and manage email reminders
   - Support for one-time and recurring reminders (daily, weekly)
   - Track when reminders were last sent
   - Enable/disable reminders without deleting

2. **Database Integration**
   - New `email_reminders` table with all necessary fields
   - Tracks: title, message, scheduled time, recurrence, active status, send history

3. **REST API Endpoints**
   - `GET /api/email-reminders` - Get all reminders for user
   - `POST /api/email-reminders` - Create new reminder
   - `GET /api/email-reminders/<id>` - Get specific reminder
   - `PUT /api/email-reminders/<id>` - Update reminder
   - `DELETE /api/email-reminders/<id>` - Delete reminder
   - `POST /api/send-test-email` - Send test email to verify configuration

4. **User Interface**
   - New page: `/email-reminders` with full reminder management UI
   - Create reminder form with all options
   - List view showing all reminders with status
   - Edit modal for updating existing reminders
   - Delete functionality with confirmation
   - Test email button to verify SMTP configuration
   - Informational sidebar with tips and best practices
   - Added Email Reminders link to main navigation menu

5. **Email Sending**
   - Built-in SMTP client using Python's `smtplib`
   - Configurable via environment variables
   - Support for TLS/SSL connections
   - HTML and plain text email templates
   - Graceful error handling

6. **Background Scheduler**
   - Standalone script: `send_scheduled_emails.py`
   - Automatically checks for pending reminders
   - Sends emails at scheduled times
   - Handles recurring reminders (reschedules for next occurrence)
   - Marks one-time reminders as inactive after sending
   - Can be run via cron, Windows Task Scheduler, or APScheduler

7. **Configuration**
   - Email provider settings via environment variables
   - Support for Gmail, Office 365, and custom SMTP servers
   - Secure credential management

### 📁 Files Modified/Created

**New Files:**
- `templates/email_reminders.html` - Complete UI for reminder management
- `send_scheduled_emails.py` - Background scheduler script
- `EMAIL_REMINDERS_SETUP.md` - Comprehensive setup and usage guide

**Modified Files:**
- `app.py` - Added database table, email functions, and API routes
- `templates/navbar.html` - Added link to Email Reminders page

### 🔧 Code Changes Detail

#### In `app.py`:

1. **Imports** (lines 1-12):
   - Added `smtplib` and email MIME modules for SMTP functionality

2. **Email Configuration** (lines 26-32):
   - `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`
   - `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`
   - All configurable via environment variables

3. **Email Sending Function** (lines 51-83):
   - `send_email(to_email, subject, body, html_body)` 
   - Handles SMTP connection, authentication, and message sending
   - Returns boolean success/failure status

4. **Database Table** (lines 315-334):
   - `email_reminders` table in `init_db()` function
   - Fields: id, user_email, title, message, scheduled_time, is_active, is_recurring, recurrence_type, last_sent_at, created_at, updated_at

5. **API Routes** (new):
   - `@app.route('/api/email-reminders', methods=['GET', 'POST'])` - List and create reminders
   - `@app.route('/api/email-reminders/<id>', methods=['GET', 'PUT', 'DELETE'])` - CRUD individual reminders
   - `@app.route('/email-reminders')` - HTML page for management
   - `@app.route('/api/send-test-email', methods=['POST'])` - Test SMTP configuration

## How to Set Up

### 1. Configure Email Provider
Choose Gmail, Outlook, or custom SMTP:

**Gmail Example:**
```bash
export MAIL_SERVER="smtp.gmail.com"
export MAIL_PORT="587"
export MAIL_USE_TLS="True"
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="your-app-password"
export MAIL_DEFAULT_SENDER="noreply@momcare.com"
```

### 2. Set Environment Variables
Create `.env` file or use system environment variables.

### 3. Verify Installation
- Start Flask: `python app.py`
- Navigate to `http://localhost:5000/email-reminders`
- Log in and click "Send Test Email"
- Check inbox for test message

### 4. Enable Automatic Sending
Run scheduler (choose one method):

**Cron (Linux/Mac):**
```bash
*/5 * * * * cd /path/to/MomCare && python send_scheduled_emails.py
```

**Windows Task Scheduler:**
- Create task to run `python send_scheduled_emails.py` every 5 minutes

**Python APScheduler** (integrated):
- Already included in setup documentation

## Usage Examples

### Create Medication Reminder
- **Title**: "Morning Medication"
- **Message**: "Time to take your morning medications"
- **Time**: 8:00 AM
- **Repeat**: Daily

### Create Wellness Check-in
- **Title**: "Evening Wellness Check"
- **Message**: "How are you feeling? Update your mood and wellness in MomCare"
- **Time**: 8:00 PM
- **Repeat**: Daily

### Create Appointment Reminder
- **Title**: "Doctor Appointment Tomorrow"
- **Message**: "You have an appointment with Dr. Smith tomorrow at 2:00 PM"
- **Time**: 1:00 PM (day before)
- **Repeat**: Once

## Security Features

✅ User authentication required (session-based)
✅ Each user only sees their own reminders
✅ Input validation on all endpoints
✅ SQL injection protection via parameterized queries
✅ HTTPS recommended for production
✅ Environment variables for sensitive credentials
✅ No password or credential logs

## Testing

### Manual Testing
1. Create a test reminder for 1 minute from now
2. Click "Send Test Email" to verify SMTP works
3. Run `python send_scheduled_emails.py` manually
4. Check for email in inbox/spam

### Automated Testing
Add to test suite:
```python
def test_create_email_reminder():
    response = client.post('/api/email-reminders', json={
        'title': 'Test',
        'message': 'Test reminder',
        'scheduled_time': '2026-03-27T10:00:00',
        'is_recurring': False
    })
    assert response.status_code == 201
```

## Performance Considerations

- Background scheduler runs independently
- No performance impact on main Flask app
- Database queries indexed on `(user_email, scheduled_time)`
- Email sending is non-blocking (scheduler runs separately)
- Can handle thousands of reminders per user

## Future Enhancements

1. **SMS Notifications** - Integrate Twilio for SMS reminders
2. **Push Notifications** - Mobile app push notifications
3. **Email Templates** - Customizable email templates
4. **Timezone Support** - Schedule based on user timezone
5. **Delivery Confirmation** - Track email delivery status
6. **Retry Logic** - Automatic retries for failed sends
7. **Reminder Analytics** - Track completion rates
8. **Smart Reminders** - AI-powered reminder suggestions

## Troubleshooting

### Issue: Test email not received
**Solution**: 
- Check spam/junk folder
- Verify SMTP credentials (especially Gmail app password)
- Ensure MAIL_USERNAME and MAIL_PASSWORD are set
- Check firewall allows outbound SMTP (port 587)

### Issue: Reminders not sending automatically
**Solution**:
- Verify `send_scheduled_emails.py` is running
- Check system logs for errors
- Ensure reminders are marked `is_active = 1`
- Verify scheduled_time is formatted correctly

### Issue: "Not authenticated" error on API
**Solution**:
- Ensure user is logged in (session active)
- Check browser cookies for session ID
- Try logging out and logging back in

## Documentation

See `EMAIL_REMINDERS_SETUP.md` for:
- Detailed setup instructions for each email provider
- Cron/Task Scheduler configuration
- Complete API documentation
- Troubleshooting guide
- Security best practices

## Support & Questions

For issues:
1. Check `EMAIL_REMINDERS_SETUP.md` troubleshooting section
2. Review console logs for error messages
3. Verify environment variables are set correctly
4. Test SMTP settings independently

---

**Implementation Date**: March 27, 2026
**Status**: ✅ Complete and Ready for Use
**Version**: 1.0.0
