from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import json
from pathlib import Path
import sqlite3
from sqlite3 import Connection
import os
from datetime import datetime




app = Flask(__name__)
app.secret_key = os.environ.get('MOMCARE_SECRET', 'change-this-secret-for-production')

DB_PATH = Path(__file__).parent / 'users.db'

def get_db() -> Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('PRAGMA synchronous=NORMAL;')
        conn.execute('PRAGMA foreign_keys=ON;')
    except Exception:
        pass
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    # ... your CREATE TABLE statements ...
    conn.commit()
    conn.close()
    
# Ensure DB schema exists on startup
try:
    init_db()
except Exception as _:
    # don't prevent app from starting if init has issues; log to console
    print('Warning: init_db() failed to run during startup')




DB_PATH = Path(__file__).parent / 'users.db'




def get_db() -> Connection:
   # Create a short-lived connection with a higher timeout and pragmatic settings
   # to reduce "database is locked" errors under concurrent access.
   conn = sqlite3.connect(DB_PATH, timeout=30)
   conn.row_factory = sqlite3.Row
   try:
       # Enable WAL mode for better concurrency (writers don't block readers)
       conn.execute('PRAGMA journal_mode=WAL;')
       # Moderate synchronous to improve performance while WAL is active
       conn.execute('PRAGMA synchronous=NORMAL;')
       # Enable foreign keys if used
       conn.execute('PRAGMA foreign_keys=ON;')
   except Exception:
       # best-effort; don't fail if PRAGMA isn't supported
       pass
   return conn




def init_db():
   """Create users table if it doesn't exist, and migrate from users.json if present."""
   conn = get_db()
   cur = conn.cursor()
   cur.execute(
       """
       CREATE TABLE IF NOT EXISTS users (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           first TEXT NOT NULL,
           last TEXT NOT NULL,
           email TEXT NOT NULL UNIQUE,
           birthdate TEXT,
           password_hash TEXT NOT NULL,
           security_question TEXT,
           security_answer TEXT
       )
       """
   )
   # Ensure older DBs have the expected security columns
   try:
       cur.execute("PRAGMA table_info(users)")
       user_cols = [r[1] for r in cur.fetchall()]
       if 'security_question' not in user_cols:
           try:
               cur.execute("ALTER TABLE users ADD COLUMN security_question TEXT")
           except Exception:
               pass
       if 'security_answer' not in user_cols:
           try:
               cur.execute("ALTER TABLE users ADD COLUMN security_answer TEXT")
           except Exception:
               pass
   except Exception:
       # best-effort, proceed without failing init
       pass
  
   # Create monthly_budgets table
   cur.execute(
       """
       CREATE TABLE IF NOT EXISTS monthly_budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            month_iso TEXT NOT NULL,
            income REAL DEFAULT 0,
            budget_limit REAL DEFAULT 0,
            month INTEGER,
            year INTEGER,
            created_at TEXT,
            UNIQUE(user_email, month_iso)
       )
       """
   )


   # Create expenses table
   cur.execute(
       """
       CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            title TEXT NOT NULL,
            start_time REAL,
            duration REAL,
            color TEXT,
            is_priority INTEGER DEFAULT 0,
            task_date TEXT,
            completed INTEGER DEFAULT 0,
            created_at TEXT
       )
       """
   )


   # Create grocery_items table
   cur.execute(
       """
        CREATE TABLE IF NOT EXISTS grocery_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            estimated_cost REAL,
            category TEXT,
            is_checked INTEGER DEFAULT 0,
            month_iso TEXT,
            month INTEGER,
            year INTEGER,
            created_at TEXT
       )
       """
   )

   # Create reminders table (one per user)
   cur.execute(
       """
       CREATE TABLE IF NOT EXISTS reminders (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           user_email TEXT NOT NULL UNIQUE,
           message TEXT,
           created_at TEXT,
           updated_at TEXT
       )
       """
   )
   # Create reminder_items table for multiple scheduled reminders
   cur.execute(
       """
       CREATE TABLE IF NOT EXISTS reminder_items (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           user_email TEXT NOT NULL,
           title TEXT,
           message TEXT,
           remind_at TEXT,
           is_recurring INTEGER DEFAULT 0,
           recurrence_rule TEXT,
           created_at TEXT,
           updated_at TEXT
       )
       """
   )
   # Migration: detect older schema variations and migrate data if necessary
   cur.execute("PRAGMA table_info(grocery_items)")
   cols = [r[1] for r in cur.fetchall()]
   # If the DB has an old schema (item, qty, cost, month_str, purchased), rebuild table
   old_style = set(["item", "qty", "cost", "month_str", "purchased"]).issubset(set(cols))
   # If only month_iso is missing but month_str exists, add month_iso and copy values
   if "month_iso" not in cols and "month_str" in cols and not old_style:
       try:
           cur.execute("ALTER TABLE grocery_items ADD COLUMN month_iso TEXT")
           cur.execute("UPDATE grocery_items SET month_iso = month_str WHERE month_str IS NOT NULL")
       except Exception:
           # ignore; best-effort migration
           pass


   if old_style:
       # Create new table with the desired schema
       cur.execute(
           """
           CREATE TABLE IF NOT EXISTS grocery_items_new (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               user_email TEXT NOT NULL,
               item_name TEXT NOT NULL,
               quantity INTEGER DEFAULT 1,
               estimated_cost REAL,
               category TEXT,
               is_checked INTEGER DEFAULT 0,
               month_iso TEXT,
               year INTEGER,
               created_at TEXT
           )
           """
       )
       # Copy and map old columns to new columns
       try:
           cur.execute(
               "INSERT INTO grocery_items_new (id, user_email, item_name, quantity, estimated_cost, category, is_checked, month_iso, created_at) "
               "SELECT id, user_email, item AS item_name, qty AS quantity, cost AS estimated_cost, category, purchased AS is_checked, month_str AS month_iso, NULL FROM grocery_items"
           )
           cur.execute("DROP TABLE grocery_items")
           cur.execute("ALTER TABLE grocery_items_new RENAME TO grocery_items")
       except Exception:
           # If migration fails, ignore to avoid crashing init; developer should inspect DB
           pass
   conn.commit()






   # Migrate existing users from users.json if present
   data_file = Path(__file__).parent / 'users.json'
   if data_file.exists():
       try:
           with open(data_file, 'r', encoding='utf-8') as f:
               users = json.load(f)
       except Exception:
           users = []


       if users:
           for u in users:
               try:
                   cur.execute(
                       "INSERT OR IGNORE INTO users (first, last, email, birthdate, password_hash) VALUES (?, ?, ?, ?, ?)",
                       (u.get('first'), u.get('last'), u.get('email'), u.get('birthdate'), u.get('password_hash')),
                   )
               except Exception:
                   # ignore individual insert errors
                   pass
           conn.commit()
           # rename migrated file to keep a backup
           try:
               data_file.rename(data_file.with_suffix('.json.bak'))
           except Exception:
               pass


   conn.close()




@app.route('/')
def index():
   return render_template('index.html')




@app.route('/signup', methods=['GET', 'POST'])
def signup():
   if request.method == 'POST':
       first = request.form.get('first', '').strip()
       last = request.form.get('last', '').strip()
       email = request.form.get('email', '').strip().lower()
       password = request.form.get('password', '')
       confirm = request.form.get('confirm', '')
       day = request.form.get('day', '')
       month = request.form.get('month', '')
       year = request.form.get('year', '')


       # Basic validation
       if not first or not last or not email or not password:
           flash('Please fill in all required fields.')
           return redirect(url_for('signup'))


       if password != confirm:
           flash('Passwords do not match.')
           return redirect(url_for('signup'))


       conn = get_db()
       cur = conn.cursor()
       cur.execute("SELECT id FROM users WHERE email = ?", (email,))
       if cur.fetchone():
           conn.close()
           flash('An account with that email already exists.')
           return redirect(url_for('signup'))


       password_hash = generate_password_hash(password)
       birthdate = f"{day}-{month}-{year}"
       security_question = request.form.get('security_question', '').strip()
       security_answer = request.form.get('security_answer', '').strip().lower()


       if not security_question or not security_answer:
           flash('Please select and answer a security question.')
           return redirect(url_for('signup'))


       try:
           # Hash the security answer before storing it
           security_answer_hash = generate_password_hash(security_answer)
           cur.execute(
               "INSERT INTO users (first, last, email, birthdate, password_hash, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?, ?)",
               (first, last, email, birthdate, password_hash, security_question, security_answer_hash),
           )
           conn.commit()
       except Exception as e:
           print(e)
           flash('Unable to create account. Please try again.')
           conn.close()
           return redirect(url_for('signup'))
       conn.close()


       # Get the new user's ID
       try:
           conn = get_db()  # Reconnect to get ID
           cur = conn.cursor()
           cur.execute("SELECT id FROM users WHERE email = ?", (email,))
           user_row = cur.fetchone()
           user_id = user_row['id']
           conn.close()
          
           session['user_id'] = user_id
           session['user_email'] = email
           session['user_first'] = first
           flash('Account created successfully!')
           return redirect(url_for('dashboard'))
       except Exception as e:
           print(f"Error setting session: {e}")
           flash('Account created, but please log in.')
           return redirect(url_for('index'))


   return render_template('signup.html')




@app.route('/login', methods=['POST'])
def login():
   email = request.form.get('email', '').strip().lower()
   password = request.form.get('password', '')


   if not email or not password:
       flash('Please provide both email and password.')
       return redirect(url_for('index'))


   conn = get_db()
   cur = conn.cursor()
   cur.execute('SELECT id, first, password_hash FROM users WHERE email = ?', (email,))
   row = cur.fetchone()
   conn.close()


   if not row:
       flash('Invalid email or password.')
       return redirect(url_for('index'))


   user_id = row['id']
   first = row['first']
   password_hash = row['password_hash']


   if not check_password_hash(password_hash, password):
       flash('Invalid email or password.')
       return redirect(url_for('index'))


   session['user_id'] = user_id
   session['user_email'] = email
   session['user_first'] = first
   return redirect(url_for('dashboard'))






@app.route('/forgot-password-qa', methods=['GET', 'POST'])
def forgot_password_qa():
   """Forgot password via security question - username lookup."""
   if request.method == 'POST':
       username = request.form.get('username', '').strip()
      
       if not username:
           flash('Please enter your first name.')
           return redirect(url_for('forgot_password_qa'))
      
       conn = get_db()
       cur = conn.cursor()
       cur.execute('SELECT email, security_question FROM users WHERE first = ?', (username,))
       row = cur.fetchone()
       conn.close()
      
       if not row:
           flash('Username not found.')
           return redirect(url_for('forgot_password_qa'))
      
       email = row['email']
       security_question = row['security_question']
      
       return render_template('forgot_qa.html', email=email, security_question=security_question)
  
   return render_template('forgot_qa_firstname.html')


@app.route('/api/reminder', methods=['GET', 'PUT'])
def api_reminder():
   # Require logged-in user
   user_email = session.get('user_email')
   if not user_email:
       return jsonify({'error': 'Not authenticated'}), 401

   conn = get_db()
   cur = conn.cursor()
   if request.method == 'GET':
       cur.execute('SELECT message, updated_at FROM reminders WHERE user_email = ?', (user_email,))
       row = cur.fetchone()
       conn.close()
       if not row:
           return jsonify({'message': ''})
       return jsonify({'message': row['message'] or '', 'updated_at': row['updated_at']})

   # PUT -> update or create
   data = request.get_json() or {}
   message = data.get('message', '')
   now = datetime.utcnow().isoformat()

   try:
       # Try updating existing
       cur.execute('UPDATE reminders SET message = ?, updated_at = ? WHERE user_email = ?', (message, now, user_email))
       if cur.rowcount == 0:
           cur.execute('INSERT INTO reminders (user_email, message, created_at, updated_at) VALUES (?, ?, ?, ?)', (user_email, message, now, now))
       conn.commit()
   except Exception as e:
       conn.rollback()
       conn.close()
       return jsonify({'error': 'Unable to save reminder'}), 500

   conn.close()
   return jsonify({'message': message, 'updated_at': now})


@app.route('/api/reminders', methods=['GET', 'POST'])
def api_reminders():
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = get_db()
    cur = conn.cursor()
    if request.method == 'GET':
        cur.execute('SELECT id, title, message, remind_at, is_recurring, recurrence_rule, created_at, updated_at FROM reminder_items WHERE user_email = ? ORDER BY remind_at IS NULL, remind_at', (user_email,))
        rows = cur.fetchall()
        reminders = [dict(r) for r in rows]
        conn.close()
        return jsonify({'reminders': reminders})

    # POST -> create new reminder item
    data = request.get_json() or {}
    title = data.get('title', '')
    message = data.get('message', '')
    remind_at = data.get('remind_at')
    is_recurring = 1 if data.get('is_recurring') else 0
    recurrence_rule = data.get('recurrence_rule')
    now = datetime.utcnow().isoformat()
    try:
        cur.execute('INSERT INTO reminder_items (user_email, title, message, remind_at, is_recurring, recurrence_rule, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (user_email, title, message, remind_at, is_recurring, recurrence_rule, now, now))
        conn.commit()
        new_id = cur.lastrowid
        cur.execute('SELECT id, title, message, remind_at, is_recurring, recurrence_rule, created_at, updated_at FROM reminder_items WHERE id = ?', (new_id,))
        row = cur.fetchone()
        conn.close()
        return jsonify(dict(row)), 201
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': 'Unable to create reminder item'}), 500


@app.route('/api/reminders/<int:item_id>', methods=['PUT', 'DELETE'])
def api_reminder_item(item_id):
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = get_db()
    cur = conn.cursor()
    if request.method == 'DELETE':
        cur.execute('DELETE FROM reminder_items WHERE id = ? AND user_email = ?', (item_id, user_email))
        conn.commit()
        conn.close()
        return jsonify({'deleted': True})

    # PUT -> update
    data = request.get_json() or {}
    title = data.get('title', '')
    message = data.get('message', '')
    remind_at = data.get('remind_at')
    is_recurring = 1 if data.get('is_recurring') else 0
    recurrence_rule = data.get('recurrence_rule')
    now = datetime.utcnow().isoformat()
    try:
        cur.execute('UPDATE reminder_items SET title = ?, message = ?, remind_at = ?, is_recurring = ?, recurrence_rule = ?, updated_at = ? WHERE id = ? AND user_email = ?',
                    (title, message, remind_at, is_recurring, recurrence_rule, now, item_id, user_email))
        if cur.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Not found'}), 404
        conn.commit()
        cur.execute('SELECT id, title, message, remind_at, is_recurring, recurrence_rule, created_at, updated_at FROM reminder_items WHERE id = ?', (item_id,))
        row = cur.fetchone()
        conn.close()
        return jsonify(dict(row))
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': 'Unable to update reminder item'}), 500




@app.route('/verify-security-answer', methods=['POST'])
def verify_security_answer():
   """Verify security answer and reset password."""
   email = request.form.get('email', '').strip().lower()
   security_answer = request.form.get('security_answer', '').strip().lower()
   new_password = request.form.get('new_password', '')
   confirm_password = request.form.get('confirm_password', '')
  
   if not email or not security_answer or not new_password:
       flash('Please fill in all fields.')
       return redirect(url_for('forgot_password_qa'))
  
   if new_password != confirm_password:
       flash('Passwords do not match.')
       return redirect(url_for('forgot_password_qa'))
  
   conn = get_db()
   cur = conn.cursor()
   cur.execute('SELECT security_answer FROM users WHERE email = ?', (email,))
   row = cur.fetchone()
   conn.close()
  
   if not row:
       flash('User not found.')
       return redirect(url_for('forgot_password_qa'))
  
   stored_answer_hash = row['security_answer']
  
   # Verify the security answer
   if not check_password_hash(stored_answer_hash, security_answer):
       flash('Incorrect security answer.')
       return redirect(url_for('forgot_password_qa'))
  
   # Update password
   new_password_hash = generate_password_hash(new_password)
   conn = get_db()
   cur = conn.cursor()
   cur.execute('UPDATE users SET password_hash = ? WHERE email = ?', (new_password_hash, email))
   conn.commit()
   conn.close()
  
   flash('Password reset successfully! Please log in with your new password.')
   return redirect(url_for('index'))










@app.route('/dashboard')
def dashboard():
   first = session.get('user_first')
   today = datetime.now().strftime('%B %d, %Y')
   user_email = session.get('user_email')
  
   tasks = []
   budget_limit = 0
   total_spent = 0
   top_expense_category = "None"
  
   # Handle month selection
   selected_month_iso = request.args.get('month')
   selected_month = None
  
   if selected_month_iso:
       try:
           # Parse YYYY-MM
           date_obj = datetime.strptime(selected_month_iso, '%Y-%m')
           selected_month = date_obj.strftime('%B %Y')
       except ValueError:
           # Fallback if invalid format
           selected_month_iso = datetime.now().strftime('%Y-%m')
           selected_month = datetime.now().strftime('%B %Y')
   else:
       # Default to current month
       selected_month_iso = datetime.now().strftime('%Y-%m')
       selected_month = datetime.now().strftime('%B %Y')


   if user_email:
       conn = get_db()
       cur = conn.cursor()
      
       # Load upcoming tasks (limit 10)
       cur.execute('SELECT * FROM tasks WHERE user_email = ? ORDER BY task_date DESC, start_time ASC LIMIT 10', (user_email,))
       rows = cur.fetchall()
       tasks = [dict(r) for r in rows]
       # Budget & expense functionality disabled — UI-only mode.
       # Keep tasks loading but do not query or modify budget/expenses in the DB.
       conn.close()


   # Determine Status Indicator
   # Red > 100%, Orange >= 70%, Green < 70%
   budget_color = "green"
   budget_icon = "fa-check-circle"
  
   if budget_limit > 0:
       pct = (total_spent / budget_limit) * 100
       if pct > 100:
           budget_color = "red"
           budget_icon = "fa-exclamation-circle"
       elif pct >= 70:
           budget_color = "orange"
           budget_icon = "fa-exclamation-triangle"
   elif total_spent > 0:
       # No budget set but spent money -> technically over budget/warning
       budget_color = "red"
       budget_icon = "fa-exclamation-circle"
   else:
       # No budget, no spend -> neutral/green
       pass


   return render_template('dashboard.html', first=first, today=today, tasks=tasks,
                          budget_limit=budget_limit, total_spent=total_spent,
                          top_expense_category=top_expense_category,
                          selected_month=selected_month,
                          selected_month_iso=selected_month_iso,
                          budget_color=budget_color,
                          budget_icon=budget_icon)




def init_tasks_table():
   """Create tasks table if it doesn't exist."""
   conn = get_db()
   cur = conn.cursor()
   cur.execute(
       """
       CREATE TABLE IF NOT EXISTS tasks (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           user_email TEXT NOT NULL,
           title TEXT NOT NULL,
           start_time REAL,
           duration REAL,
           color TEXT,
           is_priority INTEGER DEFAULT 0,
           task_date TEXT,
           completed INTEGER DEFAULT 0,
           created_at TEXT
       )
       """
   )
   conn.commit()
   conn.close()








# JSON API endpoints for client-side integration
@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
   user_email = session.get('user_email')
   if not user_email:
       return jsonify([])
   conn = get_db()
   cur = conn.cursor()
   cur.execute('SELECT * FROM tasks WHERE user_email = ? ORDER BY task_date DESC, start_time ASC', (user_email,))
   rows = cur.fetchall()
   tasks = []
   for r in rows:
       tasks.append({
           'id': r['id'],
           'title': r['title'],
           'start_time': r['start_time'],
           'duration': r['duration'],
           'color': r['color'],
           'is_priority': bool(r['is_priority']),
           'task_date': r['task_date'],
           'completed': bool(r['completed'])
       })
   conn.close()
   return jsonify(tasks)




@app.route('/api/tasks', methods=['POST'])
def api_create_task():
   user_email = session.get('user_email')
   if not user_email:
       return jsonify({'error': 'unauthenticated'}), 401


   data = request.get_json() or {}
   title = data.get('title', '').strip()
   start_time = data.get('start_time')
   duration = data.get('duration')
   color = data.get('color')
   is_priority = 1 if data.get('is_priority') else 0
   task_date = data.get('task_date') or datetime.now().strftime('%Y-%m-%d')


   if not title:
       return jsonify({'error': 'title required'}), 400


   # server-side overlap validation when start_time and duration provided
   try:
       if start_time is not None and duration is not None:
           new_start = float(start_time)
           new_end = new_start + float(duration)
           cur = conn.cursor()
           cur.execute('SELECT id FROM tasks WHERE user_email = ? AND task_date = ? AND start_time IS NOT NULL AND duration IS NOT NULL AND (start_time < ? AND (start_time + duration) > ?)', (user_email, task_date, new_end, new_start))
           if cur.fetchone():
               conn.close()
               return jsonify({'error': 'overlap'}), 400
   except Exception:
       pass


   conn = get_db()
   cur = conn.cursor()
   cur.execute(
       'INSERT INTO tasks (user_email, title, start_time, duration, color, is_priority, task_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
       (user_email, title, start_time, duration, color, is_priority, task_date, datetime.now().isoformat()),
   )
   conn.commit()
   task_id = cur.lastrowid
   conn.close()


   return jsonify({'id': task_id, 'title': title, 'start_time': start_time, 'duration': duration, 'color': color, 'is_priority': bool(is_priority), 'task_date': task_date, 'completed': False}), 201




@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def api_update_task(task_id):
   user_email = session.get('user_email')
   if not user_email:
       return jsonify({'error': 'unauthenticated'}), 401


   data = request.get_json() or {}
   title = data.get('title')
   start_time = data.get('start_time')
   duration = data.get('duration')
   color = data.get('color')
   is_priority = 1 if data.get('is_priority') else 0
   task_date = data.get('task_date')
   completed = 1 if data.get('completed') else 0


   conn = get_db()
   cur = conn.cursor()
   # only update fields provided
   cur.execute('SELECT id FROM tasks WHERE id = ? AND user_email = ?', (task_id, user_email))
   if not cur.fetchone():
       conn.close()
       return jsonify({'error': 'not found'}), 404
   # Determine proposed start/duration/date for overlap check
   cur.execute('SELECT start_time, duration, task_date FROM tasks WHERE id = ? AND user_email = ?', (task_id, user_email))
   existing = cur.fetchone()
   prop_start = start_time if start_time is not None else existing['start_time']
   prop_duration = duration if duration is not None else existing['duration']
   prop_date = task_date if task_date is not None else existing['task_date']


   # Only validate overlap when scheduling fields are being changed by the client
   if any(k in data for k in ('start_time', 'duration', 'task_date')):
       try:
           if prop_start is not None and prop_duration is not None:
               ns = float(prop_start)
               ne = ns + float(prop_duration)
               cur.execute('SELECT id FROM tasks WHERE user_email = ? AND task_date = ? AND id != ? AND start_time IS NOT NULL AND duration IS NOT NULL AND (start_time < ? AND (start_time + duration) > ?)', (user_email, prop_date, task_id, ne, ns))
               if cur.fetchone():
                   conn.close()
                   return jsonify({'error': 'overlap'}), 400
       except Exception:
           pass


   cur.execute('UPDATE tasks SET title = COALESCE(?, title), start_time = COALESCE(?, start_time), duration = COALESCE(?, duration), color = COALESCE(?, color), is_priority = ?, task_date = COALESCE(?, task_date), completed = ? WHERE id = ? AND user_email = ?',
               (title, start_time, duration, color, is_priority, task_date, completed, task_id, user_email))
   conn.commit()
   conn.close()
   return jsonify({'ok': True})




@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def api_delete_task(task_id):
   user_email = session.get('user_email')
   if not user_email:
       return jsonify({'error': 'unauthenticated'}), 401
   conn = get_db()
   cur = conn.cursor()
   cur.execute('DELETE FROM tasks WHERE id = ? AND user_email = ?', (task_id, user_email))
   conn.commit()
   conn.close()
   return jsonify({'ok': True})






@app.route('/tasks')
def tasks():
   # require login
   user_email = session.get('user_email')
   if not user_email:
       flash('Please sign in to view your tasks.')
       return redirect(url_for('index'))


   conn = get_db()
   cur = conn.cursor()
   cur.execute('SELECT * FROM tasks WHERE user_email = ? ORDER BY task_date DESC, start_time ASC', (user_email,))
   rows = cur.fetchall()
   tasks = [dict(r) for r in rows]
   conn.close()


   # pass the user's first name and today's display string so header matches dashboard
   first = session.get('user_first')
   today = datetime.now().strftime('%B %d, %Y')
   return render_template('dailytask.html', tasks=tasks, first=first, today=today)




@app.route('/tasks/add', methods=['POST'])
def add_task():
   user_email = session.get('user_email')
   if not user_email:
       flash('Please sign in to add tasks.')
       return redirect(url_for('index'))


   title = request.form.get('title', '').strip()
   start_time = request.form.get('start_time')
   duration = request.form.get('duration')
   color = request.form.get('color')
   is_priority = 1 if request.form.get('is_priority') == 'on' else 0
   task_date = request.form.get('task_date') or datetime.now().strftime('%Y-%m-%d')


   if not title:
       flash('Task title is required.')
       # honor next param if provided
       next_view = request.form.get('next') or 'tasks'
       return redirect(url_for(next_view))


   try:
       start_time_val = float(start_time) if start_time else None
   except Exception:
       start_time_val = None


   try:
       duration_val = float(duration) if duration else None
   except Exception:
       duration_val = None


   # server-side overlap check for form submissions
   try:
       if start_time_val is not None and duration_val is not None:
           new_start = float(start_time_val)
           new_end = new_start + float(duration_val)
           cur = conn.cursor()
           cur.execute('SELECT id FROM tasks WHERE user_email = ? AND task_date = ? AND start_time IS NOT NULL AND duration IS NOT NULL AND (start_time < ? AND (start_time + duration) > ?)', (user_email, task_date, new_end, new_start))
           if cur.fetchone():
               conn.close()
               flash('Task overlaps an existing task. Choose another time.')
               next_view = request.form.get('next') or 'tasks'
               return redirect(url_for(next_view))
   except Exception:
       pass


   conn = get_db()
   cur = conn.cursor()
   cur.execute(
       'INSERT INTO tasks (user_email, title, start_time, duration, color, is_priority, task_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
       (user_email, title, start_time_val, duration_val, color, is_priority, task_date, datetime.now().isoformat()),
   )
   conn.commit()
   conn.close()


   flash('Task added.')
   next_view = request.form.get('next') or 'tasks'
   return redirect(url_for(next_view))




@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
   user_email = session.get('user_email')
   if not user_email:
       return redirect(url_for('index'))


   conn = get_db()
   cur = conn.cursor()
   # Toggle completed flag
   cur.execute('SELECT completed FROM tasks WHERE id = ? AND user_email = ?', (task_id, user_email))
   row = cur.fetchone()
   if not row:
       conn.close()
       flash('Task not found.')
       return redirect(url_for('tasks'))


   new_val = 0 if row['completed'] else 1
   cur.execute('UPDATE tasks SET completed = ? WHERE id = ? AND user_email = ?', (new_val, task_id, user_email))
   conn.commit()
   conn.close()
   next_view = request.form.get('next') or 'tasks'
   return redirect(url_for(next_view))




@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
   user_email = session.get('user_email')
   if not user_email:
       return redirect(url_for('index'))


   conn = get_db()
   cur = conn.cursor()
   cur.execute('DELETE FROM tasks WHERE id = ? AND user_email = ?', (task_id, user_email))
   conn.commit()
   conn.close()
   flash('Task deleted.')
   next_view = request.form.get('next') or 'tasks'
   return redirect(url_for(next_view))






@app.route('/budgetexpenses')
def budgetexpenses():
   first = session.get('user_first')
   user_email = session.get('user_email')
  
   if not user_email:
       flash('Please sign in to view your budget.')
       return redirect(url_for('index'))


   today = datetime.now().strftime('%B %d, %Y')
  
   # Handle month selection
   selected_month_iso = request.args.get('month')
   selected_month = None
  
   if selected_month_iso:
       try:
           # Parse YYYY-MM
           date_obj = datetime.strptime(selected_month_iso, '%Y-%m')
           selected_month = date_obj.strftime('%B %Y')
       except ValueError:
           # Fallback if invalid format
           selected_month_iso = datetime.now().strftime('%Y-%m')
           selected_month = datetime.now().strftime('%B %Y')
   else:
       # Default to current month
       selected_month_iso = datetime.now().strftime('%Y-%m')
       selected_month = datetime.now().strftime('%B %Y')
      
   # Budget & expense backend disabled — present UI only with placeholder data.
   budget_data = {'income': 0, 'budget_limit': 0}
   expenses = []
   groceries = []
   total_spent = 0
  
   return render_template('budget.html', first=first, today=today,
                          selected_month=selected_month,
                          selected_month_iso=selected_month_iso,
                          budget_data=budget_data,
                          expenses=expenses,
                          groceries=groceries,
                          total_spent=total_spent)








@app.route('/mood')
def mood():
   # require login
   user_email = session.get('user_email')
   if not user_email:
       flash('Please sign in to view your mood tracker.')
       return redirect(url_for('index'))


   first = session.get('user_first')
   today = datetime.now().strftime('%B %d, %Y')
  
   # Placeholder data - in a real app, fetch from DB
   data = {
       'sleep': '7.5',
       'water': '6',
       'activity': 'Light Stretching',
       'stress': 5,
       'mood': 'Neutral'
   }
  
   return render_template('mood.html', first=first, today=today, data=data)




@app.route('/update_mood', methods=['POST'])
def update_mood():
   user_email = session.get('user_email')
   if not user_email:
       return redirect(url_for('index'))
  
   mood_val = request.form.get('mood')
   # Save to DB logic here...
   # For now just flash and redirect
   flash(f"Mood logged: {mood_val}")
  
   return redirect(url_for('mood'))








@app.route('/logout')
def logout():
   session.pop('user_first', None)
   session.pop('user_email', None) # Ensure email is also popped
   session.pop('user_id', None)
   flash('You have been signed out.')
   return redirect(url_for('index'))




@app.route('/my-account')
def my_account():
   user_email = session.get('user_email')
   if not user_email:
       flash('Please sign in.')
       return redirect(url_for('index'))
      
   user_id = session.get('user_id')
   if not user_id:
       # Fallback for old sessions: look up ID by email
       conn = get_db()
       cur = conn.cursor()
       cur.execute('SELECT id FROM users WHERE email = ?', (user_email,))
       row = cur.fetchone()
       conn.close()
       if row:
           user_id = row['id']
           session['user_id'] = user_id
       else:
           flash('Account not found.')
           return redirect(url_for('logout'))
          
   return redirect(url_for('profile', user_id=user_id))




@app.route('/profile/<int:user_id>')
def profile(user_id):
   # logic to fetch user data
   user_email = session.get('user_email')
   if not user_email:
       flash('Please sign in to view your profile.')
       return redirect(url_for('index'))


   conn = get_db()
   cur = conn.cursor()
   # Fetch user details
   cur.execute('SELECT * FROM users WHERE id = ?', (user_id,))
   user_row = cur.fetchone()
   conn.close()


   if not user_row:
       flash('User not found.')
       return redirect(url_for('dashboard'))
  
   # Check if the logged-in user matches the requested profile or is admin (if applicable)
   # For now, simplistic check: email must match
   if user_row['email'] != user_email:
        flash('Unauthorized access.')
        return redirect(url_for('dashboard'))


   # Prepare user object for template
   user = dict(user_row)
   user['password_display'] = '********'
  
   # Ensure fields expected by template exist, map from DB columns
   # DB has: first, last, email, birthdate...
   # Template expects: first_name, last_name, gender, height_display, weight_display
   # We might need to add these columns to DB or handle missing data gracefully.
   # For this iteration, I will map existing DB fields and use placeholders for missing ones.
  
   user['first_name'] = user['first']
   user['last_name'] = user['last']
   user['birthdate_display'] = user['birthdate']
  
   # Placeholders for fields not searching in init_db yet
   user['gender'] = user.get('gender', 'Not Specified')
   user['height_display'] = user.get('height', '0')
   user['weight_display'] = user.get('weight', '0')




   first = session.get('user_first')
   today = datetime.now().strftime('%B %d, %Y')
  
   # If a profile image was uploaded and saved in static/images, expose its URL
   images_dir = Path(__file__).parent / 'static' / 'images'
   profile_filename = f"user_{user_id}_profile.jpg"
   if (images_dir / profile_filename).exists():
       user['profile_pic_url'] = url_for('static', filename=f'images/{profile_filename}')
   else:
       user['profile_pic_url'] = None


   return render_template('profile.html', user=user, first=first, today=today)




@app.route('/profile/<int:user_id>/upload_photo', methods=['POST'])
def upload_profile_photo(user_id):
   # allow only the profile owner to upload
   user_email = session.get('user_email')
   if not user_email or session.get('user_id') != user_id:
       flash('Unauthorized upload attempt.')
       return redirect(url_for('profile', user_id=user_id))


   if 'photo' not in request.files:
       flash('No file part.')
       return redirect(url_for('profile', user_id=user_id))


   file = request.files['photo']
   if file.filename == '':
       flash('No selected file.')
       return redirect(url_for('profile', user_id=user_id))


   # basic validation of allowed extensions
   ALLOWED_EXT = {'.png', '.jpg', '.jpeg', '.gif'}
   _, ext = os.path.splitext(file.filename.lower())
   if ext not in ALLOWED_EXT:
       flash('Unsupported file type. Use PNG/JPG/GIF.')
       return redirect(url_for('profile', user_id=user_id))


   # ensure images dir exists
   images_dir = Path(__file__).parent / 'static' / 'images'
   images_dir.mkdir(parents=True, exist_ok=True)


   # save with deterministic filename for the user
   filename = f'user_{user_id}_profile.jpg'
   save_path = images_dir / filename
   try:
       # convert and save: we simply stream to disk
       file.save(save_path)
       flash('Profile photo updated.')
   except Exception as e:
       print(f"Error saving file: {e}")
       flash('Failed to save photo.')


   return redirect(url_for('profile', user_id=user_id))


@app.route('/profile/edit/<int:user_id>')
def edit_profile(user_id):
    return "Edit Profile Page (Coming Soon)"


if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        import traceback
        traceback.print_exc()

    app.run(debug=True)