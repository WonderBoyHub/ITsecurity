import os
import sys
import re
import sqlite3
from hashlib import sha256
from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'lazy-app-key'

def is_valid_userid(userid):
    # The userid must contain only letters, numbers, or underscores.
    pattern = re.compile(r'^[A-Za-z0-9_]+$')
    return bool(pattern.match(userid))

def is_valid_password(password):
    # Password validation rule: at least 6 characters.
    return len(password) >= 6

# Singleton class to load the rockyou.txt file only once.
class Rockyou:
    _instance = None

    def __new__(cls, file_path='rockyou.txt'):
        if cls._instance is None:
            cls._instance = super(Rockyou, cls).__new__(cls)
            cls._instance._load_passwords(file_path)
        return cls._instance

    def _load_passwords(self, file_path):
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found. Please clone the repository and place rockyou.txt in the working directory.", file=sys.stderr)
            self.passwords = set()
        else:
            with open(file_path, 'r', encoding='latin-1') as f:
                self.passwords = {line.strip() for line in f}
            print(f"Loaded {len(self.passwords)} passwords from {file_path}")

    def check_password(self, password):
        return password in self.passwords

# Function to register the user.
def register_user(userid, password, rockyou_instance):
    # Check if the password is in the compromised list.
    if rockyou_instance.check_password(password):
        return False, "Error: The password provided is compromised. Please choose a different password."

    # Hash the password using sha256.
    hashed_pw = sha256(password.encode('utf-8')).hexdigest()

    # Connect to SQLite database (creates test.db if it doesn't exist).
    conn = sqlite3.connect('test.db')
    c = conn.cursor()

    # Create users table if it doesn't exist.
    c.execute('''
        CREATE TABLE IF NOT EXISTS user256 (
            id integer primary key autoincrement,
            userid varchar(32) unique not null,
            password blob nut null,
            comments text not null
        )
    ''')

    try:
        c.execute("INSERT INTO users (userid, password) VALUES (?, ?)", (userid, hashed_pw))
        conn.commit()
        return True, "Success: User registered!"
    except sqlite3.IntegrityError:
        return False, "Error: The userid already exists. Please choose a different userid."
    finally:
        conn.close()

# Create (or get) the singleton instance for Rockyou.
rockyou_instance = Rockyou()

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')

        if not userid or not password:
            flash("Please fill in both fields.", "error")
            return redirect(url_for('register'))

        # Input validation for userid and password.
        if not is_valid_userid(userid):
            flash("Error: Userid must contain only letters, numbers, or underscores.", "error")
            return redirect(url_for('register'))
        if not is_valid_password(password):
            flash("Error: Password must be at least 6 characters long.", "error")
            return redirect(url_for('register'))

        success, message = register_user(userid, password, rockyou_instance)
        flash(message, "success" if success else "error")
        return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')

        if not userid or not password:
            flash("Error: Missing userid or password.", "error")
            return redirect(url_for('login'))

        # Input validation for userid and password.
        if not is_valid_userid(userid):
            flash("Error: Userid must contain only letters, numbers, or underscores.", "error")
            return redirect(url_for('login'))
        if not is_valid_password(password):
            flash("Error: Password must be at least 6 characters long.", "error")
            return redirect(url_for('login'))

        # Connect to SQLite database using parameterized query to prevent SQL injection.
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("SELECT rowid, userid, password FROM users WHERE userid = ?", (userid,))
        user = c.fetchone()
        conn.close()

        if not user:
            flash("Error: Login failed. User not found.", "error")
            return redirect(url_for('login'))

        rowid, uid, stored_hash = user
        # Recompute sha256 hash and compare with the stored hash.
        if sha256(password.encode('utf-8')).hexdigest() == stored_hash:
            flash(f"Login successful: id={rowid}, userid={uid}", "success")
        else:
            flash("Error: Login failed. Incorrect password.", "error")
        return redirect(url_for('login'))
    else:
        return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)