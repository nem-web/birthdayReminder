from flask import Flask, render_template, request, redirect, flash
import sqlite3
from datetime import datetime
import smtplib
import schedule
import time
import threading

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Use persistent storage for SQLite
DB_PATH = "/persistent/database.db"

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS birthdays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Email notification function
def send_email(name):
    sender_email = "system.bdayreminder@gmail.com"  # Replace with your email
    sender_password = "actv lvwy iznt ogcu"  # Replace with your email password
    recipient_email = "kathariyanemchandra.com"  # Replace with your email

    subject = f"Birthday Reminder: {name}'s Birthday Today!"
    body = f"Hello! This is a reminder that today is {name}'s birthday."
    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message)
        print(f"Email sent for {name}'s birthday.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to check birthdays
def check_birthdays():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM birthdays WHERE date = ?", (today,))
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        send_email(row[0])

# Scheduler task
def schedule_task():
    schedule.every().day.at("08:00").do(check_birthdays)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start the scheduler in a background thread
thread = threading.Thread(target=schedule_task)
thread.daemon = True
thread.start()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM birthdays")
    birthdays = cursor.fetchall()
    conn.close()
    return render_template('index.html', birthdays=birthdays)

@app.route('/add_birthday', methods=['POST'])
def add_birthday():
    name = request.form['name']
    date = request.form['date']

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO birthdays (name, date) VALUES (?, ?)", (name, date))
    conn.commit()
    conn.close()

    flash("Birthday added successfully!")
    return redirect('/')

@app.route('/delete_birthday/<int:id>')
def delete_birthday(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM birthdays WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Birthday deleted successfully!")
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
