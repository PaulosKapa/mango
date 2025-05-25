import customtkinter as ctk
from PIL import Image, ImageTk
import os
from customtkinter import CTkImage

# Initialize theme
ctk.set_appearance_mode("Dark")  # Light, Dark, System
ctk.set_default_color_theme("dark-blue")  # blue, green, dark-blue, etc.

# Create main window
window = ctk.CTk()
window.title("🍍 ANANAS Bot")
window.geometry("800x500")

# Placeholder text
placeholder_text = "Tell us your issue..."

# --- Chat Textbox ---
chat_window = ctk.CTkTextbox(
    window,
    wrap="word",
    font=("Segoe UI", 14),
    state="disabled",
    corner_radius=10,
    width=760,
    height=380
)
chat_window.place(x=20, y=20)

# Top frame with same bg color as chat window
top_frame_bg = chat_window.cget("fg_color")
  # get chat window bg color

top_frame = ctk.CTkFrame(window, corner_radius=0, width=760, height=100, fg_color=top_frame_bg, border_width=0 )
top_frame.place(x=250, y=50)

# Load image
img_path = "pineapple.png"  # replace with your image path
if os.path.exists(img_path):
    pil_img = Image.open(img_path).resize((60, 80), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(pil_img)
    img_label = ctk.CTkLabel(top_frame, image=img, text="")
    img_label.image = img
    img_label.pack(side="left", padx=10, pady=10)
else:
    img_label = None

# Big, centered, calligraphy style label
calligraphy_font = ("Segoe Script", 24)  # example calligraphy font, adjust if you want

text_label = ctk.CTkLabel(
    top_frame,
    text="We are here -\nfor you",
    font=calligraphy_font,
    justify="center"
)
text_label.pack(side="left", expand=True, fill="both", padx=10, pady=10)

# Insert initial message in chat window (below top_frame visually)
chat_window.configure(state="normal")
chat_window.insert("end", "\n\n")  # add some spacing under top_frame
chat_window.configure(state="disabled")

# Flag to hide top_frame only once
frame_hidden = False

# --- Functions ---
def my_response(user_input):
    return (
        "Παρακαλώ καταθέστε τα παρακάτω στοιχεία:\n"
        "1. Ποιος είναι ο αριθμός κυκλοφορίας\n"
        "2. Ποιο είναι το όνομά σας\n"
        "3. Περιγράψτε το συμβάν\n"
        "4. Σε ποια τοποθεσία βρίσκεστε\n"
        "5. Ποιος είναι ο τελικός προορισμός σας\n"
    )

def my_message():
    global frame_hidden
    user_input = entry.get()
    if user_input.strip() == "" or user_input == placeholder_text:
        return

    if not frame_hidden:
        top_frame.place_forget()
        frame_hidden = True

    entry.delete(0, "end")
    chat_window.configure(state="normal")
    chat_window.insert("end", f"\n{user_input}\n")
    chat_window.insert("end", f"{my_response(user_input)}\n")
    chat_window.configure(state="disabled")
    chat_window.yview("end")

# --- Entry & Send Button ---
entry = ctk.CTkEntry(window, font=("Segoe UI", 14), placeholder_text=placeholder_text, width=700, height=70, corner_radius=20)
entry.place(x=50, y=410)

entry.bind("<Return>", lambda e: my_message())

# Optional icon for send button
icon_path = "button.png"
if os.path.exists(icon_path):
    pil_img = Image.open(icon_path).resize((15, 15), Image.Resampling.LANCZOS)
    ctk_img = CTkImage(light_image=pil_img, dark_image=pil_img, size=(25, 25))
    send_button = ctk.CTkButton(
        window,
        image=ctk_img,
        text="",
        width=35,
        height=35,
        command=my_message,
        
    )
else:
    send_button = ctk.CTkButton(window, text="Αποστολή", command=my_message, width=35, height=35)

send_button.place(x=680, y=435)

# Start the application
window.mainloop()
