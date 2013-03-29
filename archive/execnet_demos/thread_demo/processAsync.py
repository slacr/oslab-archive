import sys, execnet, time
from multiprocessing import Process

def doProc():
    
    text = "This threading example is constructed so specifically that nothing should go awry, but should it then contact your local system administrator"
    for x in text:
        print(x, end='')
        sys.stdout.flush()
        time.sleep(0.1)


hosts = open("nodes.txt")

code = "import socket, time; host = socket.gethostname(); time.sleep(int(host[-1:])); channel.send(host)"

returnOrder = []

for host in hosts:
    host = host.strip()
    print("making gateway (ssh) to "+host)
    gw = execnet.makegateway("ssh="+host+"//id="+host)

for machine in execnet.default_group:
    print("opening channel to "+machine.id)
    ch = machine.remote_exec(code)
    ch.setcallback(returnOrder.append)
    
proct = Process(target=doProc)
proct.start()
        
m = len(returnOrder)
while m<len(execnet.default_group):
    if m == len(returnOrder):
        pass
    else:
        print(returnOrder)
        m = len(returnOrder)

proct.join()
