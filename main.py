import string
#what symbols to emit from the words
def is_punctuation(char):
    """Check if a character is punctuation (including Greek punctuation)."""
    return char in string.punctuation or char in ':,.;«»΄¨“”‘’'  # Add Greek-specific symbols if needed
#emit symbols and join the word in one
def clean_word(word):
    """Remove all punctuation from a word procedurally."""
    return ''.join(char for char in word if not is_punctuation(char))
#split the text to lines and find the given word
def words(specified):
    lines_words = []
    with open("test.txt", 'r', encoding="utf-8") as file:
        for line in file:
            # Split the line into words (split() handles multiple spaces)
            words_in_line  = line.split()
            if specified in words_in_line and "Π:" in words_in_line:
                # Append the entire line's words as a sublist
                lines_words.append(words_in_line)
    return(lines_words)
#emit symbols from the array
def clean_arrays(choosen_word):
    new_array = []
    for words_var in words(choosen_word):
        for word in words_var:
            new_array.append(clean_word(word))
    return(new_array)

#find plate
def choose_plate(): 
   
    for word in clean_arrays("πινακίδα"):
        if len(word) == 7:
            return word

#find name
def choose_name(): 
    name = []
    i=0
    for word in clean_arrays("όνομα"):
        if word[0].isupper() and word != 'Π' and i!=1:
            name.append(word)
        i+=1            
    return(name)

print(choose_plate())
print(choose_name())