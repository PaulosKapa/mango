import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import json

class NLPQuestionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Incident Report via Questions")
        self.root.geometry("850x700") # Increased size to accommodate more info
        self.root.resizable(False, False)

        self.backend_url = "http://127.0.0.1:5000"

        # --- Question Display Frame ---
        question_frame = tk.LabelFrame(root, text="Current Question", padx=15, pady=15)
        question_frame.pack(padx=20, pady=15, fill="x")

        self.question_label = tk.Label(question_frame, text="Click 'Start Conversation' to begin.", font=("Arial", 16, "bold"), wraplength=750, justify="left")
        self.question_label.pack(pady=10, anchor="w")

        # --- Answer Input Frame ---
        answer_frame = tk.LabelFrame(root, text="Your Answer", padx=15, pady=10)
        answer_frame.pack(padx=20, pady=10, fill="x")

        self.answer_entry = tk.Entry(answer_frame, width=60, font=("Arial", 14))
        self.answer_entry.pack(side=tk.LEFT, padx=5, pady=5, fill="x", expand=True)
        self.answer_entry.bind("<Return>", lambda event: self.submit_answer_wrapper()) # Allow pressing Enter to submit

        self.submit_button = tk.Button(answer_frame, text="Submit Answer", command=self.submit_answer_wrapper, font=("Arial", 12), bg="#007bff", fg="white")
        self.submit_button.pack(side=tk.RIGHT, padx=5)

        # --- Control Buttons ---
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)

        self.start_button = tk.Button(control_frame, text="Start New Conversation", command=self.start_conversation, font=("Arial", 12), bg="#28a745", fg="white")
        self.start_button.pack(side=tk.LEFT, padx=10)

        # --- Conversation History Frame ---
        history_frame = tk.LabelFrame(root, text="Conversation History", padx=10, pady=10)
        history_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.history_text_area = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, width=70, height=8, font=("Arial", 11), bg="#f8f9fa", fg="#333")
        self.history_text_area.pack(padx=5, pady=5, fill="both", expand=True)
        self.history_text_area.insert(tk.END, "Question and answers will appear here.\n")
        self.history_text_area.config(state=tk.DISABLED) # Make it read-only

        # --- Processed Results Display Frame ---
        results_frame = tk.LabelFrame(root, text="Real-time Processed Data", padx=10, pady=10)
        results_frame.pack(padx=20, pady=15, fill="both", expand=True)

        self.results_text_area = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, width=70, height=10, font=("Courier New", 11), bg="#e9ecef", fg="#333")
        self.results_text_area.pack(padx=5, pady=5, fill="both", expand=True)
        self.results_text_area.insert(tk.END, "Extracted data will update after each answer.")
        self.results_text_area.config(state=tk.DISABLED)

    def update_text_area(self, text_area, content, append=False):
        text_area.config(state=tk.NORMAL)
        if not append:
            text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, content)
        text_area.yview(tk.END) # Scroll to the bottom
        text_area.config(state=tk.DISABLED)

    def start_conversation(self):
        self.update_text_area(self.history_text_area, "Starting new conversation...\n")
        self.update_text_area(self.results_text_area, "Extracted data will update after each answer.")
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.config(state=tk.NORMAL)
        self.submit_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED) # Disable start button once conversation begins

        try:
            response = requests.get(f"{self.backend_url}/start_conversation")
            response.raise_for_status()
            data = response.json()
            if data["status"] == "in_progress":
                self.question_label.config(text=data["question"])
                self.update_text_area(self.history_text_area, f"Q: {data['question']}\n", append=True)
                self.answer_entry.focus_set()
            else:
                self.question_label.config(text="Error: Could not start conversation.")
                messagebox.showerror("Error", "Backend did not return a question to start.")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Could not connect to the Flask backend. Make sure it's running.")
            self.question_label.config(text="Connection Error. Check backend.")
            self.start_button.config(state=tk.NORMAL) # Re-enable start on connection error
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.question_label.config(text=f"Error: {e}")
            self.start_button.config(state=tk.NORMAL)

    def submit_answer_wrapper(self):
        # This wrapper prevents submission if the button is disabled
        if self.submit_button['state'] == tk.DISABLED:
            return
        self.submit_answer()

    def submit_answer(self):
        answer = self.answer_entry.get().strip()
        if not answer:
            messagebox.showwarning("Missing Answer", "Please provide an answer.")
            return

        # Add user's answer to history
        current_question_text = self.question_label.cget("text")
        self.update_text_area(self.history_text_area, f"A: {answer}\n\n", append=True)


        try:
            response = requests.post(
                f"{self.backend_url}/submit_answer",
                json={"answer": answer}
            )
            response.raise_for_status()
            data = response.json()

            # Update processed data
            if data.get("extracted_data"):
                self.update_text_area(self.results_text_area, json.dumps(data["extracted_data"], indent=2, ensure_ascii=False))
            else:
                self.update_text_area(self.results_text_area, "No data extracted yet or error in processing.", append=True)


            if data["status"] == "in_progress":
                self.question_label.config(text=data["question"])
                self.update_text_area(self.history_text_area, f"Q: {data['question']}\n", append=True)
                self.answer_entry.delete(0, tk.END)
                self.answer_entry.focus_set() # Keep focus on the answer entry
            elif data["status"] == "finished":
                self.question_label.config(text=data["question"])
                self.update_text_area(self.history_text_area, f"{data['question']}\n", append=True)
                self.answer_entry.config(state=tk.DISABLED)
                self.submit_button.config(state=tk.DISABLED)
                self.start_button.config(state=tk.NORMAL) # Re-enable start button
                messagebox.showinfo("Conversation Finished", "All questions answered! Check the processed data.")
            else: # Handle potential 'error' status from backend
                 messagebox.showerror("Backend Error", f"An error occurred on the backend: {data.get('error_details', 'Unknown error')}")
                 self.question_label.config(text="Backend Error during processing.")
                 self.answer_entry.config(state=tk.DISABLED)
                 self.submit_button.config(state=tk.DISABLED)

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Could not connect to the Flask backend. Make sure it's running.")
            self.question_label.config(text="Connection Error. Check backend.")
            self.answer_entry.config(state=tk.DISABLED)
            self.submit_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL) # Re-enable start on connection error
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.question_label.config(text=f"Error: {e}")
            self.answer_entry.config(state=tk.DISABLED)
            self.submit_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = NLPQuestionApp(root)
    root.mainloop()