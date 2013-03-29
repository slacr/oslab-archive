import sys, execnet, time
from multiprocessing import Process

def doProc():
    
    text = "This example is constructed so specifically that nothing should go awry, but should it then contact your local system administrator"
    for x in text:
        print(x, end='')
        sys.stdout.flush()
        time.sleep(0.1)


hosts = open("nodes.txt")

code = "import socket, random, time, subprocess; host = socket.gethostname(); time.sleep(random.randint(2,10)); retcode = subprocess.check_output(['ps']); channel.send(retcode)"

returnOrder = []

for host in hosts:
    host = host.strip()
    print("making gateway (ssh) to "+host)
    try:
        gw = execnet.makegateway("ssh="+host+"//id="+host+"//python=/usr/local/bin/python3")
    except:
        print(host + " failed \n contents of execnet.default_group = ")
        print(execnet.default_group)

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
        print()
        print(returnOrder)
        print()
        m = len(returnOrder)

proct.join()
