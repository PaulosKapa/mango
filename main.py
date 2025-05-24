import spacy
import string

info_detail = {"Name":"", "Plate":""}

# Load the Greek language model
try:
    nlp = spacy.load("el_core_news_sm")
except OSError:
    print("Greek language model 'el_core_news_sm' not found. Please run:")
    print("python -m spacy download el_core_news_sm")
    exit()

# Example Greek text - CORRECTED: Read content from file
file_path = "test.txt"
try:
    with open(file_path, 'r', encoding="utf-8") as f:
        text = f.read() # Read the entire content of the file into the 'text' variable
        
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the file: {e}")
    exit()



def name_process():
    # Process the text with the loaded NLP pipeline
    doc = nlp(text)

    # Extract Greek names
    greek_names = []
    for ent in doc.ents:
        if ent.label_ == "PERSON": # Add this condition back to filter for PERSON entities
            greek_names.append(ent.text)
    return(greek_names)

    
def plate_process():
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()  # Read the entire file content into a string
    
            cleaned_content = content.replace(',', '').replace('.', '')
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

info_detail.update({"Name": name_process()}) 
info_detail.update({"Plate": plate_process()})

