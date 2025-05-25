import customtkinter as ctk
import requests
from PIL import Image, ImageTk
import os
from customtkinter import CTkImage

# Initialize theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class SimpleNLPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🍍 ANANAS Simple Bot")
        self.root.geometry("800x500")
        self.backend_url = "http://127.0.0.1:5000"

        self.placeholder_text = "Πείτε μας τι συνέβη..."

        # Chat display
        self.chat_window = ctk.CTkTextbox(
            root, wrap="word", font=("Segoe UI", 14),
            state="disabled", corner_radius=10, width=760, height=300
        )
        self.chat_window.place(x=20, y=20)

        # Top banner (image + title)
        self.top_frame = ctk.CTkFrame(
            root, corner_radius=0, width=760, height=100,
            fg_color=self.chat_window.cget("fg_color"), border_width=0
        )
        self.top_frame.place(x=250, y=50)

        # Load image (optional)
        img_path = "pineapple.png"
        if os.path.exists(img_path):
            pil_img = Image.open(img_path).resize((60, 80), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(pil_img)
            img_label = ctk.CTkLabel(self.top_frame, image=img, text="")
            img_label.image = img
            img_label.pack(side="left", padx=10, pady=10)

        # Title text
        text_label = ctk.CTkLabel(
            self.top_frame,
            text="We are here -\nfor you",
            font=("Segoe Script", 24),
            justify="center"
        )
        text_label.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        self.chat_window.configure(state="normal")
        self.chat_window.insert("end", "\n\n")
        self.chat_window.configure(state="disabled")

        self.frame_hidden = False

        # Entry field
        self.entry = ctk.CTkEntry(
            root, font=("Segoe UI", 14),
            placeholder_text=self.placeholder_text,
            width=700, height=70, corner_radius=20
        )
        self.entry.place(x=20, y=340)
        self.entry.bind("<Return>", lambda e: self.send_answer())

        # Send button
        icon_path = "button.png"
        if os.path.exists(icon_path):
            pil_icon = Image.open(icon_path).resize((15, 15), Image.Resampling.LANCZOS)
            ctk_icon = CTkImage(light_image=pil_icon, dark_image=pil_icon, size=(25, 25))
            self.send_button = ctk.CTkButton(
                root, image=ctk_icon, text="", width=35, height=35,
                command=self.send_answer
            )
        else:
            self.send_button = ctk.CTkButton(
                root, text="Αποστολή", command=self.send_answer,
                width=100, height=40
            )
        self.send_button.place(x=730, y=338)

        # Begin conversation with AI
        self.start_conversation()

    def update_chat(self, text, append=True):
        self.chat_window.configure(state="normal")
        if append:
            self.chat_window.insert("end", text + "\n")
        else:
            self.chat_window.delete("1.0", "end")
            self.chat_window.insert("end", text + "\n")
        self.chat_window.configure(state="disabled")
        self.chat_window.yview("end")

    def start_conversation(self):
        try:
            resp = requests.get(f"{self.backend_url}/start_conversation")
            resp.raise_for_status()
            data = resp.json()
            question = data.get("question", "Δεν λάβαμε ερώτηση από το σύστημα.")
            self.update_chat(f"🤖: {question}", append=False)
        except Exception as e:
            self.update_chat(f"❌ Σφάλμα κατά την έναρξη: {e}", append=False)

    def send_answer(self):
        answer = self.entry.get().strip()
        if not answer or answer == self.placeholder_text:
            return

        if not self.frame_hidden:
            self.top_frame.place_forget()
            self.frame_hidden = True

        self.update_chat(f"👤: {answer}")
        self.entry.delete(0, "end")

        try:
            resp = requests.post(
                f"{self.backend_url}/submit_answer",
                json={"answer": answer}
            )
            resp.raise_for_status()
            data = resp.json()

            next_q = data.get("question", "")
            status = data.get("status", "")
            if status == "finished":
                self.update_chat("🎉 Όλες οι ερωτήσεις έχουν ολοκληρωθεί.")
            else:
                self.update_chat(f"🤖: {next_q}")
        except Exception as e:
            self.update_chat(f"❌ Σφάλμα κατά την αποστολή: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = SimpleNLPApp(root)
    root.mainloop()
