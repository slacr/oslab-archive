import asyncore, socket, time, asynchat
from threading import Thread

class listenHandle(asynchat.async_chat):
    def __init__(self, sock, addr):
        asynchat.async_chat.__init__(self, sock=sock)
        self.addr = addr
        self.ibuf = ""
        self.set_terminator("/0")

    def collect_incoming_data(self, data):
        if data.decode("ascii") == "kill":
            self.close()
            exit()
        self.ibuf = self.ibuf + data

    def found_terminator(self):
        print(self.ibuf)
        self.ibuf= ""

class listener(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('',1332))
        self.listen(5)
        
    def handle_accept(self):
        conn, addr = self.accept()
        print("incoming connection from %s " % repr(addr))
        handler = listenHandle(conn, addr)


class connected(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( ('localhost', 1332) )
        self.ibuf = "first p0st EOF", "ascii"

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        print(self.recv(8192))

    def handle_write(self):
        sent = self.send(self.ibuf)
        self.ibuf = ""

    
server = listener()
client = connected()
loopthread = Thread(target=asyncore.loop)
loopthread.start()
print("this")
while True:
    inp = input("send: ")
    client.ibuf = bytes(inp, "ascii")

    if inp == "kill":
        client.close()
        server.close()
        break
loopthread.join()
