import socket
import json

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.137.16", 12345)) 



def send(key,value):
    d = {key: value}

    client.sendall(json.dumps(d).encode("utf-8"))

    if key == "1":
        response = client.recv(1024).decode("utf-8")
        return response
    if key == "2":
        response = client.recv(1024).decode("utf-8")
        return response
    
    
    else:
        return False

while True:
    key=input()
    value=input()
    print(send(key,value))