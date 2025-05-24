import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import json

BASE_URL = "http://127.0.0.1:5000"  # adjust if your Flask backend runs elsewhere

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Incident Conversation & Admin SQL")

        # Conversation UI
        tk.Label(self, text="Conversation").grid(row=0, column=0, sticky="w", pady=5)
        tk.Button(self, text="Start Conversation", command=self.start_conversation).grid(row=0, column=1, sticky="ew")

        tk.Label(self, text="Status:").grid(row=1, column=0, sticky="w")
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var).grid(row=1, column=1, sticky="w")

        tk.Label(self, text="Question:").grid(row=2, column=0, sticky="nw")
        self.question_text = tk.Text(self, height=3, width=60, wrap="word")
        self.question_text.grid(row=2, column=1, sticky="ew")
        self.question_text.config(state="disabled")

        tk.Label(self, text="Your Answer:").grid(row=3, column=0, sticky="nw")
        self.answer_entry = tk.Text(self, height=3, width=60)
        self.answer_entry.grid(row=3, column=1, sticky="ew")

        tk.Button(self, text="Submit Answer", command=self.submit_answer).grid(row=4, column=1, sticky="e", pady=5)

        tk.Label(self, text="Extracted Data:").grid(row=5, column=0, sticky="nw")
        self.extracted_text = scrolledtext.ScrolledText(self, height=10, width=60)
        self.extracted_text.grid(row=5, column=1, sticky="ew")
        self.extracted_text.config(state="disabled")

        # Separator
        tk.Frame(self, height=2, bd=1, relief="sunken").grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        # Admin SQL UI
        tk.Label(self, text="Admin SQL Executor").grid(row=7, column=0, sticky="w")
        self.sql_input = scrolledtext.ScrolledText(self, height=5, width=60)
        self.sql_input.grid(row=8, column=0, columnspan=2, sticky="ew")

        tk.Button(self, text="Execute SQL", command=self.execute_sql).grid(row=9, column=1, sticky="e", pady=5)

        tk.Label(self, text="SQL Result:").grid(row=10, column=0, sticky="nw")
        self.sql_result = scrolledtext.ScrolledText(self, height=10, width=60)
        self.sql_result.grid(row=10, column=1, sticky="ew")
        self.sql_result.config(state="disabled")

        self.columnconfigure(1, weight=1)

    def start_conversation(self):
        try:
            res = requests.get(f"{BASE_URL}/start_conversation")
            data = res.json()
            self.status_var.set(data.get("status", ""))
            self._set_text(self.question_text, data.get("question", ""))
            self._set_text(self.extracted_text, json.dumps(data.get("extracted_data", {}), indent=2))
            self.answer_entry.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start conversation:\n{e}")

    def submit_answer(self):
        answer = self.answer_entry.get("1.0", tk.END).strip()
        if not answer:
            messagebox.showwarning("Input needed", "Please enter your answer before submitting.")
            return
        try:
            res = requests.post(f"{BASE_URL}/submit_answer", json={"answer": answer})
            data = res.json()
            self.status_var.set(data.get("status", ""))
            self._set_text(self.question_text, data.get("question", ""))
            self._set_text(self.extracted_text, json.dumps(data.get("extracted_data", {}), indent=2))
            self.answer_entry.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit answer:\n{e}")

    def execute_sql(self):
        sql_code = self.sql_input.get("1.0", tk.END).strip()
        if not sql_code:
            messagebox.showwarning("Input needed", "Please enter SQL code to execute.")
            return
        try:
            res = requests.post(f"{BASE_URL}/admin/sql", json={"sql": sql_code})
            data = res.json()
            if data.get("status") == "error":
                self._set_text(self.sql_result, f"Error: {data.get('error')}")
            else:
                self._set_text(self.sql_result, json.dumps(data.get("results", []), indent=2))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute SQL:\n{e}")

    def _set_text(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.config(state="disabled")


if __name__ == "__main__":
    app = App()
    app.mainloop()
