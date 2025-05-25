def location_of_case(nlp, text):
    """
    Extracts sentences describing the location of the case (Τοποθεσία Περιστατικού).
    Looks for keywords asking where the incident happened.
    """
    location_indicators = [
        "πού συνέβη", "τοποθεσία", "διεύθυνση", "περιοχή", "πόλη", "δρόμος", "οδός",
        "συμβάν", "σημείο"
    ]
    doc = nlp(text.lower())
    locations = []
    for sent in doc.sents:
        if any(keyword in sent.text for keyword in location_indicators):
            locations.append(sent.text.strip())
    return locations
