import socket 
import threading 
import queue 

messages = queue.Queue()
clients = []


# Create UDP sockets bound to port 9999
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
server.bind(("localhost", 9999))

# Stores messages in queue 
def receive(): 
    while True:
        try: 
            message, addr = server.recvfrom(1024)
            messages.put((message,addr))
        except: 
            pass

# Takes the messages from the queue for every client
def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            print(message.decode())
            if addr not in clients:
                clients.append(addr)
            for client in clients:
                try:
                    if message.decode().startswith("SIGNUP_TAG:"):
                        name = message.decode()[message.decode().index(":")+1]
                        server.sendto(f"{name} joined!".encode(), client)
                    else:
                        server.sendto(message,client)
                except:
                    client.remove(client)


t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()                