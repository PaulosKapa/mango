#This is the watson api file


import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # Place this at the top of the Python script
from tkinter import scrolledtext

import os
import json
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai import Credentials

API_KEY = "SL2Ug6gQ9pVZV12JWtX_y7ZWyJQCvLY8EubR84iZj4cP"  # os.getenv("WM_API_KEY", "YOUR_IBM_CLOUD_API_KEY_HERE")
SERVICE_URL = "https://us-south.ml.cloud.ibm.com"  # os.getenv("WM_URL", "YOUR_WATSONX_AI_SERVICE_URL_HERE")
PROJECT_ID = "f406bc13-a60d-4073-9e52-d99565d73dc4"  # os.getenv("WM_PROJECT_ID", "YOUR_WATSONX_AI_PROJECT_ID_HERE")

MODEL_ID = "meta-llama/llama-4-maverick-17b-128e-instruct-fp8"  # Or another suitable model

GEN_PARAMS = {
    GenParams.DECODING_METHOD: DecodingMethods.GREEDY,  # Or DecodingMethods.SAMPLE for more creativity
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.MAX_NEW_TOKENS: 200,  # Max length of the generated response
    GenParams.REPETITION_PENALTY: 1.0,
    GenParams.TEMPERATURE: 0.1,  # Lower temperature for more accurate responses
}
try:
    credentials = Credentials(
        api_key=API_KEY,
        url=SERVICE_URL
    )

    # Initialize the ModelInference object
    # For conversational context, you typically send the entire dialog history in the prompt.
    # watsonx.ai foundation models don't have a built-in 'chat' session like Gemini's SDK,
    # so you manage the history yourself by concatenating it into the prompt.
    model_inference = ModelInference(
        model_id=MODEL_ID,
        params=GEN_PARAMS,
        credentials=credentials,
        project_id=PROJECT_ID
    )
    print(f"Watsonx.ai ModelInference for '{MODEL_ID}' initialized.")

except Exception as e:
    print(f"Error initializing watsonx.ai: {e}")
    print("Please ensure your API Key, URL, and Project ID are correct and accessible.")
    exit(1)


chat_history = []
######


def format_prompt_from_history(user_input):
    system_prompt = (
        "Είσαι βοηθός ασφαλιστικής εταιρείας που θέλεις να εξυπηρετήσεις των πελάτη σου"
        "Είσαι ένας σύντομος, επαγγελματικός και ευγενικός Ασφαλιστικός Βοηθός. "
        "Απαντάς πάντα στα ελληνικά. Μην επαναλαμβάνεις την ερώτηση. "
        "Μην ξεκινάς με γενικά μηνύματα όπως 'Μήπως χρειάζεσαι βοήθεια...'. "
        "Απάντα άμεσα και περιεκτικά με νέες, σχετικές πληροφορίες."
        "Να μην επαναλαμβάνεις το κειμενό σου."
        "Μην κάνεις πάνω απο δύο ερωτήσεις τον χρήστη."
        
   
        
    )

    conversation = system_prompt + "\n\n"

    for entry in chat_history:
        if entry["role"] == "user":
            conversation += f"Ερώτηση: {entry['text']}\n"
        elif entry["role"] == "model":
            conversation += f"Απάντηση: {entry['text']}\n"

    conversation += f"Ερώτηση: {user_input}\nΑπάντηση:"

    return conversation




def send_message_to_watsonx_ai(user_input):
    global chat_history

    try:
        # 1. Format the user's input into a single prompt for the LLM
        full_prompt = format_prompt_from_history(user_input)

        # 2. Call the watsonx.ai model
        result = model_inference.generate_text(prompt=full_prompt)
        watsonx_response_text = result.strip()

        # 3. Update the conversation history
        chat_history.append({"role": "user", "text": user_input})
        chat_history.append({"role": "model", "text": watsonx_response_text})

        return watsonx_response_text

    except Exception as e:
        print(f"Error calling watsonx.ai model: {e}")
        return "Συγνώμη, έχω πρόβλημα σύνδεσης με το watsonx.ai αυτή τη στιγμή."





def my_message():
 #i made it like this in order to disable the front end 
    user_input = entry.get()
    if user_input.strip() == "":
        return
    entry.delete(0, END)

    chat_window.configure(state='normal')
    chat_window.insert(END, f"\n{user_input}   \n", 'right')
    response = send_message_to_watsonx_ai(user_input)

    chat_window.insert(END, f"   {response}\n", 'left')
    chat_window.configure(state='disabled')
    chat_window.yview(END)


def clear_placeholder(event):
    if entry.get() == placeholder_text:
        entry.delete(0, END)
        entry.config(foreground='black')

def set_placeholder():
    if not entry.get():
        entry.insert(0, placeholder_text)
        entry.config(foreground='grey')

window = ttk.Window(themename="minty")
window.title("Ασφαλιστικός Βοηθός")
window.geometry("800x500")
window.configure(bg="#e6e0f8")

chat_window = scrolledtext.ScrolledText(window, wrap="word", state='disabled', font=("Segoe UI", 12, "italic"))
chat_window.place(x=20, y=20, width=760, height=380)

chat_window.tag_configure('right', justify='right', foreground='#1a237e', font=("Segoe UI", 12, "bold"))
chat_window.tag_configure('left', justify='left', foreground='#4b0082', font=("Segoe UI", 12))

placeholder_text = "Ρώτα οτιδήποτε!"
entry = ttk.Entry(window, font=("Segoe UI", 12), bootstyle="info")
entry.place(x=100, y=420, width=500, height=35)
entry.insert(0, placeholder_text)
entry.config(foreground='grey')

entry.bind("<FocusIn>", clear_placeholder)
entry.bind("<FocusOut>", lambda e: set_placeholder())
entry.bind("<Return>", lambda e: my_message())


send_button = ttk.Button(window, text="Αποστολή", bootstyle="success", command=my_message)
send_button.place(x=660, y=420, width=95, height=35)

chat_window.configure(state='normal')
chat_window.insert(END, f"\n   Γεια σας! Είμαι ο βοηθός ασφαλειών σας. Πώς μπορώ να σας βοηθήσω σήμερα;\n\n", 'left')
chat_window.configure(state='disabled')

window.mainloop()