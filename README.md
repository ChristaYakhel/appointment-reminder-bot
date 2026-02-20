APPOINTMENT REMINDER BOT

☆☆☆ A conversational appointment management system built with Python and Tkinter. Designed to simplify how users schedule and track medical appointments through a clean, chat-based interface — no forms, no complexity.☆☆☆


OVERVIEW
Most appointment management tools rely on complex forms and rigid workflows.
This bot takes a different approach — it guides users step-by-step through conversation,
validates every input, and surfaces reminders automatically.


 FEATURES
☆☆ Chat Interface	Scrollable conversational UI built with Tkinter
☆☆ Smart Scheduling	Multi-step booking with validation at every stage
☆☆ Specialty Matching	Accepts partial input (e.g., cardio → Cardiology)
☆☆ View Appointments	Lists all upcoming appointments sorted by date
☆☆ 24-Hour Reminders	Shows appointments due within the next 24 hours
☆☆ Delete / Cancel	Remove appointments from a numbered list
☆☆ Persistent Storage	Data saved locally using JSON
☆☆ Input Validation	Rejects past dates, empty fields, invalid formats


TECHNOLOGY STACK

☆Built using Python Tkinter for a conversational desktop interface
☆Uses JSON-based local storage for persistent data management
☆Implements scheduling logic with Python datetime utilities
☆Designed to run on Python 3.11+

SYSTEM ARCHITECURE

User Input
    ↓
Intent Detection
    ↓
Flow Manager  ←→  Storage Manager
    ↓
UI Renderer


☆****GETTING STARTED****☆

** Prerequisites -Python 3.11 or higher

**INSTALLATION

git clone https://github.com/ChristaYakhel/appointment-reminder-bot.git
cd appointment-reminder-bot
python main.py

**Usage
schedule   - Create a new appointment
view       - List upcoming appointments
reminder   - Show appointments within 24 hours
delete     - Cancel an appointment


PROJECT STRUCTURE

appointment-reminder-bot

├── main.py

├── appointments.json

└── README.md



















HOW TO USE
1. Clone the repository
   git clone https://github.com/<your-username>/Appointment-Reminder-Bot.git
   cd Appointment-Reminder-Bot

2.Run the Bot
   python bot.py

3. Interact with the Bot

  Type schedule → Bot guides you step by step to schedule an appointment
  Type view → View all your appointments
  Type reminder → Check tomorrow’s appointments


  






