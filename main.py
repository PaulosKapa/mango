def words(specified):
    lines_words = []
    with open("test.txt", 'r', encoding="utf-8") as file:
        for line in file:
            # Split the line into words (split() handles multiple spaces)
            words = line.split()
            for word in words:
                if word == specified:
                    lines_words.append(words)
    return(lines_words)

print(words("πινακίδα"))