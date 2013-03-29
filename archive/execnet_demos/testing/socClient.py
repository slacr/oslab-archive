import socket

HOST='10.14.3.155'
PORT=50155
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send(b'Test')
data = s.recv(1024)
print('Received: ', data)
s.send(b'Test2')
data = s.recv(1024)
print('Received: ', data)
