def name_process(nlp,text):
    # Process the text with the loaded NLP pipeline
    doc = nlp(text)

    # Extract Greek names
    greek_names = []
    for ent in doc.ents:
        if ent.label_ == "PERSON": # Add this condition back to filter for PERSON entities
            greek_names.append(ent.text)
    return(greek_names)