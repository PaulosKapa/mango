import tkinter as tk
import pandas as pd
import spacy

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
    

root = tk.Tk()
root.title("Chatbot")

chat_log = tk.Text(root, height=25, width=50)
chat_log.pack()

# Show greeting as soon as window opens
chat_log.insert(tk.END, "Bot: Good morning, how can I help you? Please describe me what happened?\n")

entry = tk.Entry(root, width=60)
entry.pack(side=tk.LEFT)

questions = [
    "What is your plate registration number?",
    "What is your name?",
    "Where are you?",
    "Where would you like to go?"
]

columns = ["Incident Description", "Reg. number", "Name", "Location", "Destination"]

current_question = 0  # track which question to ask
answers = {}

def save_to_excel(data):
    df = pd.DataFrame([data])
    df.to_excel("chat_answers.xlsx", index=False)
    print("Saved answers to chat_answers.xlsx")

def on_enter(event):
    global current_question
    user_msg = entry.get().strip()
    if not user_msg:
        return
    
    chat_log.insert(tk.END, "You: " + user_msg + "\n")


    if current_question == 0:
        # Αποθήκευσε την περιγραφή περιστατικού
        answers[columns[0]] = user_msg

        # Κατάταξε το περιστατικό με spaCy
        category = classify_incident(user_msg)
        answers["Incident Category"] = category

        chat_log.insert(tk.END, f"Bot: Καταχώρησα το περιστατικό ως: {category}\n")

        # Ρώτα πρώτη επίσημη ερώτηση
        chat_log.insert(tk.END, "Bot: " + questions[0] + "\n")
        current_question += 1

    else:
        # Αποθήκευσε απάντηση στην κατάλληλη στήλη
        answers[columns[current_question]] = user_msg

        if current_question < len(questions):
            chat_log.insert(tk.END, "Bot: " + questions[current_question] + "\n")
            current_question += 1
        else:
            chat_log.insert(tk.END, "Bot: Thank you for the info.\n")
            save_to_excel(answers)


    entry.delete(0, tk.END)

entry.bind("<Return>", on_enter)

send_btn = tk.Button(root, text="Send", command=lambda: on_enter(None))
send_btn.pack(side=tk.LEFT)

root.mainloop()
