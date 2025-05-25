import spacy
from flask import Flask, request, jsonify
import plate, incident, name  # Ensure these modules are correctly implemented
import sqlite3, json

# --- Flask Setup ---
app = Flask(__name__)

# --- Load Greek NLP Model Once ---
try:
    nlp = spacy.load("el_core_news_lg")
except OSError:
    print("Greek language model 'el_core_news_lg' not found. Please run:")
    print("    python -m spacy download el_core_news_lg")
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

# --- Helper to Save to DB ---
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
    print("[DB] Saved incident data to database.")

# --- Conversation State (In-Memory for Demo) ---
conversation_state = {
    "current_question_index": -1,
    "current_incident_text": "",
    "mock_questions": [
        "Ποιο είναι το ονοματεπώνυμό σας;",
        "Ποια είναι η πινακίδα του οχήματος που εμπλέκεται; (π.χ. ABC-1234)",
        "Σε ποια ακριβή τοποθεσία συνέβη το περιστατικό; (Οδός, αριθμός, περιοχή, πόλη)",
        "Ποια ήταν η ακριβής ώρα του συμβάντος; (π.χ. 14:30)",
        "Περιγράψτε με λίγα λόγια τι συνέβη;",
        "Υπήρχαν μάρτυρες στο σημείο;",
        "Ποιος είναι ο τελικός προορισμός του οχήματος μετά το συμβάν, αν χρειάζεται ρυμούλκηση;"
    ]
}

# --- API: Start Conversation ---
@app.route('/start_conversation', methods=['GET'])
def start_conversation():
    conversation_state["current_question_index"] = 0
    conversation_state["current_incident_text"] = ""
    first_q = conversation_state["mock_questions"][0]
    return jsonify({
        "question": first_q,
        "status": "in_progress",
        "extracted_data": None
    })

# --- API: Submit Answer ---
@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    answer = data.get('answer', '').strip()
    if not answer:
        return jsonify({"error": "Empty answer"}), 400

    # Append to incident text
    conversation_state["current_incident_text"] += f" {answer}."

    # NLP Processing
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
        next_q = conversation_state["mock_questions"][idx]
        return jsonify({
            "question": next_q,
            "status": "in_progress",
            "extracted_data": extracted_data
        })
    else:
        # Final step: save once
        save_to_db(extracted_data)
        return jsonify({
            "question": "Όλες οι ερωτήσεις απαντήθηκαν. Δείτε τα τελικά αποτελέσματα.",
            "status": "finished",
            "extracted_data": extracted_data
        })

# --- Run Server ---
if __name__ == '__main__':
    print("Starting Flask Backend on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
