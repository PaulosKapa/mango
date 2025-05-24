import spacy
from flask import Flask, request, jsonify
import sqlite3
import json
import plate, incident, name  # Your custom modules for NLP extraction

# --- Flask Setup ---
app = Flask(__name__)

# --- Load Greek NLP Model Once ---
try:
    nlp = spacy.load("el_core_news_lg")
except OSError:
    print("Greek language model 'el_core_news_lg' not found. Please run:")
    print("python -m spacy download el_core_news_lg")
    exit()

# --- SQLite Setup ---
conn = sqlite3.connect('chat_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    names TEXT,
    plates TEXT,
    events TEXT,
    full_text_processed TEXT
)
''')
conn.commit()

def save_to_db(extracted_data):
    cursor.execute('''
        INSERT INTO incidents (
            category,
            reg_number,
            name,
            location,
            incident_description,
            destination,
            "Possible malfunction",
            "Possible resolution",
            "Recommented autorepair-shop",
            "Is final destination within the country?",
            "Was delay-voucher used?",
            "Was a link for geolocation sent?",
            "Was a declaration needed?",
            "Is a fast track case?",
            "Is it a fraud?",
            "Communication quality",
            "Tags/Short summary"
     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("Incident Category", ""),
        data.get("Reg. number", ""),
        data.get("Name", ""),
        data.get("Location", ""),
        data.get("Incident Description", ""),
        data.get("Destination", ""),
        data.get("Possible malfunction", ""),
        data.get("Possible resolution", ""),
        data.get("Recommented autorepair-shop", ""),
        data.get("Is final destination within the country?", ""),
        data.get("Was delay-voucher used?", ""),
        data.get("Was a link for geolocation sent?", ""),
        data.get("Was a declaration needed?", ""),
        data.get("Is a fast track case?", ""),
        data.get("Is it a fraud?", ""),
        data.get("Communication quality", ""),
        data.get("Tags/Short summary", "")
    ))
    conn.commit()
    print("Saved answers to database chat_data.db")

# --- Conversation State (global, for demo purposes) ---
conversation_state = {
    "current_question_index": -1,
    "current_incident_text": "",
    "mock_questions": [
         "Please describe what happened:",
    "What is your plate registration number?",
    "What is your name?",
    "Where are you?",
    "Where would you like to go?",
    "Possible malfunction?",
    "Possible resolution?",
    "Recommented autorepair-shop?",
    "Is final destination within the country? (Yes/No)",
    "Was delay-voucher used? (Yes/No)",
    "Was a link for geolocation sent? (Yes/No)",
    "Was a declaration needed? (Yes/No)",
    "Is it a fast track case? (Yes/No)",
    "Is it a fraud? (Yes/No)",
    "Communication quality?",
    "Tags/Short summary?"
]
}

# --- Start conversation ---
@app.route('/start_conversation', methods=['GET'])
def start_conversation():
    global conversation_state
    conversation_state["current_question_index"] = 0
    conversation_state["current_incident_text"] = ""
    first_question = conversation_state["mock_questions"][0]
    return jsonify({
        "question": first_question,
        "status": "in_progress",
        "extracted_data": None
    })

# --- Submit answer & get next question or finish ---
@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    global conversation_state
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    answer = data.get('answer', '').strip()

    # Append answer to accumulated incident text
    conversation_state["current_incident_text"] += f" {answer}."

    # NLP Extraction
    extracted_data = {}
    try:
        extracted_events = incident.incident_process(nlp, conversation_state["current_incident_text"])
        extracted_plates = plate.plate_process(conversation_state["current_incident_text"])
        extracted_names = name.name_process(nlp, conversation_state["current_incident_text"])

        extracted_data = {
            "names": extracted_names,
            "plates": extracted_plates,
            "events": extracted_events,
            "full_text_processed": conversation_state["current_incident_text"]
        }
        print("Extracted data:", extracted_data)
    except Exception as e:
        print(f"Error during NLP processing: {e}")
        extracted_data = {
            "error": str(e),
            "full_text_processed": conversation_state["current_incident_text"]
        }

    # Next question
    conversation_state["current_question_index"] += 1
    idx = conversation_state["current_question_index"]
    if idx < len(conversation_state["mock_questions"]):
        next_question = conversation_state["mock_questions"][idx]
        return jsonify({
            "question": next_question,
            "status": "in_progress",
            "extracted_data": extracted_data
        })
    else:
        # Conversation finished, save to DB
        save_to_db(extracted_data)
        return jsonify({
            "question": "Όλες οι ερωτήσεις απαντήθηκαν. Δείτε τα τελικά αποτελέσματα.",
            "status": "finished",
            "extracted_data": extracted_data
        })

# --- Run server ---
if __name__ == '__main__':
    print("Starting Flask Backend Server...")
    print("GET /start_conversation to begin.")
    print("POST /submit_answer with JSON: {'answer': 'user_answer'}")
    app.run(host='127.0.0.1', port=5000, debug=True)
