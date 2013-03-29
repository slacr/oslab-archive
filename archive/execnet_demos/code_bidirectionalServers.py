
import sys, random, time, threading, socket

me = socket.gethostname()

def server(channel):
    for msg in channel:
        if msg == 'EOF':
            break;
        print(eval(msg))
        channel.send(me + " " + str(eval(msg)))

if __name__ == '__channelexec__':
    serv = threading.Thread(target=server, args=(channel,))
    serv.start()
    for x in range(3):
        n = random.randint(1,3)
        time.sleep(n)
        channel.send(me + str(x) + ": " + str(n))
    serv.join()
