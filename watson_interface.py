import os
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai import Credentials

# IBM Watsonx Configuration
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

try:
    credentials = Credentials(api_key=API_KEY, url=SERVICE_URL)
    model_inference = ModelInference(
        model_id=MODEL_ID,
        params=GEN_PARAMS,
        credentials=credentials,
        project_id=PROJECT_ID
    )
except Exception as e:
    print(f"Error initializing Watsonx: {e}")
    model_inference = None


# ---- Chat Handling ----

chat_history = []


def send_message_to_watsonx_ai(user_input):
    global chat_history
    try:
        prompt = format_prompt_from_history(user_input)
        result = model_inference.generate_text(prompt=prompt)
        response = result.strip()
        chat_history.append({"role": "user", "text": user_input})
        chat_history.append({"role": "model", "text": response})
        return response
    except Exception as e:
        print(f"Watsonx error: {e}")
        return "Συγγνώμη, παρουσιάστηκε πρόβλημα με το μοντέλο AI."


def format_prompt_from_history(user_input):
    system_prompt = (
        "Είσαι ένας ευγενικός, σύντομος και επαγγελματικός ασφαλιστικός βοηθός. "
        "Απαντάς πάντα στα ελληνικά, με απλό και ξεκάθαρο τρόπο. Μην κάνεις εισαγωγές, "
        "και μην επαναλαμβάνεις τα ερωτήματα ή τον εαυτό σου."
    )
    conversation = system_prompt + "\n\n"
    for entry in chat_history:
        if entry["role"] == "user":
            conversation += f"Ερώτηση: {entry['text']}\n"
        elif entry["role"] == "model":
            conversation += f"Απάντηση: {entry['text']}\n"
    conversation += f"Ερώτηση: {user_input}\nΑπάντηση:"
    return conversation


# ---- Public Utility ----

def generate_question_list():
    instruction = (
        "Θέλω να δημιουργήσεις μια λίστα με σύντομες, χρήσιμες ερωτήσεις που θα έκανε ένας ασφαλιστικός βοηθός "
        "σε έναν πελάτη μετά από τροχαίο. Στόχος είναι να συλλέξεις τις απαραίτητες πληροφορίες για το συμβάν. "
        "Μην εξηγείς, μην αριθμείς. Δώσε μόνο τις ερωτήσεις σε ξεχωριστές γραμμές."
    )
    ai_response = send_message_to_watsonx_ai(instruction)
    print("Raw AI Response:\n", ai_response)
    questions = [line.strip("•- ").strip() for line in ai_response.split("\n") if line.strip()]
    return questions
