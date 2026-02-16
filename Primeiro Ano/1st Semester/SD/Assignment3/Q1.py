import os

def encrypt(cleartext: str, keystream: bytes) -> bytes:
    text = cleartext.encode()
    result = bytes([x ^ y for x, y in zip(text,keystream)])
    return result


def decrypt(ciphertext:bytes, keystream: bytes) -> str:
    # Operação XOR
    text = bytes([c ^ k for c,k in zip(ciphertext,keystream)]) 
    result = text.decode() # Passa de bytes a str
    return result

def key_generator(plaintext:str):
    key = os.urandom(len(plaintext))
    return key

def main():

    plaintext = 'OLAMUNDO'
    key = key_generator(plaintext)
    print("Key: "+ str(key))
    print()
    print("Mensagem Encriptada: " + str(encrypt(plaintext,key)))
    print()
    print("Mensagem Desencriptada: " + decrypt((encrypt(plaintext,key)),key))
    print()



if __name__ == "__main__":
    main()