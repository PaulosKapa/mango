# app.py

from flask import Flask, request, jsonify
import spacy
import sqlite3, json
import plate, incident, name
import watson_interface
#from watson_interface import generate_question_list  # <-- Dynamic questions from AI

app = Flask(__name__)

# Load SpaCy NLP model (Greek)
try:
    nlp = spacy.load("el_core_news_lg")
except OSError:
    print("Run: python -m spacy download el_core_news_lg")
    exit()

# SQLite DB Setup
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
        INSERT INTO incidents (names, plates, events, full_text_processed)
        VALUES (?, ?, ?, ?)
    ''', (
        json.dumps(extracted_data.get("names", []), ensure_ascii=False),
        json.dumps(extracted_data.get("plates", []), ensure_ascii=False),
        json.dumps(extracted_data.get("events", []), ensure_ascii=False),
        extracted_data.get("full_text_processed", "")
    ))
    conn.commit()
    print("[DB] Saved incident data.")

# --- Conversation State ---
conversation_state = {
    "current_question_index": -1,
    "current_incident_text": "",
    "mock_questions": []
}

# Start conversation and dynamically generate questions
@app.route('/start_conversation', methods=['GET'])
def start_conversation():
    try:
        questions = watson_interface.generate_question_list()
        if not questions:
            raise ValueError("AI returned no questions.")
        conversation_state["mock_questions"] = questions
        conversation_state["current_question_index"] = 0
        conversation_state["current_incident_text"] = ""
        return jsonify({
            "question": questions[0],
            "status": "in_progress",
            "extracted_data": None
        })
    except Exception as e:
        return jsonify({
            "error": "Failed to load AI-generated questions.",
            "details": str(e)
        }), 500

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    answer = data.get('answer', '').strip()
    if not answer:
        return jsonify({"error": "Empty answer"}), 400

    # Append user response
    conversation_state["current_incident_text"] += f" {answer}."

    try:
        events = incident.incident_process(nlp, conversation_state["current_incident_text"])
        plates = plate.plate_process(conversation_state["current_incident_text"])
        names = name.name_process(nlp, conversation_state["current_incident_text"])
        extracted_data = {
            "names": names,
            "plates": plates,
            "events": events,
            "full_text_processed": conversation_state["current_incident_text"].strip()
        }
    except Exception as e:
        extracted_data = {
            "error": str(e),
            "full_text_processed": conversation_state["current_incident_text"].strip()
        }

    # Move to next question
    conversation_state["current_question_index"] += 1
    idx = conversation_state["current_question_index"]

    if idx < len(conversation_state["mock_questions"]):
        return jsonify({
            "question": conversation_state["mock_questions"][idx],
            "status": "in_progress",
            "extracted_data": extracted_data
        })
    else:
        save_to_db(extracted_data)
        return jsonify({
            "question": "Όλες οι ερωτήσεις απαντήθηκαν.",
            "status": "finished",
            "extracted_data": extracted_data
        })

if __name__ == '__main__':
    print("Server running on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
