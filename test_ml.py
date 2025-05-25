import spacy
from flask import Flask, request, jsonify
import test_back
# --- NLP Logic (Backend) ---
# This function remains the same as our previous, refined version for accident description
# --- Flask Application Setup ---
app = Flask(__name__)

# Define the API endpoint for NLP processing
@app.route('/process_general', methods=['POST'])
def process_general():
    # Ensure the request is JSON
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    input_text = data.get('text', '')

    if not input_text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Call the NLP backend logic
        extracted_events = test_back.get_accident_description(input_text, spacy)
        return jsonify({"events": extracted_events})
    except Exception as e:
        # Catch any errors during NLP processing and return a server error
        print(f"Error during NLP processing: {e}")
        return jsonify({"error": "Internal server error during NLP processing."}), 500

# --- Server Start ---
if __name__ == '__main__':
    # Make sure to run the Spacy model download command first!
    # python -m spacy download el_core_news_sm

    # You can set the host to '0.0.0.0' to make it accessible from other machines
    # on your network, if desired. For local testing, '127.0.0.1' or 'localhost' is fine.
    print("Starting Flask Backend Server...")
    print("Accessible at http://127.0.0.1:5000")
    print("POST to /process_incident with JSON: {'text': 'Your incident description'}")
    app.run(host='127.0.0.1', port=5000, debug=True) # debug=True is good for development