import argparse
import os
import hashlib
import secrets

# Path for file_shadow
file_shadow = "file_shadow"

# Create and verify file_shadow
"""
def create_shadow_file():
    try:    
        with open("file_shadow", "x"):
            print("file_shadow criado com sucesso!")
    except FileExistsError:
        print("O ficheiro file_shadow já existe!")
"""

def load_shadow():
    shadow = {}
    if os.path.exists(file_shadow):
        with open(file_shadow, "r") as f:
            for line in f:
                line = line.strip()
                if ":" in line:
                    path, hash_value = line.split(":",1)
                    shadow[path] = hash_value # hash e salt
    return shadow

def save_shadow(shadow):
    with open(file_shadow, "w") as f:
        for path, hash_value in shadow.items():
            f.write(f"{path}:{hash_value}\n")
    os.chmod(file_shadow, 0o600)


def secure_sha256(path,salt):
    file_path = os.path.expanduser(path)

    with open(file_path, "rb") as f:
        data = f.read()
    
    hash_value = hashlib.sha256(salt + data).hexdigest()
    return hash_value


def protect(files):
    shadow =load_shadow()
    for file_path in files:
        salt = secrets.token_bytes(16)
        abs_path = os.path.abspath(file_path)
        hash_value = secure_sha256(abs_path,salt)
        if hash_value:
            shadow[abs_path] = f"{hash_value}:{salt.hex()}"
    save_shadow(shadow)

def update(files):
    shadow = load_shadow()
    for file_path in files:
        salt = secrets.token_bytes(16)
        abs_path = os.path.abspath(file_path)
        if abs_path not in shadow:
            print(f"Not monitored: {abs_path}")
            continue
        hash_value = secure_sha256(abs_path,salt)
        if hash_value:
            shadow[abs_path] = f"{hash_value}:{salt.hex()}"
            print(f"{abs_path} is updated in file_shadow")
    save_shadow(shadow)

def verify(files):
    shadow = load_shadow()
    for file_path in files:
        abs_path = os.path.abspath(file_path)
        if abs_path not in shadow:
            print(f"Not monitored: {abs_path}")
            continue
        else:
            stored_hash_value, salt_hex = shadow[abs_path].split(":")
            salt = bytes.fromhex(salt_hex)
            hash_value = secure_sha256(abs_path,salt)
            if hash_value == stored_hash_value:
                print("Everything intact!")
            else:
                print(f"ALERT: Unauthorized modification -> {abs_path}")


def main():
    parser = argparse.ArgumentParser(description="Monitor file integrity with hash + salt")
    parser.add_argument("command", choices=["protect", "update", "verify"], help="Command to execute")
    parser.add_argument("files", nargs="+", help="List of files to process")
    
    args = parser.parse_args()
    
    cmd = args.command
    files = args.files  # já é lista de strings

    if cmd == "protect": 
        protect(files)
    elif cmd == "update":
        update(files)
    elif cmd == "verify":
        verify(files)
    else:
        print("Invalid command")

if __name__ == "__main__":
    main()
