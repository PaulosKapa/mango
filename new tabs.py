import tkinter as tk
import spacy
import sqlite3

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def classify_incident(text):
    doc = nlp(text.lower())

    accident_keywords = {"accident", "crash", "collision", "ατύχημα", "σύγκρουση"}
    road_assist_keywords = {"road assistance", "breakdown", "tow", "οδική βοήθεια", "βλάβη"}

    tokens = {token.text for token in doc}

    if tokens.intersection(accident_keywords):
        return "Accident Care"
    elif tokens.intersection(road_assist_keywords):
        return "Road Assistance"
    else:
        return "Other"

# Set up SQLite
conn = sqlite3.connect('chat_data.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    reg_number TEXT,
    name TEXT,
    location TEXT,
    incident_description TEXT,
    destination TEXT,
    "Possible malfunction" TEXT,
    "Possible resolution" TEXT,
    "Recommented autorepair-shop" TEXT,
    "Is final destination within the country?" TEXT,
    "Was delay-voucher used?" TEXT,
    "Was a link for geolocation sent?" TEXT,
    "Was a declaration needed?" TEXT,
    "Is a fast track case?" TEXT,
    "Is it a fraud?" TEXT,
    "Communication quality" TEXT,
    "Tags/Short summary" TEXT
)
''')
conn.commit()

def save_to_db(data):
    cursor.execute('''
        INSERT INTO incidents (
            category,
            reg_number,
            name,
            location,
            incident_description,
            destination,
            "Possible malfunction",
            "Possible resolution",
            "Recommented autorepair-shop",
            "Is final destination within the country?",
            "Was delay-voucher used?",
            "Was a link for geolocation sent?",
            "Was a declaration needed?",
            "Is a fast track case?",
            "Is it a fraud?",
            "Communication quality",
            "Tags/Short summary"
     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("Incident Category", ""),
        data.get("Reg. number", ""),
        data.get("Name", ""),
        data.get("Location", ""),
        data.get("Incident Description", ""),
        data.get("Destination", ""),
        data.get("Possible malfunction", ""),
        data.get("Possible resolution", ""),
        data.get("Recommented autorepair-shop", ""),
        data.get("Is final destination within the country?", ""),
        data.get("Was delay-voucher used?", ""),
        data.get("Was a link for geolocation sent?", ""),
        data.get("Was a declaration needed?", ""),
        data.get("Is a fast track case?", ""),
        data.get("Is it a fraud?", ""),
        data.get("Communication quality", ""),
        data.get("Tags/Short summary", "")
    ))
    conn.commit()
    print("Saved answers to database chat_data.db")

# GUI setup
root = tk.Tk()
root.title("Chatbot")

chat_log = tk.Text(root, height=25, width=70)
chat_log.pack()

entry = tk.Entry(root, width=60)

questions = [
    "Please describe what happened:",
    "What is your plate registration number?",
    "What is your name?",
    "Where are you?",
    "Where would you like to go?",
    "Possible malfunction?",
    "Possible resolution?",
    "Recommented autorepair-shop?",
    "Is final destination within the country? (Yes/No)",
    "Was delay-voucher used? (Yes/No)",
    "Was a link for geolocation sent? (Yes/No)",
    "Was a declaration needed? (Yes/No)",
    "Is it a fast track case? (Yes/No)",
    "Is it a fraud? (Yes/No)",
    "Communication quality?",
    "Tags/Short summary?"
]

columns = [
    "Incident Description",
    "Reg. number",
    "Name",
    "Location",
    "Destination",
    "Possible malfunction",
    "Possible resolution",
    "Recommented autorepair-shop",
    "Is final destination within the country?",
    "Was delay-voucher used?",
    "Was a link for geolocation sent?",
    "Was a declaration needed?",
    "Is a fast track case?",
    "Is it a fraud?",
    "Communication quality",
    "Tags/Short summary"
]

current_question = -1  # Start before the first question (initial yes/no)
answers = {}

def ask_next_question():
    global current_question
    current_question += 1
    if current_question < len(questions):
        chat_log.insert(tk.END, "Bot: " + questions[current_question] + "\n")
        entry.pack(side=tk.LEFT)
        entry.focus()
    else:
        chat_log.insert(tk.END, "Bot: Thank you for the info. Goodbye!\n")
        save_to_db(answers)
        entry.config(state='disabled')
        yes_button.config(state='disabled')
        no_button.config(state='disabled')

def on_yes_no(answer):
    global current_question
    chat_log.insert(tk.END, f"You: {answer}\n")
    yes_button.pack_forget()
    no_button.pack_forget()

    if answer == "No":
        chat_log.insert(tk.END, "Bot: Okay, have a nice day!\n")
        entry.config(state='disabled')
        return
    else:
        current_question = 0
        chat_log.insert(tk.END, "Bot: Please describe what happened:\n")
        entry.pack(side=tk.LEFT)
        entry.focus()

def on_enter(event=None):
    global current_question
    if current_question < 0:
        return
    user_msg = entry.get().strip()
    if not user_msg:
        return
    chat_log.insert(tk.END, "You: " + user_msg + "\n")

    answers[columns[current_question]] = user_msg

    if current_question == 0:
        category = classify_incident(user_msg)
        answers["Incident Category"] = category

    entry.delete(0, tk.END)
    ask_next_question()

chat_log.insert(tk.END, "Bot: Good morning, do you need help? (Yes/No)\n")

yes_button = tk.Button(root, text="Yes", command=lambda: on_yes_no("Yes"))
no_button = tk.Button(root, text="No", command=lambda: on_yes_no("No"))
yes_button.pack(side=tk.LEFT)
no_button.pack(side=tk.LEFT)

entry.bind("<Return>", on_enter)

root.mainloop()
conn.close()
