def vigE(key, cleartext):
    ciphertext = ""
    key = key.upper()  # Change key to uppercase for consitancy
    key_length = len(key)
    key_index = 0
    for char in cleartext:
        if char.isalpha():  # Only change letters/characters
            if char.islower():
                # Get number shift from key letter 
                # Change the lowercase letter
                shift = ord(key[key_index]) - 65
                ciphertext += chr((ord(char) + shift - 97) % 26 + 97)
            else:
                # Get number shift from key letter
                # Change the uppercase letter.
                shift = ord(key[key_index]) - 65
                ciphertext += chr((ord(char) + shift - 65) % 26 + 65)
            key_index = (key_index + 1) % key_length
        else:
            # If not a letter, just keep it as it is.
            ciphertext += char
    return ciphertext

def vigD(key, ciphertext):
    cleartext = ""
    key = key.upper()
    key_length = len(key)
    key_index = 0
    for char in ciphertext:
        if char.isalpha(): 
            if char.islower():
                shift = ord(key[key_index]) - 65
                cleartext += chr((ord(char) - shift - 97) % 26 + 97)
            else:
                shift = ord(key[key_index]) - 65
                cleartext += chr((ord(char) - shift - 65) % 26 + 65)
            key_index = (key_index + 1) % key_length
        else:
            cleartext += char
    return cleartext

def main():
    try:
        key = input("Enter encryption key (word): ")
    except ValueError:
        print("Invalid key entered. Using default key PYTHON")
        key = "PYTHON"
    cleartext = input("Enter text to encrypt: ")
    ciphertext = vigE(key, cleartext)
    print("Encrypted text: " + ciphertext)
    decrypted_text = vigD(key, ciphertext)
    print("Decrypted text: " + decrypted_text)

if __name__ == "__main__":
    main()