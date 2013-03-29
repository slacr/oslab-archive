#this exemplifies how to send python objects like modules, but is that worth it? compare to gfsSimple.py

import sys, execnet
import remoteModule as code


hosts = open("nodes.txt")


returnOrder = []

for host in hosts:
    host = host.strip()
    print("making gateway (ssh) to "+host)
    try:
        gw = execnet.makegateway("ssh="+host+"//id="+host+"//python=python3")
    except:
        print(host + " failed \n contents of execnet.default_group = ")
        print(execnet.default_group)

for machine in execnet.default_group:
    print("opening channel to "+machine.id)
    ch = machine.remote_exec(code)
    ch.setcallback(returnOrder.append)
    
print(returnOrder)
