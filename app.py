from flask import Flask, render_template, request, redirect, flash
import psycopg2
from datetime import datetime
import smtplib
import schedule
import time
import threading
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Get PostgreSQL database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Initialize PostgreSQL Database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS birthdays (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            date DATE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Email sending function
def send_email(name, email):
    sender_email = "your_email@example.com"
    sender_password = "your_password"
    subject = f"Reminder: It's {name}'s Birthday Today!"
    body = f"Don't forget to wish {name} a happy birthday!"
    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message)
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to check for birthdays
def check_birthdays():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, email FROM birthdays WHERE date = %s", (today,))
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        send_email(row[0], row[1])

# Schedule the check_birthdays function to run daily
def schedule_task():
    schedule.every().day.at("08:00").do(check_birthdays)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Run the scheduler in a separate thread
thread = threading.Thread(target=schedule_task)
thread.daemon = True
thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_birthday', methods=['POST'])
def add_birthday():
    name = request.form['name']
    email = request.form['email']
    date = request.form['date']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO birthdays (name, email, date) VALUES (%s, %s, %s)", (name, email, date))
    conn.commit()
    conn.close()

    flash("Birthday added successfully!")
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
