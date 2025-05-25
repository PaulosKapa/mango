import tkinter as tk
import pandas as pd

root = tk.Tk()
root.title("Chatbot")

chat_log = tk.Text(root, height=25, width=50)
chat_log.pack()

# Show greeting as soon as window opens
chat_log.insert(tk.END, "Bot: Good morning, how can I help you?\n")

entry = tk.Entry(root, width=60)
entry.pack(side=tk.LEFT)

questions = [
    "What is your plate registration number?",
    "What is your name?",
    "What happened?",
    "Where are you?",
    "Where would you like to go?"
]

columns = ["Reg. number", "Name", "Incident", "Location", "Destination"]

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
        # Ask first question
        chat_log.insert(tk.END, "Bot: " + questions[0] + "\n")
        current_question = 1
    else:
        # Save the answer to previous question
        answers[columns[current_question - 1]] = user_msg

        if current_question < len(questions):
            # Ask next question
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
