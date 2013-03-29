import sys, execnet
import remoteModule as code


hosts = open("nodes.txt")


returnOrder = []

for host in hosts:
    host = host.strip()
    print("making gateway (ssh) to "+host)
    gw = execnet.makegateway("ssh="+host+"//id="+host)

for machine in execnet.default_group:
    print("opening channel to "+machine.id)
    ch = machine.remote_exec(code)
    ch.setcallback(returnOrder.append)

print(returnOrder)
