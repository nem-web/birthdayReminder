from flask import Flask, render_template_string, request, redirect, flash
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import schedule
import time
import threading
import smtplib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Firebase initialization
cred = credentials.Certificate("serviceAccountKey.json")  # Replace with your Firebase credentials file
firebase_admin.initialize_app(cred)
db = firestore.client()

# HTML template in a string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Birthday Reminder</title>
</head>
<body>
    <h1>Birthday Reminder</h1>
    <form action="/add_birthday" method="post">
        <label for="name">Name:</label><br>
        <input type="text" id="name" name="name" required><br><br>
        <label for="email">Email:</label><br>
        <input type="email" id="email" name="email" required><br><br>
        <label for="date">Birthday (YYYY-MM-DD):</label><br>
        <input type="date" id="date" name="date" required><br><br>
        <button type="submit">Add Birthday</button>
    </form>
    <p>{{ get_flashed_messages() }}</p>
</body>
</html>
"""

# Function to add a birthday to Firestore
def add_birthday_to_firestore(name, email, date):
    db.collection("birthdays").add({
        "name": name,
        "email": email,
        "date": date
    })

# Function to get today's birthdays
def get_today_birthdays():
    today = datetime.now().strftime("%Y-%m-%d")
    birthdays = db.collection("birthdays").where("date", "==", today).stream()
    return [{"name": b.get("name"), "email": b.get("email")} for b in birthdays]

# Function to send email notifications
def send_email_notification(name, email):
    sender_email = "system.bdayreminder@gmail.com"  # Replace with your email
    reciever_email = "kathariyanemchandra@gmail.com"  # Replace with your email
    sender_password = "actv lvwy iznt ogcu"        # Replace with your email password
    subject = f"Reminder: It's {name}'s Birthday Today!"
    body = f"Don't forget to wish {name} a happy birthday!"
    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, sender_email, message)  # Sends email to yourself
    except Exception as e:
        print(f"Failed to send email: {e}")

# Scheduled function to check birthdays
def check_and_notify_birthdays():
    today_birthdays = get_today_birthdays()
    for birthday in today_birthdays:
        send_email_notification(birthday["name"], birthday["email"])

# Schedule the task to run daily
def schedule_task():
    schedule.every().day.at("08:00").do(check_and_notify_birthdays)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start the scheduler in a separate thread
thread = threading.Thread(target=schedule_task)
thread.daemon = True
thread.start()

# Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/add_birthday', methods=['POST'])
def add_birthday():
    name = request.form["name"]
    email = request.form["email"]
    date = request.form["date"]

    add_birthday_to_firestore(name, email, date)
    flash("Birthday added successfully!")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
