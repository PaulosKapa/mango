def possible_vehicle_malfunction(nlp, text):
    """
    Extracts sentences related to possible vehicle malfunction (Πιθανή βλάβη οχήματος).
    """
    malfunction_indicators = [
        "βλάβη", "πρόβλημα", "μηχανική βλάβη", "σπάσιμο", "ελάττωμα", "κακή λειτουργία",
        "στάση", "μπλοκάρισμα", "μπλοκαρισμένο", "κατεστραμμένο"
    ]
    doc = nlp(text.lower())
    malfunctions = []
    for sent in doc.sents:
        if any(keyword in sent.text for keyword in malfunction_indicators):
            malfunctions.append(sent.text.strip())
    return malfunctions
