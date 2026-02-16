from collections import Counter
import string
import math
import random



# --------------------------
# 1 Função para carregar bigramas, Função para frequência de ngramas e Função para frequência de letras
# --------------------------
def load_frequencies(path):
    freqs = {}
    total = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2:
                seq, freq = parts
                freq = float(freq)
                freqs[seq] = freq
                total += freq
    # normaliza para probabilidades logarítmicas
    for k in freqs:
        freqs[k] = math.log(freqs[k]+ 1e-9 / total)
    return freqs

def count_ngrams(text, n=2):
    text = ''.join(i for i in text if i in string.ascii_uppercase)
    ngrams = [text[i:i+n] for i in range(len(text)-n+1)]
    return dict(Counter(ngrams))

def ngrams_freq(text, n=2):
    ngrams=count_ngrams(text,n)
    total = sum(ngrams.values())

    freq = {k: round((v/total)*100,1) for k,v in ngrams.items()}
    freq_ord = dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))
    return freq_ord

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

# carregar bigramas
bigrams = load_frequencies("pt_bigrams.txt")

# --------------------------
# 2 Função para decifrar
# --------------------------
def decrypt(ciphertext, key):
    return ''.join(key.get(c, c) for c in ciphertext)

# --------------------------
# 3 Função de score
# --------------------------
def score_text(text, bigram_freqs):
    score = 0.0
    for i in range(len(text)-1):
        bigram = text[i:i+2]
        if bigram in bigram_freqs:
            score += bigram_freqs[bigram]
        else:
            # penaliza bigramas inexistentes
            score += math.log(1e-6)
    return score

# --------------------------
# 4 Completar chave parcial
# --------------------------
def complete_key(partial_key):
    letters = list(string.ascii_uppercase)
    used = {v for v in partial_key.values() if v}
    unused = [c for c in letters if c not in used]
    random.shuffle(unused)
    
    completed = {}
    i = 0
    for c in letters:
        if partial_key[c]:
            completed[c] = partial_key[c]
        else:
            completed[c] = unused[i]
            i += 1
    return completed

# --------------------------
# 5 Swap aleatório respeitando letras fixas
# --------------------------
def swap_random(key, fixed_letters=None):
    if fixed_letters is None:
        fixed_letters = set()
    swappable = [c for c in string.ascii_uppercase if c not in fixed_letters]
    a, b = random.sample(swappable, 2)
    new_key = key.copy()
    new_key[a], new_key[b] = new_key[b], new_key[a]
    return new_key

# --------------------------
# 6 Texto cifrado e chave parcial
# --------------------------

def load_ciphertext(path):
    with open(path, "r", encoding="utf-8") as f:
        ciphertext = f.read().upper() # Variavel com a mensagem encriptada

    return ciphertext

ciphertxt = "Q1_ciphertext.txt"

partial_key = {
    'A': 'V', 'B': 'J', 'C': 'G', 'D': 'E', 'E': 'K',
    'F': 'T', 'G': 'Z', 'H': 'A', 'I': 'B', 'J': 'D',
    'K': 'P', 'L': 'Q', 'M': 'Y', 'N': 'U', 'O': 'L',
    'P': 'O', 'Q': 'S', 'R': 'N', 'S': 'F', 'T': 'M',
    'U': 'X', 'V': 'I', 'W': 'R', 'X': 'H', 'Y': 'C', 'Z': 'W'
}



# --------------------------
# 7 Hill climbing 
# --------------------------

def hill_climb(ciphertext, partial_key, bigram_freqs, iterations=10000):
    fixed_letters = {v for v in partial_key.values() if v}
    best_key = complete_key(partial_key)
    best_score = score_text(decrypt(ciphertext, best_key), bigram_freqs)
    
    for i in range(iterations):
        new_key = swap_random(best_key, fixed_letters=fixed_letters)
        new_score = score_text(decrypt(ciphertext, new_key), bigram_freqs)
        
        if new_score > best_score:
            best_key, best_score = new_key, new_score
            print(f"Iteração {i}: Novo melhor score = {best_score}")
    
    return best_key, best_score


# --------------------------
# 8 Resultado final
# --------------------------

def main():
    print("Permutação usada para decifrar:")
    print(''.join(partial_key.values()))
    ciphertext = load_ciphertext(ciphertxt)
    #print(letters_freq(ciphertext))
    #print(ngrams_freq(ciphertext,n=2))
    #print(ngrams_freq(ciphertext,n=3))
    #best_key, best_score = hill_climb(ciphertext, partial_key, bigrams, iterations=10000)
    plaintext = decrypt(ciphertext, partial_key)
    #print("\nMelhor score final:", best_score)
    print("Texto decifrado:")
    print(plaintext)


if __name__ == "__main__":
    main()

