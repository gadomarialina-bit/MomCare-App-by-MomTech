from flask import Flask, render_template, request, redirect, url_for, flash, session
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
            gender TEXT,
            height TEXT,
            weight TEXT,
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



init_db()


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


@app.route('/dashboard')
def dashboard():
    first = session.get('user_first')
    today = datetime.now().strftime('%B %d, %Y')
    return render_template('dashboard.html', first=first, today=today)


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


@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_first', None)
    flash('You have been signed out.')
    return redirect(url_for('index'))


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
