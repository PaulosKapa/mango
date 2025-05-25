import spacy
from flask import Flask, request, jsonify
import plate, incident, name # Ensure these modules are correctly implemented

# --- Flask Setup ---
app = Flask(__name__)

# --- Load Greek NLP Model Once ---
try:
    nlp = spacy.load("el_core_news_lg")
except OSError:
    print("Greek language model 'el_core_news_lg' not found. Please run:")
    print("python -m spacy download el_core_news_lg")
    exit()

# --- Conversation State (Global for simplicity, use session for real app) ---
conversation_state = {
    "current_question_index": -1, # Start at -1 to ask first question at index 0
    "current_incident_text": "", # This will accumulate all answers
    "mock_questions": [
        "Ποια ήταν η ακριβής ώρα του συμβάντος; (π.χ. 14:30)",
        "Σε ποια τοποθεσία συνέβη το συμβάν; (Οδός, αριθμός, περιοχή)",
        "Υπήρχαν μάρτυρες στο σημείο;",
        "Ποια ήταν η πινακίδα του άλλου οχήματος;",
        "Ποιο ήταν το χρώμα του άλλου οχήματος;",
        "Ποιο ήταν το όνομα του οδηγού του άλλου οχήματος;",
        "Υπάρχουν κάποιες φωτογραφίες της ζημιάς;",
        "Ποια ήταν η ταχύτητα των οχημάτων πριν τη σύγκρουση;"
    ]
}

# --- API endpoint to start the conversation ---
@app.route('/start_conversation', methods=['GET'])
def start_conversation():
    global conversation_state
    conversation_state["current_question_index"] = 0
    conversation_state["current_incident_text"] = "" # Reset for new conversation

    if conversation_state["current_question_index"] < len(conversation_state["mock_questions"]):
        first_question = conversation_state["mock_questions"][conversation_state["current_question_index"]]
        return jsonify({
            "question": first_question,
            "status": "in_progress",
            "extracted_data": None # No data yet
        })
    else:
        # Should not happen on start, but as a fallback
        return jsonify({
            "question": "Δεν υπάρχουν ερωτήσεις.",
            "status": "finished",
            "extracted_data": None
        })

# --- API endpoint to submit an answer and get the next question/results ---
@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    global conversation_state
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    answer = data.get('answer', '')

    # Append the answer to the incident text
    # A more sophisticated LLM would rephrase and integrate, here we just append.
    conversation_state["current_incident_text"] += f" {answer}."

    # Process the accumulated incident text
    extracted_data = {}
    try:
        extracted_events = incident.incident_process(nlp, conversation_state["current_incident_text"])
        extracted_plate = plate.plate_process(conversation_state["current_incident_text"])
        extracted_name = name.name_process(nlp, conversation_state["current_incident_text"])
        extracted_data = {
            "names": extracted_name,
            "plates": extracted_plate,
            "events": extracted_events,
            "full_text_processed": conversation_state["current_incident_text"] # Show what's being processed
        }
    except Exception as e:
        # Log the error but don't halt the conversation
        print(f"Error during NLP processing of accumulated text: {e}")
        extracted_data = {"error": f"NLP processing issue: {e}", "full_text_processed": conversation_state["current_incident_text"]}

    # Move to the next question
    conversation_state["current_question_index"] += 1

    if conversation_state["current_question_index"] < len(conversation_state["mock_questions"]):
        next_question = conversation_state["mock_questions"][conversation_state["current_question_index"]]
        return jsonify({
            "question": next_question,
            "status": "in_progress",
            "extracted_data": extracted_data
        })
    else:
        # All questions asked
        return jsonify({
            "question": "Όλες οι ερωτήσεις απαντήθηκαν. Δείτε τα τελικά αποτελέσματα.",
            "status": "finished",
            "extracted_data": extracted_data
        })

# --- Server Start ---
if __name__ == '__main__':
    print("Starting Flask Backend Server...")
    print("Accessible at http://127.0.0.1:5000")
    print("GET /start_conversation to begin.")
    print("POST /submit_answer with JSON: {'answer': 'user_answer'}")
    app.run(host='127.0.0.1', port=5000, debug=True)