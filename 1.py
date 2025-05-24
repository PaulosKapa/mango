import re  # Move import to top of file (best practice)

def extract_plates(text):
    return re.findall(r'[Α-Ω]{2,3}\d{4}', text)  # Finds Greek license plates

def words(specified):
    lines_words = []
    with open("test.txt", 'r', encoding="utf-8") as file:
        text = file.read()
        
        # Extract and print license plates
        plates = extract_plates(text)
        print(f"Found license plates: {plates}")
        
        # Reset file pointer for line-by-line reading
        file.seek(0)  
        for line in file:
            if specified in line:  # More efficient than splitting
                lines_words.append(line.strip())
    
    return lines_words

# Test both functions
print("Lines containing 'πινακίδα':")
print(words("πινακίδα"))