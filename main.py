import tkinter as tk
from tkinter import Canvas, Scrollbar, Frame, Label, Entry, Button, messagebox
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "appointments.json"


# STORAGE 
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
        except Exception as e:
            print(f"[Storage] Load error: {e}")
            return []

    def save_data(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"[Storage] Save error: {e}")

    def add_appointment(self, appt):
        self.data.append(appt)
        self.save_data()

    def delete_appointment(self, index):
        if 0 <= index < len(self.data):
            del self.data[index]
            self.save_data()
            return True
        return False

    def get_appointments(self):
        return self.data


# UI
class ChatBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Appointment Assistant")
        self.root.geometry("560x760")
        self.root.configure(bg="#0f172a")

        self.storage = StorageManager(DATA_FILE)

        self.notified_file = "notified.json"
        self.notified = self._load_notified()

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

        # SCROLLABLE CHAT
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

        #INPUT
        bottom = Frame(root, bg="#0f172a")
        bottom.pack(fill="x", padx=10, pady=10)

        self.entry = Entry(bottom, font=("Segoe UI", 12),
                           bg="#1e293b", fg="white",
                           insertbackground="white", relief="flat")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=6)
        self.entry.bind("<Return>", self.on_enter)

        Button(bottom, text="Send", command=self.on_enter,
               bg="#38bdf8", fg="#0f172a",
               font=("Segoe UI", 10, "bold"),
               relief="flat", padx=15, pady=6).pack(side="right")

        self.bot("👋 Hello! I manage your appointments.")
        self.bot("Type: schedule  |  view  |  reminder  |  delete")

        self.start_auto_checker()

    # NOTIFIED PERSISTENCE
    def _load_notified(self):
        if not os.path.exists(self.notified_file):
            return set()
        try:
            with open(self.notified_file, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()

    def _save_notified(self):
        try:
            with open(self.notified_file, "w") as f:
                json.dump(list(self.notified), f)
        except Exception as e:
            print(f"[Notified] Save error: {e}")

    # AUTO REMINDER LOOP
    def start_auto_checker(self):
        self.check_due_appointments()
        self.root.after(60000, self.start_auto_checker)  

    def check_due_appointments(self):
        self.storage.data = self.storage.load_data()
        now = datetime.now()

        for a in self.storage.get_appointments():
            try:
                appt_time = datetime.strptime(
                    a["dt"] + " " + a["tm"],
                    "%Y-%m-%d %H:%M"
                )

                unique_id = a["dt"] + "_" + a["tm"] + "_" + a["doc"]
                diff = (now - appt_time).total_seconds()
                if -60 <= diff <= 180:  
                    if unique_id not in self.notified:
                        self.bot(f"⏰ REMINDER: Appointment with Dr {a['doc']} now!")
                        self.appointment_card(a)
                        messagebox.showinfo(
                            "Appointment Reminder",
                            f"You have an appointment with Dr {a['doc']} now!"
                        )
                        self.notified.add(unique_id)
                        self._save_notified()  

            except Exception as e:
                print(f"[Reminder] Error: {e}")
                continue

    # CHAT 
    def user(self, text):
        Label(self.frame, text=text, bg="#2563eb", fg="white",
              font=("Segoe UI", 11), wraplength=340,
              padx=12, pady=8).pack(anchor="e", pady=6)
        self.scroll_bottom()

    def bot(self, text):
        Label(self.frame, text=text, bg="#1e293b", fg="white",
              font=("Segoe UI", 11), wraplength=340,
              padx=12, pady=8, justify="left").pack(anchor="w", pady=6)
        self.scroll_bottom()

    def scroll_bottom(self):
        self.root.update_idletasks()
        self.canvas.yview_moveto(1)

    # CARD
    def appointment_card(self, a, index=None):
        card = Frame(self.frame, bg="#111827",
                     highlightbackground="#334155",
                     highlightthickness=1, padx=12, pady=8)

        Label(card, text=f"🗓  {a['dt']}   🕐 {a['tm']}",
              font=("Segoe UI", 11, "bold"),
              fg="#38bdf8", bg="#111827").pack(anchor="w")

        Label(card, text=f"👨‍⚕️  Dr {a['doc']}  |  {a['spec']}",
              fg="white", bg="#111827").pack(anchor="w", pady=2)

        Label(card, text=f"🏥  {a['hos']}",
              fg="#cbd5e1", bg="#111827").pack(anchor="w")  

        if index is not None:
            def make_delete(i):
                def do_delete():
                    if messagebox.askyesno("Delete", "Delete this appointment?"):
                        if self.storage.delete_appointment(i):
                            card.destroy()
                            self.bot("✅ Appointment deleted.")
                        else:
                            self.bot("⚠️ Could not delete — try again.")
                return do_delete

            Button(card, text="🗑 Delete", command=make_delete(index),
                   bg="#dc2626", fg="white",
                   font=("Segoe UI", 9, "bold"),
                   relief="flat", padx=8, pady=2).pack(anchor="e", pady=(4, 0))

        card.pack(fill="x", pady=6)
        self.scroll_bottom()

    # INPUT
    def on_enter(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        self.user(text)
        self.entry.delete(0, "end")
        self.process(text.lower(), text)

    # COMMAND
    def process(self, lower, original):

        if self.flow == "schedule":
            self.schedule_flow(original)
            return

        if self.flow == "delete":
            self.delete_flow(lower)
            return

        if "view" in lower:
            self.show_appointments()
            return

        if "reminder" in lower:
            self.show_reminders()
            return

        if "delete" in lower or "cancel" in lower:
            self.start_delete_flow()
            return

        if "schedule" in lower:
            self.flow = "schedule"
            self.step = 1
            self.temp = {}
            numbered = "\n".join(
                f"  {i+1}. {s}" for i, s in enumerate(self.specialties)
            )
            self.bot(f"Choose specialty (type number or name):\n{numbered}")
        else:
            self.bot("Type: schedule  |  view  |  reminder  |  delete")

    #SCHEDULING 
    def schedule_flow(self, text):

        if self.step == 1:
            matched = None

            if text.strip().isdigit():
                idx = int(text.strip()) - 1
                if 0 <= idx < len(self.specialties):
                    matched = self.specialties[idx]

            if not matched:
                for s in self.specialties:
                    if text.strip().lower() in s.lower():
                        matched = s
                        break

            if matched:
                self.temp["spec"] = matched
                self.step = 2
                self.bot(f"✅ Specialty: {matched}\n\nDoctor name?")
            else:
                self.bot("⚠️ No matching specialty. Try again or type number (1–5).")

        elif self.step == 2:
            if len(text.strip()) < 2:
                self.bot("⚠️ Please enter a valid doctor name (at least 2 characters).")
                return
            self.temp["doc"] = text.strip().title()
            self.step = 3
            self.bot("Hospital name?")

        elif self.step == 3:
            if len(text.strip()) < 2:
                self.bot("⚠️ Please enter a valid hospital name.")
                return
            self.temp["hos"] = text.strip().title()
            self.step = 4
            self.bot("Date (YYYY-MM-DD)?")

        elif self.step == 4:
            try:
                parsed_date = datetime.strptime(text.strip(), "%Y-%m-%d")
                if parsed_date.date() < datetime.now().date():
                    self.bot("⚠️ That date is in the past. Please enter a future date.")
                    return
                self.temp["dt"] = text.strip()
                self.step = 5
                self.bot("Time (HH:MM in 24-hour format)?")
            except ValueError:
                self.bot("⚠️ Invalid date. Use format YYYY-MM-DD (e.g. 2025-08-15).")

        elif self.step == 5:
            try:
                datetime.strptime(text.strip(), "%H:%M")
                self.temp["tm"] = text.strip()
                self.storage.add_appointment(self.temp.copy())
                self.bot(
                    f"✅ APPOINTMENT SCHEDULED!\n\n"
                    f"📅 {self.temp['dt']} at {self.temp['tm']}\n"
                    f"👨‍⚕️ Dr {self.temp['doc']} — {self.temp['spec']}\n"
                    f"🏥 {self.temp['hos']}"
                )
                self.flow = None
                self.step = 0
                self.temp = {}
            except ValueError:
                self.bot("⚠️ Invalid time. Use HH:MM format (e.g. 14:30).")

    # DELETE FLOW
    def start_delete_flow(self):
        self.storage.data = self.storage.load_data()
        now = datetime.now()

        future = []
        for i, a in enumerate(self.storage.get_appointments()):
            try:
                appt_time = datetime.strptime(a["dt"] + " " + a["tm"], "%Y-%m-%d %H:%M")
                if appt_time >= now:
                    future.append((i, a))
            except Exception:
                continue

        if not future:
            self.bot("No upcoming appointments to delete.")
            return

        self.bot("Which appointment to delete? Type its number:\n")
        for n, (i, a) in enumerate(future, 1):
            self.bot(f"  {n}. Dr {a['doc']} | {a['dt']} {a['tm']} | {a['hos']}")

        self._delete_candidates = future
        self.flow = "delete"

    def delete_flow(self, lower):
        text = lower.strip()
        if not text.isdigit():
            self.bot("⚠️ Please type the number of the appointment to delete.")
            return

        idx = int(text) - 1
        if idx < 0 or idx >= len(self._delete_candidates):
            self.bot(f"⚠️ Invalid number. Choose 1–{len(self._delete_candidates)}.")
            return

        real_index, a = self._delete_candidates[idx]
        if self.storage.delete_appointment(real_index):
            self.bot(f"✅ Deleted: Dr {a['doc']} on {a['dt']} at {a['tm']}.")
        else:
            self.bot("⚠️ Could not delete. Please try again.")

        self.flow = None
        self._delete_candidates = []

    # VIEW UPCOMING
    def show_appointments(self):
        self.storage.data = self.storage.load_data()
        now = datetime.now()

        future = []
        for i, a in enumerate(self.storage.get_appointments()):
            try:
                appt_time = datetime.strptime(a["dt"] + " " + a["tm"], "%Y-%m-%d %H:%M")
                if appt_time >= now:
                    future.append((i, a))
            except Exception as e:
                print(f"[View] Parse error: {e}")
                continue

        if not future:
            self.bot("📭 No upcoming appointments.")
            return

        future.sort(key=lambda x: datetime.strptime(x[1]["dt"] + " " + x[1]["tm"], "%Y-%m-%d %H:%M"))

        self.bot(f"📋 UPCOMING APPOINTMENTS ({len(future)} total)")
        for i, a in future:
            self.appointment_card(a, index=i)

    # REMINDER LIST
    def show_reminders(self):
        self.storage.data = self.storage.load_data()
        now = datetime.now()
        tomorrow = now + timedelta(days=1)

        upcoming = []
        for i, a in enumerate(self.storage.get_appointments()):
            try:
                appt_time = datetime.strptime(a["dt"] + " " + a["tm"], "%Y-%m-%d %H:%M")
                if now <= appt_time <= tomorrow:
                    upcoming.append((i, a))
            except Exception as e:
                print(f"[Reminder] Parse error: {e}")
                continue

        if not upcoming:
            self.bot("🔕 No appointments in the next 24 hours.")
            return

        upcoming.sort(key=lambda x: datetime.strptime(x[1]["dt"] + " " + x[1]["tm"], "%Y-%m-%d %H:%M"))

        self.bot(f"⏰ UPCOMING (NEXT 24 HOURS) — {len(upcoming)} appointment(s)")
        for i, a in upcoming:
            self.appointment_card(a, index=i)

# RUN 
if __name__ == "__main__":
    root = tk.Tk()
    ChatBotApp(root)
    root.mainloop()

