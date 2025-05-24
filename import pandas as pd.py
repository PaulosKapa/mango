import pandas as pd

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

def save_to_excel():
    filtered_lines = words("πινακίδα")
    # Convert list of word lists to DataFrame (each word is a column)
    df = pd.DataFrame(filtered_lines)
    # Save to Excel
    df.to_excel('filtered_lines.xlsx', index=False, header=False)
    print("Saved filtered lines to filtered_lines.xlsx")

save_to_excel()
choose_label()
