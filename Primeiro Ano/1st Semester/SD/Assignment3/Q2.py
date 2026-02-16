
commands = [b"START",b"STOP",b"REMOVE",b"TRANSFER"]
hexfile = "hexfile.txt"

# --------- Load file ------
def hex_to_bytes(h):
    """ Remove espaços e converte hex string para bytes
        Exemplo: 1452c9f51904ffe0 = b'\x14\x52\xc9\xf5\x19\x04\xff\xe0'
         = b'\x14R\xc9\xf5\x19\x04\xff\xe0'
    """
    h = h.strip()
    return bytes.fromhex(h)

def load_hexfile(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    hexs = []
    for line in lines:
        if "-" in line:
            part = line.split("-", 1)[1].strip()
        else:
            part = line
        hexs.append(part.split()[0])  # pega primeiro token hex
    bytes_list = [hex_to_bytes(h) for h in hexs]
    return bytes_list

def xor_bytes(b1:bytes ,b2:bytes)->bytes:
    n = min(len(b1),len(b2))
    return bytes(x ^ y for x,y in zip(b1[:n], b2[:n]))

def keyvalue(dict, commands):
    list = []
    for cipher in dict[8]:
        keystream = xor_bytes(cipher, commands[3])
        list.append(keystream)
    return list

def main():
    # chaves de 4,5,6,8
    all_ciphers = load_hexfile(hexfile)
    print("----------------")
    
    filtered = {4:[],5:[],6:[],8:[],}
    for cipher in set(all_ciphers):
        if len(cipher)==4:
            filtered[4].append(cipher)
        if len(cipher)==5:
            filtered[5].append(cipher)
        if len(cipher)==6:
            filtered[6].append(cipher)
        if len(cipher)==8:
            filtered[8].append(cipher)

    print("Ciphers: ")
    for length in sorted(filtered.keys()):
        print(f"{length} bytes:")
        for c in filtered[length]:
            print("  ", c.hex())
        print()

    print("----------------")

    keystream = keyvalue(filtered,commands)

    print("Keystreams:")
    for i in keystream:
        print(i.hex())
    print("----------------")


#----------------
#Decryption Table:
#----------------
#9ae7a7b6 XOR 41875ec8d07cefea = STOP
#12d31198 XOR 400088bb4a42bab2 = STOP
#1354c7eb XOR c9b3e8e63b1ea3f7 = STOP
#1354c9e91e XOR 41875ec8d07cefea = START
#9ae7a9b46f XOR c9b3e8e63b1ea3f7 = START
#12d31f9a84 XOR 400088bb4a42bab2 = START
#13c213878639 XOR 41875ec8d07cefea = REMOVE
#9bf6a5a96d5b XOR c9b3e8e63b1ea3f7 = REMOVE
#1245c5f41c07 XOR 400088bb4a42bab2 = REMOVE
#1452c9f51904ffe0 XOR 400088bb4a42bab2 = TRANSFER
#15d51f86833aaab8 XOR 41875ec8d07cefea = TRANSFER
#9de1a9a86858e6a5 XOR c9b3e8e63b1ea3f7 = TRANSFER


if __name__ == "__main__":
    main()