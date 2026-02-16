import os
import re
from io import StringIO
import sys
import threading
import requests
import base64
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
import jwt
import json
import time

import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend

import command
from utils import JWTValidator, CertValidator
from utils.ca_client import CertificateAuthorityClient
from utils.eciesdecryptor import ECIESDecryptor


app = Flask(__name__, static_folder='dist')
app.config['SECRET_KEY'] = 'secret!'
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading", logger=True)


items_lock = threading.Lock()
auction_items = {}

clients_lock = threading.Lock()
clients = {}


def fetch_ca_public_key(ca_url="http://127.0.0.1:9000/.well-known/ca-public") -> str:
    response = requests.get(ca_url)
    response.raise_for_status()

    data = response.json()
    if "public_key" not in data:
        raise KeyError(f"'public_key' not found in response from {ca_url}")

    return data["public_key"]


ca_public_key = fetch_ca_public_key(ca_url="http://127.0.0.1:9000/.well-known/ca-public")


@socketio.on('connect')
def handle_connect(auth):
    print(f"THIS IS THE FULL AUTH {auth}\n\n\n\n")
    token = auth.get("jwt_token")
    cert_pem = auth.get("certificate")
    ip = request.remote_addr
    listen_port = auth.get('listen_port') if auth else None
    client_type = auth.get('client_type') if auth else 'N/A'

    #if not token:
    #    print(f"Connection from {ip}:{listen_port} rejected: missing JWT")
    #    return False
    
    #try:
    #    payload = jwt.decode(token, ca_public_key, algorithms=["ES256"], audience="AuctionNetwork")
    #    jwt_info = {k: payload.get(k) for k in ("sub", "iss", "aud", "exp", "nbf", "iat", "jti")}
    #    print(f"JWT verified from {ip}:{listen_port}, issuer={jwt_info["iss"]}, subject={jwt_info["sub"]}")
    #except jwt.InvalidTokenError as e:
    #    print(f"Invalid JWT from {ip}:{listen_port}: {e}")
    #    return False

    validator = JWTValidator(
        key=ca_public_key,
        algorithms=["ES256"],
        expected_issuer="MyLocalAuctionCA",
        expected_audience="AuctionNetwork"
    )

    try:
        payload = validator.validate(token)
        print(f"JWT verified from {ip}:{listen_port}, issuer={payload["iss"]}, subject={payload["sub"]}")
    except ValueError as e:
        print(e)
        return False

    if not cert_pem:
        print(f"Connection from {ip}:{listen_port} rejected: missing CERTIFICATE")
        return False
    
    #try:
    #    cert = x509.load_pem_x509_certificate(cert_pem.encode())
    #    ca_cert_key = serialization.load_pem_public_key(ca_public_key if isinstance(ca_public_key, bytes) else ca_public_key.encode())

    #    ca_cert_key.verify(
    #        cert.signature,
    #        cert.tbs_certificate_bytes,
    #        ec.ECDSA(hashes.SHA256())
    #    )

    #    cert_cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
    #    jwt_sub = payload["sub"]

    #    if cert_cn != jwt_sub:
    #        print(f"Identity mismatch: JWT subject ({jwt_sub}) != Certificate CN ({cert_cn})")
    #        emit("command_response", {"message": "Identity mismatch between JWT and certificate"}, room=request.sid)
    #        return

    #    print(f"VERIFIED PEER \n JWT subject: {jwt_sub}\n Cert CN: {cert_cn}")

    #except InvalidSignature:
    #    print("Caught InvalidSignature")  
    #    emit("command_response", {"message": "Invalid signature or certificate"}, room=request.sid)
    #    return

    #except Exception as e:
    #    print(f"Caught generic exception: {e}")
    #    emit("command_response", {"message": f"Verification failed: {str(e)}"}, room=request.sid)
    #    return

    cert_validator = CertValidator(ca_public_key=ca_public_key)

    try:
        cert = cert_validator.validate(cert_pem, u'gruposete.mcs.uminho.pt')
        cert_cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
        print(f"VERIFIED PEER \n JWT subject: {payload['sub']}\n Cert CN: {cert_cn}")

    except InvalidSignature:
        print("Caught InvalidSignature")
        emit("command_response", {"message": "Invalid signature or certificate"}, room=request.sid)
        return False
    
    except ValueError as e:
        print(f"Certificate verification failed: {e}")
        emit("command_response", {"message": str(e)}, room=request.sid)
        return False
    
    except TypeError as e:
        print(f"Certificate type error: {e}")
        emit("command_response", {"message": "Invalid certificate input type"}, room=request.sid)
        return False
    
    public_key_pem = cert.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    with clients_lock:
        clients[request.sid] = {
            "type": client_type,
            "ip": ip,
            "port": listen_port,
            "payload": {
                "iss": payload["iss"],
                "sub": payload["sub"],
                "aud": payload["aud"],
                "exp": payload["exp"],
                "nbf": payload["nbf"],
                "iat": payload["iat"],
                "jti": payload["jti"],
            },
            "cert_cn": cert_cn,
            "certificate": cert.public_bytes(serialization.Encoding.PEM).decode(),  
            "public_key": public_key_pem, 
        }

    print(f"{clients}")
    print()
    print(f"New connection from {ip}:{listen_port} ({client_type})")
    emit("connected", {"message": f"Connected as {client_type}"})

# {
#   'cZoYe4V7zYqHPTplAAAB': 
#   {
#       'type': 'terminal',     
#       'ip': '127.0.0.1', 
#       'port': 6001,
#       'payload': 
#       {
#           'iss': 'MyLocalAuctionCA', 
#           'sub': '1ae6ac0b5f3fbb3fbace91148d2e5347ef9bf4b2753800f6e73136dc33a3ce36', 
#           'aud': 'AuctionNetwork', 
#           'exp': 1763983166, 
#           'nbf': 1763979566, 
#           'iat': 1763979566, 
#           'jti': '1616aa41-725a-487f-9f55-19f32020731b'
#       }, 
#       'cert_cn': 'gruposete.mcs.uminho.pt', 
#       'certificate': '-----BEGIN CERTIFICATE-----\nMIIBkTCCATigAwIBAgIUScz3DY0jjy4DLZvkLPsS6qxakEowCgYIKoZIzj0EAwIw\nGzEZMBcGA1UECgwQTXlMb2NhbEF1Y3Rpb25DQTAeFw0yNTExMjQxMDE5MjRaFw0y\nNjExMjQxMDE5MjRaMGUxCzAJBgNVBAYTAlBUMQ4wDAYDVQQIDAVCcmFnYTEOMAwG\nA1UEBwwFQnJhZ2ExFDASBgNVBAoMC1AyUCBBdWN0aW9uMSAwHgYDVQQDDBdncnVw\nb3NldGUubWNzLnVtaW5oby5wdDBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABE7N\nob6JgYMqa4oH3+t1e5FnjfTxVHVxPpGpDB0HoI8Hx3G6xX+4gcR5xu6XuKk5JQwv\nz4kBhw4j0MvE3kFQWUujEDAOMAwGA1UdEwEB/wQCMAAwCgYIKoZIzj0EAwIDRwAw\nRAIgVx85Yf+7Uc0G4QBV28k+DSqrR64ImS66DMXf6FfI3bgCIB+PNjNAtEV2lEEn\naHihC30DbyhjPE0pbx12d9rvJn10\n-----END CERTIFICATE-----\n', 
#       'public_key': '-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAETs2hvomBgyprigff63V7kWeN9PFU\ndXE+kakMHQegjwfHcbrFf7iBxHnG7pe4qTklDC/PiQGHDiPQy8TeQVBZSw==\n-----END PUBLIC KEY-----\n'
#   }, 
#
#   'm3R3cSYs1ji9BeQnAAAD': 
#   {   
#       'type': 'terminal', 
#       'ip': '127.0.0.1', 
#       'port': 6002, 
#       'payload':
#       {
#           'iss': 'MyLocalAuctionCA', 
#           'sub': 'fba536ecf44aa4ca97b7dd81aafcad780d58f577939b684d5683313f9c7b01eb', 
#           'aud': 'AuctionNetwork', 
#           'exp': 1763983191, 
#           'nbf': 1763979591, 
#           'iat': 1763979591, 
#           'jti': '51185a2e-6c37-4329-bcdd-8b6add68b6ac'
#       }, 
#       'cert_cn': 'gruposete.mcs.uminho.pt', 
#       'certificate': '-----BEGIN CERTIFICATE-----\nMIIBkTCCATigAwIBAgIUf85PaV8m2uO34nuvrk7kYli4VMwwCgYIKoZIzj0EAwIw\nGzEZMBcGA1UECgwQTXlMb2NhbEF1Y3Rpb25DQTAeFw0yNTExMjQxMDE5NDlaFw0y\nNjExMjQxMDE5NDlaMGUxCzAJBgNVBAYTAlBUMQ4wDAYDVQQIDAVCcmFnYTEOMAwG\nA1UEBwwFQnJhZ2ExFDASBgNVBAoMC1AyUCBBdWN0aW9uMSAwHgYDVQQDDBdncnVw\nb3NldGUubWNzLnVtaW5oby5wdDBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABPcu\nBivpYFapIIZZLzVwIdJUeYfIIGeKu7xaj/uULSBU5cULITxuCqeve1COiQKmGn0G\nb7EaTWcNHI6K2j8Z/1yjEDAOMAwGA1UdEwEB/wQCMAAwCgYIKoZIzj0EAwIDRwAw\nRAIgbS/dTqyRd8ebxu39PT5WUpV0L1wFxvhUu7sJwa+nCoACIBf0mMPVP7m3JJyZ\nCn31YrqAD5xAXajV5/U8NiMAxs5j\n-----END CERTIFICATE-----\n', 
#       'public_key': '-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE9y4GK+lgVqkghlkvNXAh0lR5h8gg\nZ4q7vFqP+5QtIFTlxQshPG4Kp697UI6JAqYafQZvsRpNZw0cjoraPxn/XA==\n-----END PUBLIC KEY-----\n'}
#}


@socketio.on('disconnect')
def handle_disconnect():
    with clients_lock:
        client = clients.pop(request.sid, None)
    if client:
        client_type = client["type"] or "N/A"
        ip = client["ip"]
        port = client["port"]
        print(f"Disconnected: {client_type} ({ip}:{port})")


#@socketio.on('webrtc_offer')
#def webrtc_offer(data):
#    target_sub = data.get("to_sub")
#    with clients_lock:
#        target_sid = next((sid for sid, info in clients.items() if info["payload"]["sub"] == target_sub), None)
#        if target_sid:
#            emit("webrtc_offer", {
#                "from_sub": clients[request.sid]["payload"]["sub"],
#                "sdp": data["sdp"],
#                "type": data["type"]
#            }, room=target_sid)


#@socketio.on('webrtc_answer')
#def webrtc_answer(data):
#    target_sub = data.get("to_sub")
#    with clients_lock:
#        target_sid = next((sid for sid,info in clients.items() if info["payload"]["sub"] == target_sub), None)
#    if target_sid:
#        emit("webrtc_answer", {
#            "from_sub": clients[request.sid]["payload"]["sub"],
#            "sdp": data["sdp"],
#            "type": data["type"]
#        }, room=target_sid)


#@socketio.on('ice_candidate')
#def ice_candidate(data):
#    target_sub = data.get("to_sub")
#    with clients_lock:
#        target_sid = next((sid for sid,info in clients.items() if info["payload"]["sub"] == target_sub), None)
#    if target_sid:
#        emit("ice_candidate", {
#            "from_sub": clients[request.sid]["payload"]["sub"],
#            "candidate": data["candidate"]
#        }, room=target_sid)     


command_list = [
    command.ListCommand([]),
    command.BidCommand([]),
    command.MyItemsCommand([]),
    command.AllItemsCommand([]),
]

help_cmd = command.HelpCommand(command_list + [])  # temporary empty list; will add help_cmd itself next

command_list.append(help_cmd)

commands = command_list

decryptor = ECIESDecryptor("server/certs/server_private.pem")


@socketio.on("command")
def handle_command(data):
    
    ephemeral_pub = data.get("ephemeral_pub")
    encrypted_command = data.get("encrypted_command")

    if not ephemeral_pub or not encrypted_command:
        emit("command_response", {"message": "Missing encrypted command"}, room=request.sid)
        return

    try:
        decrypted_data = decryptor.decrypt(ephemeral_pub, encrypted_command)
        operation = decrypted_data.get("operation", "").strip()
        role = decrypted_data.get("role", "").strip()
    except Exception as e:
        emit("command_response", {"message": f"Decryption failed: {str(e)}"}, room=request.sid)
        return

    if not operation:
        emit("command_response", {"message": "Empty operation"}, room=request.sid)
        return


    client_info = clients.get(request.sid)
    print(f"This is the client info: {client_info}")
    if not client_info:
        emit("comamnd_response", {"message": "Unknown client"}, room=request.sid)

    peer_sub = client_info["payload"].get("sub")   
    peer_public_key_pem = client_info.get("public_key")

    peer_public_key = serialization.load_pem_public_key(
        peer_public_key_pem.encode()
    )

    signature_hex = data.get("signature")

    if not signature_hex:
        emit("command_response", {"message": "Missing signature"}, room=request.sid)
        return
    
    timestamp = data.get("timestamp")
    timestamp_signature = data.get("timestamp_signature")

    if not timestamp or not timestamp_signature:
        emit("command_response", {"message": "Missing timestamp or timestamp signature"}, room=request.sid)

    print("IM HERE")
    
    try:
        signature_bytes = bytes.fromhex(signature_hex)

        peer_public_key.verify(
            signature_bytes,
            operation.encode(),
            ec.ECDSA(hashes.SHA256())
        )

        print(f"VERIFIED COMMAND from {peer_sub}: {operation}")

    except InvalidSignature:
            print(f"Invalid signature or certificate for peer: {peer_sub}")
            emit("command_response", {"message": "Invalid signature or certificate"}, room=request.sid)
            return

    except Exception as e:
            print(f"Signature verification error: {str(e)}")
            emit("command_response", {"message": f"Verification failed: {str(e)}"}, room=request.sid)
            return
    

    try:
        timestamp_bytes = timestamp.encode()
        timestamp_sig_bytes = bytes.fromhex(timestamp_signature)

        ca_pub_key_obj = serialization.load_pem_public_key(ca_public_key.encode())
        ca_pub_key_obj.verify(
            timestamp_sig_bytes,
            timestamp_bytes,
            ec.ECDSA(hashes.SHA256())
        )

        print(f"Verified trusted timestamp: {timestamp}")

    except InvalidSignature:
        print(f"Invalid timestamp signature from peer: {peer_sub}")
        emit("command_response", {"message": "Invalid timestamp signature"}, room=request.sid)
        return

    except Exception as e:
        print(f"Timestamp verification error: {str(e)}")
        emit("command_response", {"message": f"Timestamp verification failed: {str(e)}"}, room=request.sid)
        return



    match = re.match(r'^/(\w+)\s*(.*)', operation)
    if not match:
        emit(f"command_response", {"message": "Commands must start with '/'"}, room= request.sid)
        return

    operation_name = match.group(1)
    operation_args = match.group(2).split() if match.group(2) else []

    cmd = next((c for c in commands if c.name == operation_name), None)
    if cmd:
        buffer = StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer
        print("Before try")
        try:
            if operation_name in ["list", "bid",]:
                cmd.execute(
                    operation_args,
                    peer_sub=peer_sub,
                    role=role,
                    room=request.sid,
                    private_emit_func=lambda event, msg, room=None:  emit(event, msg, to=room),
                    emit_func=lambda event, msg, broadcast=False: emit(event, msg, broadcast=broadcast),
                    lock = items_lock,
                    auction_items = auction_items,
                    timestamp = timestamp
                )
            elif operation_name in ["help", "myitems", "allitems"]:
                cmd.execute(
                    operation_args,
                    peer_sub=peer_sub,
                    room=request.sid,
                    emit_func=lambda event, msg, room=None:  emit(event, msg, to=room),
                    lock=items_lock,
                    auction_items=auction_items,
                )
            #elif operation_name == "sendmessage": #sendmessage from=<> to=<>
            #    if role == "admin": 
            #        cmd.execute(
            #            operation_args,
            #            emit_func=lambda event, msg, to=None: emit(event, msg, room),
            #            lock = clients_lock,
            #            clients = clients
            #        )
            #    else:
            #        return False
            else:
                cmd.execute(operation_args, room=request.sid)
        finally:
            sys.stdout = sys_stdout

        # emit("command_response", {"message": buffer.getvalue()}, room=request.sid)
    else:
        emit("command_response", {"message": f"Unknown command: {operation_name}"}, room=request.sid)


@socketio.on("room_announcement")
def handle_room_announcement(data):
    room = data["room"]
    username = data["username"]

    socketio.emit("room_announcement_username", {"username": username}, room=room)



def auction_monitor():
    ca = CertificateAuthorityClient()
    with app.app_context():
        while True:
            ca_ts, _ca_sig = ca.get_timestamp()
            now = datetime.datetime.fromisoformat(ca_ts)
            items_to_process = []

            with items_lock:
                items_to_process = [
                    (item_name, item) 
                    for item_name, item in list(auction_items.items()) 
                    if now >= item.closing_date
                ]


            print(f"THIS IS THE ITEM CLOSED LIST: {[name for name, _ in items_to_process]}")

            for item_name, item in items_to_process:
                room_name = f"auction_{item_name}"
                print(f"THIS IS THE ROOM NAME: {room_name}")

                seller_sid = None
                buyer_sid = None
                with clients_lock:
                    for sid, info in clients.items():
                        if info["payload"]["sub"] == item.seller:
                            seller_sid = sid
                        if info["payload"]["sub"] == item.buyer:
                            buyer_sid = sid

                if seller_sid:
                    socketio.server.enter_room(seller_sid, room_name)

                if buyer_sid:
                    socketio.server.enter_room(buyer_sid, room_name)


                socketio.emit("auction_closed", {
                    "room": room_name,
                }, room=room_name)

            with items_lock:
                for item_name, _ in items_to_process:
                    if item_name in auction_items:
                        del auction_items[item_name]
                               

            time.sleep(10)



if __name__ == "__main__":

    socketio.start_background_task(auction_monitor)

    socketio.run(app, host="0.0.0.0", port=5000)