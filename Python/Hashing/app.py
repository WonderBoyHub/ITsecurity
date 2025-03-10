import os
import sys
import sqlite3
import bcrypt
from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'lazy-app-key'

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

    # Hash the password using bcrypt.
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Connect to SQLite database (creates test.db if it doesn't exist).
    conn = sqlite3.connect('test.db')
    c = conn.cursor()

    # Create users table if it doesn't exist.
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            userid TEXT PRIMARY KEY,
            password BLOB
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

        success, message = register_user(userid, password, rockyou_instance)
        flash(message, "success" if success else "error")
        return redirect(url_for('register'))

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)