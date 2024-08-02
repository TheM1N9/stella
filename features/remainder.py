from datetime import datetime
import json
import time
from threading import Thread

from features.speak import speak

# Initialize reminders list
reminders = []

def create_reminder(reminder_text, reminder_time):
    reminders.append({"text": reminder_text, "time": reminder_time})
    save_reminders()
    return f"Reminder set for {reminder_time}: {reminder_text}"

def list_reminders():
    if not reminders:
        return "You have no reminders."
    response = "Your reminders are:\n"
    for idx, reminder in enumerate(reminders, 1):
        response += f"{idx}. {reminder['text']} at {reminder['time']}\n"
    return response

def check_reminders():
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        for reminder in reminders:
            if reminder["time"] == now:
                speak(f"Reminder: {reminder['text']}")
                reminders.remove(reminder)
                save_reminders()
        time.sleep(60)  # Check every minute

def save_reminders():
    with open("memory/reminders.json", "w") as file:
        json.dump(reminders, file)

def load_reminders():
    global reminders
    try:
        with open("memory/reminders.json", "r") as file:
            reminders = json.load(file)
    except FileNotFoundError:
        reminders = []

def start_reminder_thread():
    reminder_thread = Thread(target=check_reminders, daemon=True)
    reminder_thread.start()

if __name__ == "__main__":
    start_reminder_thread()
    load_reminders()
    create_reminder("testing remainder", "00:25")