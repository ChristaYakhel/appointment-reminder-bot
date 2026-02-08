import tkinter as tk
from tkinter import Canvas, Scrollbar, Frame, Label, Entry, Button
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "appointments.json"

class StorageManager:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except:
            return []

    def save_data(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_appointment(self, appt):
        self.data.append(appt)
        self.save_data()

    def get_appointments(self):
        return self.data

class ReminderEngine:
    def __init__(self, storage):
        self.storage = storage

    def get_tomorrow(self):
        today = datetime.now().date()
        results = []
        for appt in self.storage.get_appointments():
            try:
                appt_date = datetime.strptime(appt["dt"], "%Y-%m-%d").date()
                if appt_date == today + timedelta(days=1):
                    results.append(appt)
            except: continue
        return results

class ChatBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Appointment Reminder Bot ")
        self.root.geometry("500x650")
        self.root.configure(bg="white")

        self.storage = StorageManager(DATA_FILE)
        self.reminder = ReminderEngine(self.storage)
        self.specialties = ["General Medicine", "Cardiology", "Dermatology", "Orthopedics", "Neurology"]

        self.flow = None
        self.step = 0
        self.temp = {}

        # Chat container
        self.canvas = Canvas(root, bg="white", highlightthickness=0)
        self.frame = Frame(self.canvas, bg="white")
        self.scroll = Scrollbar(root, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_window((0,0), window=self.frame, anchor="nw")
        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Input
        self.bottom = Frame(root, bg="light blue")
        self.bottom.pack(fill="x")
        self.entry = Entry(self.bottom, font=("Arial", 13))
        self.entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.entry.bind("<Return>", self.on_enter)
        self.send_btn = Button(self.bottom, text="Send", bg="blue", fg="white", font=("Arial",12), command=self.on_enter)
        self.send_btn.pack(side="right", padx=10, pady=10)

        # Welcome
        self.bot_message("Hello! I'm your Appointment Bot ")
        self.bot_message("Type one of: schedule / view / reminder")

    def user_message(self, text):
        msg = Frame(self.frame, bg="white")
        Label(msg, text=text, bg="light blue", fg="black", font=("Arial",12), wraplength=350, justify="left").pack(padx=10, pady=5, anchor="e")
        msg.pack(anchor="e", pady=2, padx=10)
        self.canvas.yview_moveto(1)

    def bot_message(self, text):
        msg = Frame(self.frame, bg="white")
        Label(msg, text=text, bg="white", fg="blue", font=("Arial",12), wraplength=350, justify="left").pack(padx=10, pady=5, anchor="w")
        msg.pack(anchor="w", pady=2, padx=10)
        self.canvas.yview_moveto(1)

    def on_enter(self, event=None):
        text = self.entry.get().strip()
        if not text: return
        self.user_message(text)
        self.entry.delete(0, "end")
        self.process_command(text)

    def process_command(self, cmd):
        cmd_lower = cmd.strip().lower()

        if self.flow == "schedule":
            self.schedule_flow(cmd)
            return

        if "schedule" in cmd_lower:
            self.flow = "schedule"
            self.step = 1
            self.temp = {}
            self.bot_message("Let's schedule your appointment.")
            self.bot_message("Step 1: Choose specialty:\n" + ", ".join(self.specialties))
        elif "view" in cmd_lower:
            self.show_appointments()
        elif "reminder" in cmd_lower:
            self.show_reminders()
        else:
            self.bot_message("I didn't understand. Try: schedule / view / reminder")

    def schedule_flow(self, text):
        text_clean = text.strip()
        if self.step == 1:
            matched = None
            for s in self.specialties:
                if text_clean.lower() == s.lower():
                    matched = s
                    break
            if not matched:
                self.bot_message("Please choose a valid specialty:\n" + ", ".join(self.specialties))
                return
            self.temp["spec"] = matched
            self.step = 2
            self.bot_message("Step 2: Doctor name?")
        elif self.step == 2:
            self.temp["doc"] = text_clean.title()
            self.step = 3
            self.bot_message("Step 3: Hospital name?")
        elif self.step == 3:
            self.temp["hos"] = text_clean.title()
            self.step = 4
            self.bot_message("Step 4: Date (YYYY-MM-DD)?")
        elif self.step == 4:
            try:
                datetime.strptime(text_clean, "%Y-%m-%d")
                self.temp["dt"] = text_clean
                self.step = 5
                self.bot_message("Step 5: Time (HH:MM)?")
            except:
                self.bot_message("Invalid date. Format: YYYY-MM-DD")
        elif self.step == 5:
            try:
                datetime.strptime(text_clean, "%H:%M")
                self.temp["tm"] = text_clean
                self.storage.add_appointment(self.temp)
                self.bot_message(f" Appointment scheduled with Dr. {self.temp['doc']} on {self.temp['dt']} at {self.temp['tm']}.")
                self.flow = None
                self.step = 0
            except:
                self.bot_message("Invalid time. Format: HH:MM")

    def show_appointments(self):
        appts = self.storage.get_appointments()
        if not appts:
            self.bot_message("No appointments found.")
            return
        out = "Your Appointments:\n"
        for a in appts:
            out += f"- {a['dt']} {a['tm']} : Dr. {a['doc']} ({a['spec']}) @ {a['hos']}\n"
        self.bot_message(out)

    def show_reminders(self):
        tomorrow = self.reminder.get_tomorrow()
        if not tomorrow:
            self.bot_message("No appointments for tomorrow.")
            return
        out = "Tomorrow's Appointments:\n"
        for a in tomorrow:
            out += f"- {a['dt']} {a['tm']} : Dr. {a['doc']} ({a['spec']}) @ {a['hos']}\n"
        self.bot_message(out)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatBotApp(root)
    root.mainloop()




