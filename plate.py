def plate_process(text):
        
    
            cleaned_content = text.replace(',', '').replace('.', '')
            words = cleaned_content.split()  # Split the string by whitespace
            for word in words:
                if len(word) == 7:
                    plate_valid = True
                # Check first 3 characters are Greek letters (A-Ω)
                    for i in range(3):
                        char = word[i].upper()
                        if not ('\u0391' <= char <= '\u03A9'):  # Greek uppercase letters range
                            plate_valid = False
                            break
            
                    # Check last 4 characters are digits
                    if plate_valid:
                        for i in range(3, 7):
                            if not word[i].isdigit():
                                plate_valid = False
                                break
            
                    if plate_valid:
                        return(word)
