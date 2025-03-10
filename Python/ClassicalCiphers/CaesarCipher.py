def caesarE(key, cleartext):
    # Encrypt text by shifting letters
    ciphertext = ""
    for char in cleartext:
        if char.isalpha():
            if char.islower():
                # Shift lowercase letter
                ciphertext += chr((ord(char) + key - 97) % 26 + 97)
            else:
                # Shift uppercase letter
                ciphertext += chr((ord(char) + key - 65) % 26 + 65)
        else:
            # Keep non-letters as is
            ciphertext += char
    return ciphertext

def caesarD(key, ciphertext):
    cleartext = ""
    for char in ciphertext:
        if char.isalpha():
            if char.islower():
                cleartext += chr((ord(char) - key - 97) % 26 + 97)
            else:
                cleartext += chr((ord(char) - key - 65) % 26 + 65)
        else:
            cleartext += char
    return cleartext

def main():
    try:
        key = int(input("Enter encryption key (number): "))
    except ValueError:
        print("Invalid key entered. Using default key 3.")
        key = 3
    cleartext = input("Enter text to encrypt: ")
    ciphertext = caesarE(key, cleartext)
    print("Encrypted text: " + ciphertext)
    decrypted_text = caesarD(key, ciphertext)
    print("Decrypted text: " + decrypted_text)

if __name__ == "__main__":
    main()