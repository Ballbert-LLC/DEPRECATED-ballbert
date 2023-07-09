from phonetics import metaphone

def phoneticize_text(text):
    words = text.split()
    phonetic_words = []

    for word in words:
        phonetic_word = metaphone(word)
        phonetic_words.append(phonetic_word)

    return ' '.join(phonetic_words)

# Example usage
text = "Hello, how are you?"
phonetic_text = phoneticize_text(text)
print(phonetic_text)
