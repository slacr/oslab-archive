import execnet, sys, threading, time
from random import randint, random
import code_bidirectionalServers as code

def server(chan):
    for msg in chan:
        print(msg)

hosts = []

for line in open("nodes.txt"):
    hosts.append(line.strip())

chanList = []
servList = []

for host in hosts:
    print("making gateway (ssh) to "+host)
    gw = execnet.makegateway("ssh="+host+"//id="+host+"//python=python3")

for machine in execnet.default_group:
    print("opening channel to "+machine.id)
    ch = machine.remote_exec(code)
    chanList.append(ch)

for ch in chanList:
    serv = threading.Thread(target=server, args=(ch,))
    servList.append(serv.start())

for i in range(3):
    n = randint(0,len(hosts)-1)
    node = hosts[n]
    time.sleep(randint(0,3))
    chanList[n].send(str(random()) + ' + ' + str(random()))
    
for ch in chanList:
    ch.send('EOF')
