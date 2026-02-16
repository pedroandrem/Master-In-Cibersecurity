from typing import List

ciphertexts_hex: List[str] = [
    "557c7d787a11694469521d0d82cd13fb86a97d8a5b73c5869d126e91e558d413561ab0a3095a892fe763bcf744a0c331948779a0",
    "576f7d78700c635774520e0793cc19e081a37e8a5164c090990f7896e342d31a4d16a7b505448e35f078aaf643adc0339c8679be4384693854070fba72d6deae347df382",
    "516a606d7f0a67407f5a090393ca04e682a2649b4767c5879d027289e64ac6195616a2b100439832e26fa0fd44afda3f989468ba4f817f2f55150faf66d7d6b72b78ff852320",
    "576f7d78700c635774520e0793cc19e082a8659d5574c59a950f7e88f158db0a4513b4a119569129e76dabfd52a9c7239c817da745966d2f4a1413a77cd2daa83469f38338260dfcf580df1fe20672d7e8bde19670f7a7b9c66d86072f084554b61455c933766ba21bde22d5cd27723cc1",
    "51626c78701b6b577a5a0a1781d312e083a9749b5372ca908e0e7881e95bdd184105b0a218589921f06dbcf542a0de3387906fb65e817c2b480f1bab60",
    "5f6c657c6a117c4a6857080685cc13ef91a37c885d7ac19b880e6e91f75fd7125016a7b500"
]

ciphertexts: List[bytes] = [bytes.fromhex(c) for c in ciphertexts_hex]

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def show_ascii(bs: bytes) -> str:
    return ''.join(chr(b) for b in bs)

# Candidate plaintext guesses
guesses: List[str] = [
    "ERRADICAR", "MEDIDAS", "POBREZA", "URGENTE",
    "EDUCACAO", "SUSTENTAVEL", "OBJETIVOSDEDESENVOLVIMENTOSUSTENTAVEL"
]

with open("result.txt", "w", encoding="utf-8") as f:
    for guess_word in guesses:
        g_bytes: bytes = guess_word.encode('utf-8')
        L: int = len(g_bytes)

        for idx, c in enumerate(ciphertexts):
            max_offset: int = len(c) - L
            for offset in range(max_offset + 1):
                c_seg: bytes = c[offset:offset + L]
                keystream: bytes = xor_bytes(c_seg, g_bytes)

                f.write(f"\nGuess: {guess_word}, Ciphertext {idx+1}, Offset {offset}\n")
                f.write(f"   Segment Hex:   {c_seg.hex()}\n")
                f.write(f"   Guess Hex:     {g_bytes.hex()}\n")
                f.write(f"   Keystream Hex: {keystream.hex()}\n")
                f.write("   Decrypted Fragments:\n")

                for jdx, c_other in enumerate(ciphertexts):
                    if offset + L > len(c_other):
                        continue
                    c_other_seg: bytes = c_other[offset:offset + L]
                    p_frag: bytes = xor_bytes(c_other_seg, keystream)
                    f.write(f"      C{jdx+1}: {show_ascii(p_frag)} | {p_frag.hex()}\n")