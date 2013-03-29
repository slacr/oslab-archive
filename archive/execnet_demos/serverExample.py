import sys, execnet, random, threading
import serverExampleCode as code

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
    gw = execnet.makegateway("ssh="+host+"//id="+host)

for machine in execnet.default_group:
    print("opening channel to "+machine.id)
    ch = machine.remote_exec(code)
    chanList.append(ch)

for ch in chanList:
    serv = threading.Thread(target=server, args=(ch,))
    servList.append(serv.start())

while True:
    pass
