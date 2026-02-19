import tkinter as tk
from tkinter import Canvas, Scrollbar, Frame, Label, Entry, Button
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "appointments.json"

#STORAGE
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


#  REMINDER 
class ReminderEngine:
    def __init__(self, storage):
        self.storage = storage

    def get_today_and_tomorrow(self):
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        today_list = []
        tomorrow_list = []

        for appt in self.storage.get_appointments():
            try:
                d = datetime.strptime(appt.get("dt", ""), "%Y-%m-%d").date()
                if d == today:
                    today_list.append(appt)
                elif d == tomorrow:
                    tomorrow_list.append(appt)
            except:
                continue

        return today_list, tomorrow_list


#  UI 
class ChatBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Appointment Assistant")
        self.root.geometry("520x720")
        self.root.configure(bg="#0f172a")

        self.storage = StorageManager(DATA_FILE)
        self.reminder = ReminderEngine(self.storage)

        self.specialties = [
            "General Medicine",
            "Cardiology",
            "Dermatology",
            "Orthopedics",
            "Neurology"
        ]

        self.flow = None
        self.step = 0
        self.temp = {}

        #  SCROLLABLE CHAT
        container = Frame(root, bg="#0f172a")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = Canvas(container, bg="#0f172a", highlightthickness=0)
        self.frame = Frame(self.canvas, bg="#0f172a")
        self.scroll = Scrollbar(container, command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )

        # INPUT
        bottom = Frame(root, bg="#0f172a")
        bottom.pack(fill="x", padx=10, pady=10)

        self.entry = Entry(bottom, font=("Segoe UI", 12),
                           bg="#1e293b", fg="white",
                           insertbackground="white", relief="flat")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", self.on_enter)

        Button(bottom, text="Send", command=self.on_enter,
               bg="#38bdf8", fg="black",
               font=("Segoe UI", 10, "bold"),
               relief="flat", padx=15).pack(side="right")

        self.bot("Hello! I manage your appointments.")
        self.bot("Type: schedule OR view OR reminder")

    #  AUTO SCROLL 
    def scroll_bottom(self):
        self.root.update_idletasks()
        self.canvas.yview_moveto(1)

    #  CHAT 
    def user(self, text):
        Label(self.frame, text=text, bg="#2563eb", fg="white",
              font=("Segoe UI", 11), wraplength=320,
              padx=12, pady=8).pack(anchor="e", pady=6)
        self.scroll_bottom()

    def bot(self, text):
        Label(self.frame, text=text, bg="#1e293b", fg="white",
              font=("Segoe UI", 11), wraplength=320,
              padx=12, pady=8, justify="left").pack(anchor="w", pady=6)
        self.scroll_bottom()

    # CARD
    def appointment_card(self, a):
        card = Frame(self.frame, bg="#111827",
                     highlightbackground="#334155",
                     highlightthickness=1, padx=12, pady=8)

        Label(card, text=f"{a['dt']}   {a['tm']}",
              font=("Segoe UI", 11, "bold"),
              fg="#38bdf8", bg="#111827").pack(anchor="w")

        Label(card, text=f"Dr {a['doc']}  |  {a['spec']}",
              fg="white", bg="#111827").pack(anchor="w", pady=2)

        Label(card, text=a['hos'],
              fg="#cbd5f5", bg="#111827").pack(anchor="w")

        card.pack(fill="x", pady=6)
        self.scroll_bottom()

    #  INPUT 
    def on_enter(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        self.user(text)
        self.entry.delete(0, "end")
        self.process(text.lower(), text)

    # COMMAND 
    def process(self, lower, original):

        if "view" in lower:
            self.show_appointments()
            return

        if "reminder" in lower:
            self.show_reminders()
            return

        if self.flow == "schedule":
            self.schedule_flow(original)
            return

        if "schedule" in lower:
            self.flow = "schedule"
            self.step = 1
            self.temp = {}
            self.bot("Choose specialty:\n" + ", ".join(self.specialties))
        else:
            self.bot("Type schedule / view / reminder")

    # SCHEDULING
    def schedule_flow(self, text):

        if self.step == 1:
            for s in self.specialties:
                if text.lower() == s.lower():
                    self.temp["spec"] = s
                    self.step = 2
                    self.bot("Doctor name?")
                    return
            self.bot("Choose valid specialty")

        elif self.step == 2:
            self.temp["doc"] = text.title()
            self.step = 3
            self.bot("Hospital name?")

        elif self.step == 3:
            self.temp["hos"] = text.title()
            self.step = 4
            self.bot("Date (YYYY-MM-DD)?")

        elif self.step == 4:
            try:
                datetime.strptime(text, "%Y-%m-%d")
                self.temp["dt"] = text
                self.step = 5
                self.bot("Time (HH:MM)?")
            except:
                self.bot("Invalid date")

        elif self.step == 5:
            try:
                datetime.strptime(text, "%H:%M")
                self.temp["tm"] = text
                self.storage.add_appointment(self.temp.copy())
                self.bot("APPOINTMENT SCHEDULED ✔")
                self.flow = None
                self.step = 0
                self.temp = {}
            except:
                self.bot("Invalid time")

    # VIEW 
    def show_appointments(self):

        self.storage.data = self.storage.load_data()
        appts = self.storage.get_appointments()

        valid = []
        for a in appts:
            try:
                if all(k in a for k in ("dt","tm","doc","spec","hos")):
                    datetime.strptime(a["dt"], "%Y-%m-%d")
                    datetime.strptime(a["tm"], "%H:%M")
                    valid.append(a)
            except:
                continue

        if not valid:
            self.bot("No appointments found")
            return

        valid.sort(
            key=lambda a: datetime.strptime(
                a["dt"]+" "+a["tm"], "%Y-%m-%d %H:%M"
            )
        )

        self.bot("YOUR APPOINTMENTS")
        for a in valid:
            self.appointment_card(a)

    # REMINDER 
    def show_reminders(self):

        self.storage.data = self.storage.load_data()
        today, tomorrow = self.reminder.get_today_and_tomorrow()

        today = today or []
        tomorrow = tomorrow or []

        if not today and not tomorrow:
            self.bot("No upcoming appointments")
            return

        if today:
            self.bot("TODAY")
            for a in today:
                if all(k in a for k in ("dt","tm","doc","spec","hos")):
                    self.appointment_card(a)

        if tomorrow:
            self.bot("TOMORROW")
            for a in tomorrow:
                if all(k in a for k in ("dt","tm","doc","spec","hos")):
                    self.appointment_card(a)

# RUN
root = tk.Tk()
ChatBotApp(root)
root.mainloop()
