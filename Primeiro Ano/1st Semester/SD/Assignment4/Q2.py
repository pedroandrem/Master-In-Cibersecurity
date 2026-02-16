C1 = b'G\xa4\xff\xc9\x05\x15\xf6\x91\xd6\x00\xfe_k\x1e$\x93o\xdd\x1bH\xa8\xb1\x89\xc3\xfa\xac^n\xb5\xc7\x91\x9f5\x9bq7J\xafB\xecp'
C2 = b'J\xa3\xe3\x9aV\x14\xea\xc4\xdbD\xb3TwM.\x9ae\x8aBS\xb5\xf8\x99\x82\xfb\xe2H'
ciphertexts = [C1,C2]

def xor_bytes(a: bytes, b: bytes) -> bytes: 
    return bytes(x ^ y for x, y in zip(a, b))

def show_ascii(bs: bytes) -> str: 
    return ''.join(chr(b) for b in bs)

# We already decrypted so its easier to get some "guesses"
guesses = ["message", "no", "know", "one", "should", "You should no know this one"]


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