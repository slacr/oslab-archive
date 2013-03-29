import socket, random, time

if __name__ == '__channelexec__':
    me = socket.gethostname()
    for i in range(10):
        time.sleep(random.randint(0,10))
        channel.send(me + " " + str(i))
