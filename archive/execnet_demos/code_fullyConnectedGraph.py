from threading import Thread
from socket import gethostname
import execnet



if __name__ == '__channelexec__':
    if gethostname() == 'slacr-40':
        gw = execnet.makegateway("ssh=10.14.3.144//id=other//python=python3")
    while True:
        pass
