import argparse
import string
from collections import Counter

ALPH = string.ascii_uppercase

portuguese_freqs = {
    'A': 0.139, 'B': 0.010, 'C': 0.044, 'D': 0.054, 'E': 0.122,
    'F': 0.010, 'G': 0.012, 'H': 0.008, 'I': 0.069, 'J': 0.004,
    'K': 0.001, 'L': 0.028, 'M': 0.042, 'N': 0.053, 'O': 0.108,
    'P': 0.029, 'Q': 0.009, 'R': 0.069, 'S': 0.079, 'T': 0.049,
    'U': 0.040, 'V': 0.013, 'W': 0.0001, 'X': 0.003, 'Y': 0.0001, 'Z': 0.004
}


# ---------- Load ao ficheiro -------------
def load_ciphertext(path):
    with open(path, "r", encoding="utf-8") as f:
        ciphertext = f.read().upper() # Variavel com a mensagem encriptada

    return ciphertext

# ---------- Desencriptação -------------
def decrypt(ciphertext, key):
    plaintext = []
    key_rep = (key * (len(ciphertext) // len(key))) + key[:len(ciphertext) % len(key)]
    
    for i in range(len(ciphertext)):
        cipher_val = ord(ciphertext[i]) - ord('A')
        key_val = ord(key_rep[i]) - ord('A')

        plain_val = (cipher_val - key_val) % 26

        letter= chr(plain_val + ord('A'))
        plaintext.append(letter)
    
    plaintext = ''.join(plaintext)
    return plaintext

# ---------- Divisão por colunas -------------
def split_col(ciphertext, key_size):
    columns = ['' for _ in range(key_size)]
    for i, c in enumerate(ciphertext):
        columns[i % key_size] += c

    return columns

# ---------- Frequência das letras -------------
def letters_freq(text):
    letters={}
    n_letters= 0
    for i in text:
        if i == '\n':
            continue
        else:
            n_letters += 1
            if i in letters:
                letters[i] += 1
            else: 
                letters[i] = 1

    letters = {key: round((value/n_letters) *100,1) for key,value in letters.items()}
    letters_ord = dict(sorted(letters.items(), key=lambda x: x[1], reverse=True))

    return letters_ord

# ---------- Cálculo para a frequência observada e esperada -------------
def chi_squared(observed, expected):
    return sum(
        (observed.get(ch, 0) - expected[ch]/100)**2 / (expected[ch]/100)
        for ch in expected
    )

# ---------- Desencriptar cifra de Ceasar -------------
def caesar_decrypt(text, shift):
    result = ''
    for ch in text:
        val = (ord(ch) - ord('A') - shift) % 26
        result += chr(val + ord('A'))
    return result

# ---------- Avalia o melhor shift por coluna -------------
def best_shift_for_column(column, expected_freqs):
    best_shift = 0
    best_score = float('inf')
    for shift in range(26):
        decrypted = caesar_decrypt(column, shift)
        observed = letters_freq(decrypted)
        score = chi_squared(observed, expected_freqs)
        if score < best_score:
            best_score = score
            best_shift = shift
    return best_shift

# ---------- Encontrar e validar chave -------------
def find_key_validate(ciphertext, key_size, list):

    cols = split_col(ciphertext, key_size)
    shifts = [best_shift_for_column(col, portuguese_freqs) for col in cols]
    key = ''.join(chr(s + ord('A')) for s in shifts)
    plaintext = decrypt(ciphertext, key)

    # validação: pelo menos uma palavra das dadas existe no plaintext
    up = plaintext.upper()
    for word in list:
        if word.upper() in up:
            return key, plaintext

    return None  # não encontrou uma key 

# ---------- main -------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("key", type=int, help="Key size")
    parser.add_argument("path", type=str, help="Path for file")
    parser.add_argument("list", nargs="+", help="List of Words")
    args = parser.parse_args()
    
    ciphertext = load_ciphertext(args.path)
    result = find_key_validate(ciphertext,args.key, args.list)

    if result is None:
        print("None")
    else: 
        key,plaintext = result
        print("Chave usada para decifrar:", key)
        print("Texto decifrado:")
        print(plaintext)



if __name__ == "__main__":
    main()