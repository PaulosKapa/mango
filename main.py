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


def choose_label():
    for word_array  in words("πινακίδα"):
        for word in word_array:
            print(word)

choose_label()