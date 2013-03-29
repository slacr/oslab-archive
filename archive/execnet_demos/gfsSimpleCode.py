import sys, socket

def execute(channel):
    host = socket.gethostname()
    channel.send(host) 
    int = channel.receive()
    channel.send(int+1)

if __name__ == "__channelexec__":
    channel.send("test")
