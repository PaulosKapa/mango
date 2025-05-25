# watson_interface.py

import os
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai import Credentials

# ————— IBM Watsonx Configuration —————
API_KEY     = "SL2Ug6gQ9pVZV12JWtX_y7ZWyJQCvLY8EubR84iZj4cP"
SERVICE_URL = "https://us-south.ml.cloud.ibm.com"
PROJECT_ID  = "f406bc13-a60d-4073-9e52-d99565d73dc4"
MODEL_ID    = "meta-llama/llama-4-maverick-17b-128e-instruct-fp8"

GEN_PARAMS = {
    GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
    GenParams.MIN_NEW_TOKENS:   1,
    GenParams.MAX_NEW_TOKENS: 200,
    GenParams.REPETITION_PENALTY: 1.0,
    GenParams.TEMPERATURE:       0.1,
}

# Initialize Watsonx client
try:
    credentials = Credentials(api_key=API_KEY, url=SERVICE_URL)
    model_inference = ModelInference(
        model_id=MODEL_ID,
        params=GEN_PARAMS,
        credentials=credentials,
        project_id=PROJECT_ID
    )
except Exception as e:
    print(f"[Watsonx Init Error] {e}")
    model_inference = None

# In‐memory history for context
chat_history = []

def format_prompt_for_question(context_text: str) -> str:
    """
    Build the prompt that asks the AI to produce the next question
    for collecting traffic‐accident details in Greek.
    """
    system = (
        "Είσαι βοηθός ασφαλιστικής εταιρείας που θέλεις να εξυπηρετήσεις των πελάτη σου"
        "Είσαι ένας επαγγελματικός ασφαλιστικός βοηθός. "
        "Δεν απαντάς ποτέ. Πάντα περιμένεις την απάντηση του χρήστη για να κάνεις κάποια ερώτηση "
        "Αν δεν υπάρχει κείμενο να απαντήσεις πες Καλησπέρα σας, πώς μπορώ να σας εξυπηρετήσω"
        "Με βάση τη μέχρι τώρα συζήτηση με τον πελάτη, κάνε την επόμενη "
        "Είσαι ένας σύντομος, επαγγελματικός και ευγενικός Ασφαλιστικός Βοηθός. "
        "κατάλληλη ερώτηση για να καταγράψεις ένα τροχαίο συμβάν. "
        "Απάντα άμεσα και περιεκτικά με νέες, σχετικές πληροφορίες."
        "Μην εξηγείς και μην κάνεις εισαγωγές. Απάντησε με μία ερώτηση στα ελληνικά."
        "Να μην επαναλαμβάνεις το κειμενό σου."
        "Μην κάνεις πάνω απο δύο ερωτήσεις τον χρήστη."
    )

    convo = ""
    # (Optional) include previous Q&A for context
    for entry in chat_history:
        if entry["role"] == "user":
            convo += f"Ερώτηση: {entry['text']}\n"
        else:
            convo += f"Απάντηση: {entry['text']}\n"

    convo += f"Ερώτηση: {context_text.strip()}\nΑπάντηση:"
    return system + convo

def generate_next_question(context_text: str) -> str:
    """
    Public function your backend calls to get the *next* question
    from Watsonx, given the conversation so far.
    """
    global chat_history
    if model_inference is None:
        return "Το μοντέλο δεν είναι διαθέσιμο αυτή τη στιγμή."

    try:
        prompt = format_prompt_for_question(context_text)
        result = model_inference.generate_text(prompt=prompt)
        question = result.strip()

        # Update history so that follow‐ups can see this Q&A chain
        chat_history.append({"role": "user",   "text": context_text})
        chat_history.append({"role": "model",  "text": question})

        return question
    except Exception as e:
        print(f"[Watsonx Error] {e}")
        return "Συγγνώμη, παρουσιάστηκε πρόβλημα με το μοντέλο AI."

def reset_history():
    """Call this if you want to start a brand‐new conversation."""
    global chat_history
    chat_history = []
