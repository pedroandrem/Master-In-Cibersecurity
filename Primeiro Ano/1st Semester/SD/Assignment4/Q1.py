Plaintext = b"This is a message you can see the content"
KnownCiphertext = b'G\xa4\xff\xc9\x05\x15\xf6\x91\xd6\x00\xfe_k\x1e$\x93o\xdd\x1bH\xa8\xb1\x89\xc3\xfa\xac^n\xb5\xc7\x91\x9f5\x9bq7J\xafB\xecp'

Ciphertext = b'J\xa3\xe3\x9aV\x14\xea\xc4\xdbD\xb3TwM.\x9ae\x8aBS\xb5\xf8\x99\x82\xfb\xe2H'


keystream = bytes([k ^ c for k, c in zip(Plaintext,KnownCiphertext)])
plaintext2 = bytes([k ^ c for k, c in zip(Ciphertext,keystream)])

print(plaintext2)




