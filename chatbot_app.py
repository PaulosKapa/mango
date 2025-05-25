import customtkinter as ctk
from PIL import Image, ImageTk
import os
from customtkinter import CTkImage
import json # Not strictly needed but good practice for API responses if we had them

# Watsonx.ai Imports
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai import Credentials

# --- Watsonx.ai Configuration (from the first file) ---
# IMPORTANT: For production, use environment variables for API_KEY, SERVICE_URL, and PROJECT_ID.
# Example: API_KEY = os.getenv("WM_API_KEY", "YOUR_IBM_CLOUD_API_KEY_HERE")
API_KEY = "SL2Ug6gQ9pVZV12JWtX_y7ZWyJQCvLY8EubR84iZj4cP"
SERVICE_URL = "https://us-south.ml.cloud.ibm.com"
PROJECT_ID = "f406bc13-a60d-4073-9e52-d99565d73dc4"

MODEL_ID = "meta-llama/llama-4-maverick-17b-128e-instruct-fp8"

GEN_PARAMS = {
    GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.MAX_NEW_TOKENS: 200,
    GenParams.REPETITION_PENALTY: 1.0,
    GenParams.TEMPERATURE: 0.1,
}

# Initialize theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class SimpleNLPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🍍 ANANAS Simple Bot")
        self.root.geometry("800x500")

        # Watsonx.ai Model Initialization
        self.model_inference = None
        self._initialize_watsonx_ai()

        # Chat history for maintaining context
        self.chat_history = []

        # Placeholder text
        self.placeholder_text = "Tell us your issue..."

        # --- Chat Textbox ---
        self.chat_window = ctk.CTkTextbox(
            root,
            wrap="word",
            font=("Segoe UI", 14),
            state="disabled",
            corner_radius=10,
            width=760,
            height=300
        )
        self.chat_window.place(x=20, y=20)

        # Top frame with same bg color as chat window
        # Get computed foreground color to match the textbox background for the frame
        # This can be tricky with CTkTextbox's internal color logic.
        # A safer bet might be to pick a consistent color or ensure theme handles it.
        # For now, let's try to get a reasonable default or a known dark color.
        # The CTkTextbox 'fg_color' is usually its background color.
        top_frame_bg = self.chat_window.cget("fg_color")[0] if isinstance(self.chat_window.cget("fg_color"), tuple) else self.chat_window.cget("fg_color")
        if top_frame_bg == 'transparent': # Fallback for transparent or tricky defaults
            top_frame_bg = ctk.ThemeManager.theme['CTkFrame']['fg_color'][0] if ctk.get_appearance_mode() == "Dark" else ctk.ThemeManager.theme['CTkFrame']['fg_color'][1]


        self.top_frame = ctk.CTkFrame(
            root,
            corner_radius=0,
            width=760,
            height=100,
            fg_color=top_frame_bg,
            border_width=0
        )
        self.top_frame.place(x=20, y=20)

        # Load image
        img_path = "pineapple.png"
        if os.path.exists(img_path):
            try:
                pil_img = Image.open(img_path).resize((60, 80), Image.Resampling.LANCZOS)
                # customtkinter expects CTkImage for buttons/labels
                self.app_logo_image = CTkImage(light_image=pil_img, dark_image=pil_img, size=(60, 80))
                img_label = ctk.CTkLabel(self.top_frame, image=self.app_logo_image, text="")
                img_label.pack(side="left", padx=10, pady=10)
            except Exception as e:
                print(f"Error loading pineapple.png: {e}")
                # Fallback or indicate image missing
                ctk.CTkLabel(self.top_frame, text="🍍", font=("Segoe UI Emoji", 40)).pack(side="left", padx=10, pady=10)
        else:
            print("pineapple.png not found. Showing default emoji.")
            ctk.CTkLabel(self.top_frame, text="🍍", font=("Segoe UI Emoji", 40)).pack(side="left", padx=10, pady=10)


        # Calligraphy label
        calligraphy_font = ("Segoe Script", 24)
        text_label = ctk.CTkLabel(
            self.top_frame,
            text="We are here -\nfor you",
            font=calligraphy_font,
            justify="center"
        )
        text_label.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        # Flag to hide top frame once first message sent
        self.frame_hidden = False

        # --- Entry & Send ---
        self.entry = ctk.CTkEntry(
            root,
            font=("Segoe UI", 14),
            placeholder_text=self.placeholder_text,
            width=700,
            height=40,
            corner_radius=20
        )
        self.entry.place(x=20, y=340) # Adjusted position for chat window to be larger
        self.entry.bind("<Return>", lambda e: self.send_answer())

        # Send button
        icon_path = "button.png"
        if os.path.exists(icon_path):
            try:
                pil_icon = Image.open(icon_path).resize((25, 25), Image.Resampling.LANCZOS) # Increased size for better visibility
                ctk_icon = CTkImage(light_image=pil_icon, dark_image=pil_icon, size=(25, 25))
                self.send_button = ctk.CTkButton(
                    root,
                    image=ctk_icon,
                    text="",
                    width=40, # Adjusted width to match icon
                    height=40, # Adjusted height to match icon
                    command=self.send_answer
                )
            except Exception as e:
                print(f"Error loading button.png: {e}")
                self.send_button = ctk.CTkButton(
                    root,
                    text="Send",
                    command=self.send_answer,
                    width=100,
                    height=40
                )
        else:
            print("button.png not found. Showing default text button.")
            self.send_button = ctk.CTkButton(
                root,
                text="Send",
                command=self.send_answer,
                width=100,
                height=40
            )
        self.send_button.place(x=730, y=338) # Adjusted position for chat window to be larger

        # Start conversation with initial bot message
        self.start_conversation()

    def _initialize_watsonx_ai(self):
        """Initializes the Watsonx.ai ModelInference object."""
        try:
            credentials = Credentials(
                api_key=API_KEY,
                url=SERVICE_URL
            )
            self.model_inference = ModelInference(
                model_id=MODEL_ID,
                params=GEN_PARAMS,
                credentials=credentials,
                project_id=PROJECT_ID
            )
            print(f"Watsonx.ai ModelInference for '{MODEL_ID}' initialized.")
        except Exception as e:
            print(f"Error initializing watsonx.ai: {e}")
            self.model_inference = None # Ensure it's None if init fails
            # Provide a message to the user that the service is unavailable
            self.update_chat(f"Error: Could not connect to watsonx.ai. Please check API Key, URL, and Project ID. {e}", append=False)


    def format_prompt_from_history(self, user_input):
        """
        Formats the conversation history into a single prompt for the LLM.
        Includes a system prompt for the bot's persona.
        """
        system_prompt = (
            "Είσαι βοηθός ασφαλιστικής εταιρείας που θέλεις να εξυπηρετήσεις τον πελάτη σου.\n"
            "Είσαι ένας σύντομος, επαγγελματικός και ευγενικός Ασφαλιστικός Βοηθός. \n"
            "Απαντάς πάντα στα ελληνικά. Μην επαναλαμβάνεις την ερώτηση. \n"
            "Μην ξεκινάς με γενικά μηνύματα όπως 'Μήπως χρειάζεσαι βοήθεια...'. \n"
            "Απάντα άμεσα και περιεκτικά με νέες, σχετικές πληροφορίες.\n"
            "Να μην επαναλαμβάνεις το κείμενό σου.\n"
            "Μην κάνεις πάνω από δύο ερωτήσεις τον χρήστη.\n"
        )

        conversation = system_prompt + "\n\n"

        # Build the conversation history
        for entry in self.chat_history:
            if entry["role"] == "user":
                conversation += f"Ερώτηση: {entry['text']}\n"
            elif entry["role"] == "model":
                conversation += f"Απάντηση: {entry['text']}\n"

        conversation += f"Ερώτηση: {user_input}\nΑπάντηση:"
        return conversation

    def send_message_to_watsonx_ai(self, user_input):
        """
        Sends the formatted prompt to the watsonx.ai model and returns the response.
        """
        if not self.model_inference:
            return "Συγνώμη, το watsonx.ai δεν είναι διαθέσιμο αυτή τη στιγμή."

        try:
            full_prompt = self.format_prompt_from_history(user_input)
            result = self.model_inference.generate_text(prompt=full_prompt)
            watsonx_response_text = result.strip()
            return watsonx_response_text
        except Exception as e:
            print(f"Error calling watsonx.ai model: {e}")
            return "Συγνώμη, έχω πρόβλημα με την επικοινωνία με το watsonx.ai αυτή τη στιγμή."


    def update_chat(self, text, is_user=False):
        """
        Updates the chat window with new text, handling user vs. bot alignment.
        """
        self.chat_window.configure(state="normal")

        # Add tags for user (right) and bot (left) alignment
        if is_user:
            self.chat_window.tag_configure('user', justify='right', text_color='#E0E0E0') # Light grey for user in dark theme
            self.chat_window.insert("end", text + "\n", 'user')
        else:
            self.chat_window.tag_configure('bot', justify='left', text_color='#ADD8E6') # Light blue for bot in dark theme
            self.chat_window.insert("end", text + "\n", 'bot')

        self.chat_window.configure(state="disabled")
        self.chat_window.yview("end")

    def start_conversation(self):
        """
        Initializes the conversation with a greeting from the bot.
        """
        initial_greeting = "Γεια σας! Είμαι ο βοηθός ασφαλειών σας. Πώς μπορώ να σας βοηθήσω σήμερα;"
        self.update_chat(f"Bot: {initial_greeting}", is_user=False)
        # Add initial greeting to history as if it was a model response
        self.chat_history.append({"role": "model", "text": initial_greeting})


    def send_answer(self):
        """
        Handles sending the user's message to Watsonx.ai and displaying the response.
        """
        user_input = self.entry.get().strip()
        if not user_input or user_input == self.placeholder_text:
            return

        # Hide top frame on first send
        if not self.frame_hidden:
            self.top_frame.place_forget()
            # Adjust chat window size after hiding top frame
            self.chat_window.configure(height=400) # Give more height
            self.chat_window.place(x=20, y=20) # Reposition if needed
            self.entry.place(x=20, y=430) # Move entry down
            self.send_button.place(x=730, y=428) # Move button down
            self.frame_hidden = True

        # Display user's message
        self.update_chat(f"You: {user_input}", is_user=True)
        self.entry.delete(0, "end")

        # Add user message to history
        self.chat_history.append({"role": "user", "text": user_input})

        # Get response from Watsonx.ai
        bot_response = self.send_message_to_watsonx_ai(user_input)

        # Display bot's response
        self.update_chat(f"Bot: {bot_response}", is_user=False)
        # Add bot message to history
        self.chat_history.append({"role": "model", "text": bot_response})


if __name__ == "__main__":
    root = ctk.CTk()
    app = SimpleNLPApp(root)
    root.mainloop()