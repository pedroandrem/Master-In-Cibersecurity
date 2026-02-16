import os
import json
import sys
import socketio
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


from utils.crypto_utils import KeyPair
from utils.ca_client import CertificateAuthorityClient
from utils.identity import UserIdentity
from utils.certs_db import get_or_create_cert


public_path = "server/certs/server_public.pem"


with open(public_path, "rb") as f:
    server_public_key = serialization.load_pem_public_key(f.read())


sio = socketio.Client()


class AuctionClient:
    
    def __init__(self, port: int, keypair: KeyPair, cert: str, token: str, username: str):
        self.sio = socketio.Client()
        self.port = port
        self.keypair = keypair
        self.cert = cert
        self.token = token
        self.username = username
        self._register_events()

    def refresh_timestamp(self):
        ts, ts_sig = ca.get_timestamp()
        return ts, ts_sig

    def _register_events(self):
        @self.sio.event
        def connect():
            print("Connected to auction server!")

        @self.sio.event
        def disconnect():
            print("Disconnected from server!")
            return False

        @self.sio.on("single_command")
        def on_cmd(data):
            print(f"{data['name']}: {data['description']}\nUsage: {data['usage']}")


        @self.sio.on("someone_listed")
        def on_listed(data):
            print(f"""
__BROADCAST__
New item listed:
    - Pseudo: {data['pseudonym']}
    - Id: {data['id']}
    - Name: {data['name']}
    - Description: {data['description']}
    - Closing date: {data['closing_date']}
    - Minimum bid: {data['minimum_bid']}
    - Highest bid: {data['highest_bid']}
    - Timestamp: {data['listing_timestamp']}
""")

        @self.sio.on("someone_bided")
        def on_bid(data):
            print(f"""
__BROADCAST__
    New bid made:
    - Name: {data["name"]}
    - Description: {data['description']}
    - Bid Value: {data["highest_bid"]}$
    - Timestamp: {data['biding_timestamp'][-1]}
""")

        @self.sio.on("list_confirmation")
        def list_confirmation(data):
            print(f"List confirmation: {data}")     


        @self.sio.on("bid_confirmation")
        def bid_confirmation(data):
            print(f"Bid confirmation: {data}")   
        

        @self.sio.on("item_not_available")
        def on_unavailable(data):
            print(f"The item you tried to bid is not available: {data}")


        @self.sio.on("undervalue_bid")
        def on_undervalue_bid(data):
            print(f"Bid error received: {data}") 


        @self.sio.on("timestamp_error")
        def on_timestamp_error(data):
            print(f"Timestamp error received: {data}")   


        @self.sio.on("my_listed_items")
        def my_listed_items(data):
            print("These are my listed items:", data)
        
        
        @self.sio.on("all_listed_items")
        def my_listed_items(data):
            print("These are all listed items:", data)

        
        @self.sio.on("message")
        def message(data):
            print(f"THEY ARE COMMUNICATING {data}")

        
        @self.sio.on("auction_closed")
        def on_auction_closed(data):
            room_name = data.get("room")
            self.sio.emit('room_announcement', {
                "username": self.username,
                "room": room_name,
            })

        
        @self.sio.on("room_announcement_username")
        def room_announcement_username(data):
            username = data["username"]

            print(f"Received username: {username}")







 

    def connect(self):

        self.sio.connect(
            "http://localhost:5000",
            auth={
                "client_type": "terminal",
                "listen_port": self.port,
                "jwt_token": self.token,
                "certificate": self.cert,
            },
        )

    def encrypt_command_ecies(self, server_pub_key, command: str, role: str) -> tuple[bytes, bytes]:

        message_bytes = json.dumps({"operation": command, "role": role}).encode()

        ephemeral_private = ec.generate_private_key(ec.SECP256R1())
        ephemeral_public = ephemeral_private.public_key()

        shared_secret = ephemeral_private.exchange(ec.ECDH(), server_pub_key)

        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"auction-encryption"
        ).derive(shared_secret)

        nonce = os.urandom(12)
        encryptor = Cipher(algorithms.AES(derived_key), modes.GCM(nonce)).encryptor()
        ciphertext = encryptor.update(message_bytes) + encryptor.finalize()

        encrypted_payload = nonce + encryptor.tag + ciphertext

        ephemeral_pub_bytes = ephemeral_public.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return ephemeral_pub_bytes, encrypted_payload
    

    def send_command(self, command: str):
        role = "seller" if command.startswith("/list") else "bidder" if command.startswith("/bid") else "N/A"
        sig = self.keypair.sign(command)

        ts, ts_sig = self.refresh_timestamp()

        ephemeral_pub, encrypted_command = self.encrypt_command_ecies(server_public_key, command, role)

        self.sio.emit(
            "command",
            {
                "ephemeral_pub": ephemeral_pub.decode(),
                "encrypted_command": encrypted_command.hex(),
                "signature": sig,
                "timestamp": ts,
                "timestamp_signature": ts_sig,
            },
        )

    def run(self):
        while True:
            cmd = input("").strip().lower()
            if cmd == "quit":
                print("Exiting...")
                self.sio.disconnect()
                break
            elif cmd.startswith("/"):
                self.send_command(cmd)
            else:
                print("Unknown command. Try '/list', '/bid', or 'quit'.")


if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
    except ValueError:
        print(f"Invalid port '{sys.argv[1]}'")
        sys.exit(1)

    identity = UserIdentity.from_prompt()
    keypair = KeyPair.from_identity(identity.mnemonic, identity.username)
    print(f"This is the keyaiadsad: {keypair.private_key}, {keypair.public_pem}")
    
    ca = CertificateAuthorityClient()

    cert = get_or_create_cert(identity.username, keypair.public_pem)

    token = ca.issue_token(cert)

    client = AuctionClient(port, keypair, cert, token, identity.username)
    client.connect()
    client.run()