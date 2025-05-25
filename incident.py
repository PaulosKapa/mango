def incident_process(nlp, text):   
 #Extracts the core description of an accident from the text.
    #Focuses on sentences containing accident-related keywords and verbs.
    
    doc = nlp(text)
    accident_descriptions = []

    # Define keywords/phrases strongly indicating an accident or collision in Greek
    # These are usually verbs or key nouns related to the incident itself.
    accident_indicators = [
    "ατύχημα", "συγκρούστηκε", "σύγκρουση", "εξετράπη", "φρέναρε",
    "πρόσκρουση", "τρακάρισμα", "τρακάρισε", "χτύπησε", "χτυπήθηκε",
    "ανατροπή", "ανατράπηκε", "εκτροπή", "παραβίασε", "δεν σταμάτησε",
    "εκτροχιασμός", "εκτροχιάστηκε", "προσέκρουσε", "ζημιά", "ζημιές",
    "οδική", "αυτοκινητιστικό", "συμβάν", "παραβίαση", "προσέκρουσε"
]
    for sent in doc.sents:
        sent_text_lower = sent.text.lower()
        
        # Check if the sentence contains any strong accident indicators
        if any(indicator in sent_text_lower for indicator in accident_indicators):
           
            # If it's a descriptive sentence about the accident, add it.
            # You might want to strip leading/trailing whitespace.
            accident_descriptions.append(sent.text.strip())

    # If multiple sentences describe the accident, return them all.
    # Otherwise, you might want to return the first one, or a concatenated string.
    return accident_descriptions
