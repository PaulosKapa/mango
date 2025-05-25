# app.py

from flask import Flask, request, jsonify
import spacy, sqlite3, json
import plate, incident, name, location, malfunction
import watson_interface

app = Flask(__name__)

# Load SpaCy Greek model
try:
    nlp = spacy.load("el_core_news_lg")
except OSError:
    print("Run: python -m spacy download el_core_news_lg")
    exit()

# SQLite setup
conn = sqlite3.connect('chat_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    names TEXT,
    plates TEXT,
    events TEXT,
    location TEXT,
    malfunction TEXT,
    full_text_processed TEXT
)
''')
conn.commit()

def save_to_db(extracted_data):
    cursor.execute('''
        INSERT INTO incidents (names, plates, events, location, malfunction, full_text_processed)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        json.dumps(extracted_data.get("names", []), ensure_ascii=False),
        json.dumps(extracted_data.get("plates", []), ensure_ascii=False),
        json.dumps(extracted_data.get("events", []), ensure_ascii=False),
        json.dumps(extracted_data.get("location", []), ensure_ascii=False),
        json.dumps(extracted_data.get("malfunction", []), ensure_ascii=False),
        extracted_data.get("full_text_processed", "")
    ))
    conn.commit()

# In‐memory conversation state
conversation_state = { "current_incident_text": "" }

@app.route('/start_conversation', methods=['GET'])
def start_conversation():
    # Reset AI history and conversation context
    watson_interface.reset_history()
    conversation_state["current_incident_text"] = ""
    first_q = watson_interface.generate_next_question("")
    return jsonify({
        "question": first_q,
        "status":   "in_progress",
        "extracted_data": None
    })

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    ans = request.get_json().get("answer", "").strip()
    if not ans:
        return jsonify({"error": "Empty answer"}), 400

    # Append to running transcript
    conversation_state["current_incident_text"] += f" {ans}."

    # Run all NLP extractors into a single dict
    try:
        events     = incident.incident_process(nlp, conversation_state["current_incident_text"])
        plates     = plate.plate_process(conversation_state["current_incident_text"])
        names      = name.name_process(nlp, conversation_state["current_incident_text"])
        locs       = location.location_of_case(nlp, conversation_state["current_incident_text"])
        malfuncs   = malfunction.possible_vehicle_malfunction(nlp, conversation_state["current_incident_text"])
        extracted_data = {
            "names": names,
            "plates": plates,
            "events": events,
            "location": locs,
            "malfunction": malfuncs,
            "full_text_processed": conversation_state["current_incident_text"].strip()
        }
    except Exception as e:
        extracted_data = {
            "error": str(e),
            "full_text_processed": conversation_state["current_incident_text"].strip()
        }

    # Ask the AI for the next follow-up question
    next_q = watson_interface.generate_next_question(conversation_state["current_incident_text"])
    if next_q:
        return jsonify({
            "question": next_q,
            "status":   "in_progress",
            "extracted_data": extracted_data
        })
    else:
        # No more questions — save to DB and finish
        save_to_db(extracted_data)
        return jsonify({
            "question":       "Όλες οι ερωτήσεις απαντήθηκαν.",
            "status":         "finished",
            "extracted_data": extracted_data
        })

if __name__ == '__main__':
    print("Server running on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
