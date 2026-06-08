from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import threading
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Llama AI API Configuration (Replace with your actual API key)
YOUR_API_URL = "https://api.llama.com/v1/chat/completions"
YOUR_API_KEY = "YOUR_API_KEY"

# Lock to prevent double bookings
lock = threading.Lock()

# Database Initialization
def db_connect():
    conn = sqlite3.connect("appointments.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        doctor TEXT NOT NULL,
                        date TEXT NOT NULL,
                        time TEXT NOT NULL,
                        mode TEXT NOT NULL)''')
    conn.commit()
    conn.close()

db_connect()

# AI-Powered Date Suggestion Using Llama AI
def suggest_appointment(doctor):
    headers = {"Authorization": f"Bearer {Your_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-chat",
        "messages": [{"role": "user", "content": f"Suggest 3 different available appointment slots for {doctor}"}]
    }
    response = requests.post(LLAMA_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        suggestions = response.json().get("choices", [])[0].get("message", {}).get("content", "").split("\n")
        return suggestions  # Returns a list of time slots
    return ["No AI suggestion available."]

# API: Book an Appointment
@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    try:
        data = request.json
        print("Received Data:", data)
        
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        doctor = data.get("doctor")
        mode = data.get("mode")  # "manual" or "ai"
        date = data.get("date")
        time = data.get("time")

        if not all([name, email, phone, doctor, mode, date, time]):
            print("Missing fields:", {k: v for k, v in data.items() if not v})  # Debug missing fields
            return jsonify({"error": "Missing required fields"}), 400

        conn = sqlite3.connect("appointments.db", check_same_thread=False)
        cursor = conn.cursor()

        with lock:
            cursor.execute("SELECT * FROM appointments WHERE doctor=? AND date=? AND time=?", (doctor, date, time))
            if cursor.fetchone():
                return jsonify({"error": "Slot already booked. Choose another time."}), 409

            cursor.execute("INSERT INTO appointments (name, email, phone, doctor, date, time, mode) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (name, email, phone, doctor, date, time, mode))
            conn.commit()
            print("Inserted Successfully!")  # Debugging output

        conn.close()
        return jsonify({"message": "Appointment booked successfully!", "name": name, "email": email, "date": date, "time": time, "mode": mode}), 201

    except Exception as e:
        print("Database Error:", str(e))  # Debugging output
        return jsonify({"error": str(e)}), 500

# API: Get All Appointments
@app.route('/appointments', methods=['GET'])
def get_appointments():
    try:
        conn = sqlite3.connect("appointments.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments")
        appointments = cursor.fetchall()
        conn.close()

        result = [{"id": a[0], "name": a[1], "email": a[2], "phone": a[3], "doctor": a[4], "date": a[5], "time": a[6], "mode": a[7]} for a in appointments]
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Home Route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the AI-Powered Appointment Booking System!"})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)