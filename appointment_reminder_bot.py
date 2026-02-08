import json
import os
import time
from datetime import datetime, timedelta


DATA_FILE = "appointments.json"


# -------------------- Storage Manager--------------------


class StorageManager:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []

    def save_data(self):
        with open(self.filename, "w") as file:
            json.dump(self.data, file, indent=4)

    def add_appointment(self, appointment):
        self.data.append(appointment)
        self.save_data()

    def get_all_appointments(self):
        return self.data


# -------------Appointment  --------------------


class Appointment:
    def __init__(self, doctor, specialty, hospital, date, time_slot):
        self.doctor = doctor
        self.specialty = specialty
        self.hospital = hospital
        self.date = date
        self.time_slot = time_slot

    def compress(self):
        return {
            "doc": self.doctor,
            "spec": self.specialty,
            "hos": self.hospital,
            "dt": self.date,
            "tm": self.time_slot
        }


# Reminder Engine


class ReminderEngine:
    def __init__(self, storage):
        self.storage = storage


    def check_reminders(self):
        today = datetime.now().date()
        sent = False

        for appt in self.storage.get_all_appointments():
            appt_date = datetime.strptime(appt["dt"], "%Y-%m-%d").date()
            if appt_date == today + timedelta(days=1):
                self.send_reminder(appt)
                sent = True

        if not sent:
            print("No reminders for today.")

    def send_reminder(self, appt):
        print("\n--- APPOINTMENT REMINDER ---")
        print(f"Doctor    : {appt['doc']}")
        print(f"Specialty : {appt['spec']}")
        print(f"Hospital  : {appt['hos']}")
        print(f"Date      : {appt['dt']}")
        print(f"Time      : {appt['tm']}")
        print("----------------------------\n")


# -------------------- Bot Controller --------------------


class AppointmentBot:
    def __init__(self):
        self.storage = StorageManager(DATA_FILE)
        self.reminder_engine = ReminderEngine(self.storage)
        self.specialties = [
            "General Medicine",
            "Cardiology",
            "Dermatology",
            "Orthopedics",
            "Neurology"
        ]

    def choose_specialty(self):
        print("\nAvailable Specialties:")
        for i, s in enumerate(self.specialties, 1):
            print(f"{i}. {s}")

        while True:
            choice = input("Select specialty number: ")
            if choice.isdigit() and 1 <= int(choice) <= len(self.specialties):
                return self.specialties[int(choice) - 1]
            print("Invalid choice.")

    def input_date(self):
        while True:
            value = input("Enter date (YYYY-MM-DD): ")
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return value
            except ValueError:
                print("Invalid date.")

    def input_time(self):
        while True:
            value = input("Enter time (HH:MM): ")
            try:
                datetime.strptime(value, "%H:%M")
                return value
            except ValueError:
                print("Invalid time.")

    def schedule_appointment(self):
        print("\n--- Schedule Appointment ---")

        specialty = self.choose_specialty()
        doctor = input("Doctor name: ").strip()
        hospital = input("Hospital name: ").strip()
        date = self.input_date()
        time_slot = self.input_time()

        appointment = Appointment(
            doctor, specialty, hospital, date, time_slot
        )

        self.storage.add_appointment(appointment.compress())
        print("Appointment scheduled successfully.")

    def view_appointments(self):
        print("\n--- Your Appointments ---")
        appointments = self.storage.get_all_appointments()

        if not appointments:
            print("No appointments found.")
            return

        for i, appt in enumerate(appointments, 1):
            print(f"\nAppointment {i}")
            print(f"Doctor    : {appt['doc']}")
            print(f"Specialty : {appt['spec']}")
            print(f"Hospital  : {appt['hos']}")
            print(f"Date      : {appt['dt']}")
            print(f"Time      : {appt['tm']}")

    def send_reminders(self):
        print("\nChecking reminders...")
        time.sleep(1)
        self.reminder_engine.check_reminders()

    def run(self):
        while True:
            print("\n==== APPOINTMENT REMINDER BOT ====")
            print("1. Schedule Appointment")
            print("2. View Appointments")
            print("3. Check Reminders")
            print("4. Exit")

            choice = input("Choose option: ")

            if choice == "1":
                self.schedule_appointment()
            elif choice == "2":
                self.view_appointments()
            elif choice == "3":
                self.send_reminders()
            elif choice == "4":
                print("Exiting.")
                break
            else:
                print("Invalid option.")



# -------------------- Entry Point --------------------

if __name__ == "__main__":
    bot = AppointmentBot()
    bot.run()
