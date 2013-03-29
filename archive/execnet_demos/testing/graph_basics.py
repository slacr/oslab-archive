import socket, threading

def listenr(conn, addr):
    while True:
        data = conn.recv(1024)
        if not data: break
        print(data.decode('ascii'), addr)

def connectr(host):
    outSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    outSock.connect((host, 1337))
    msg = ''
    while input != 'quit':
        msg = input("send this: ")
        outSock.send(bytes(msg, 'ascii'))
    outSock.close()

HOST=''
PORT_0=1337

s0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s0.bind((HOST, PORT_0))

msgThreads = []
nodes = open('nodes.txt')
for node in nodes:
    node = node.strip()
    if node != '':
        startr = threading.Thread(target=connectr, args=(node,))
        msgThreads.append(startr.start())

ip = socket.gethostbyname(socket.gethostname())
nodes.close()
nodes = open('nodes.txt','a')
nodes.write(str(ip) + '\n')
nodes.close()
i=0
listenThreads = []

while i < 4:
    s0.listen(4)
    conn, addr = s0.accept()
    print ('connected by addr', addr)
    lisThread = threading.Thread(target=listenr, args=(conn, addr))
    listenThreads.append(lisThread.start())
