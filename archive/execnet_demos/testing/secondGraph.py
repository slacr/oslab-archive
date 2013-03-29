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
    while msg != 'quit':
        msg = input("send this: ")
        outSock.send(bytes(msg, 'ascii'))
    outSock.close()

def sendr(list):
    msg = ''
    print(list)
    while msg != 'quit':
        msg = input('send this: ')
        if msg == 'list': print(list)
        else:
            towhom = int(input('to whom? '))
            print(towhom)
            list[towhom].send(bytes(msg, 'ascii'))

HOST=''
PORT_0=1337

listenThreads = []
s0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s0.bind((HOST, PORT_0))

msgThreads = []
try:
    nodes = open('nodes.txt')
    for node in nodes:
        node = node.strip()
        print(node)
        if node != '':
            outSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            outSock.connect((node, 1337))
            msgThreads.append(outSock)
            lisThread = threading.Thread(target=listenr, args=(msgThreads[-1], node))
            print(msgThreads[-1])
            listenThreads.append(lisThread.start())
            print("start@")
    #    startr = threading.Thread(target=connectr, args=(node,))
     #   msgThreads.append(startr.start())
    sendThread = threading.Thread(target=sendr, args=(msgThreads,))
    sendThread.start()
    nodes.close()
except:
    print("somethingfcuk")


ip = socket.gethostname()
nodes = open('nodes.txt','a')
nodes.write(str(ip) + '\n')
nodes.close()
i=0

while i < 4:
    s0.listen(4)
    conn, addr = s0.accept()
    msgThreads.append(conn)
    print ('connected by addr', addr)
    lisThread = threading.Thread(target=listenr, args=(conn, addr))
    listenThreads.append(lisThread.start())
