from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import json
from pathlib import Path
import sqlite3
from sqlite3 import Connection
import os
from datetime import datetime


app = Flask(__name__, static_folder='images', static_url_path='/images')
app.secret_key = os.environ.get('MOMCARE_SECRET', 'change-this-secret-for-production')


DB_PATH = Path(__file__).parent / 'users.db'


def get_db() -> Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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

        # simple session mark
        session['user_email'] = email
        session['user_first'] = first
        flash('Account created successfully!')
        return redirect(url_for('dashboard'))

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
    cur.execute('SELECT first, password_hash FROM users WHERE email = ?', (email,))
    row = cur.fetchone()
    conn.close()

    if not row:
        flash('Invalid email or password.')
        return redirect(url_for('index'))

    first = row['first']
    password_hash = row['password_hash']

    if not check_password_hash(password_hash, password):
        flash('Invalid email or password.')
        return redirect(url_for('index'))

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

if __name__ == '__main__':
    app.run(debug=True)




@app.route('/dashboard')
def dashboard():
    first = session.get('user_first')
    today = datetime.now().strftime('%B %d, %Y')

    # load upcoming tasks for the signed-in user (limit 10)
    user_email = session.get('user_email')
    tasks = []
    if user_email:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM tasks WHERE user_email = ? ORDER BY task_date DESC, start_time ASC LIMIT 10', (user_email,))
        rows = cur.fetchall()
        tasks = [dict(r) for r in rows]
        conn.close()

    return render_template('dashboard.html', first=first, today=today, tasks=tasks)


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

@app.route('/dailytask_static/<path:filename>')
def dailytask_static(filename):
    """Serve static files from the DAILYTASK folder (CSS/JS/images).
    This avoids changing the app's static folder configuration.
    """
    base = Path(__file__).parent / 'DAILYTASK'
    return send_from_directory(base, filename)


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
    today = datetime.now().strftime('%B %d, %Y')
    
    return render_template('budget.html', first=first, today=today)




@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_first', None)
    flash('You have been signed out.')
    return redirect(url_for('index'))
