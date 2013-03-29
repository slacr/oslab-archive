#This example creates a process which demonstrates a way to receive messages from other nodes while still doing work on the master machine

import sys, execnet, time
from multiprocessing import Process

#this is our process: a teletype which prints a message 1 char @ a time
def doProc():
    
    text = "This threading example is constructed so specifically that nothing should go awry, but should it then contact your local system administrator"
    for x in text:
        print(x, end='')
        sys.stdout.flush()
        time.sleep(0.1)


#the code being sent waits for a random number of seconds between 0 and 10, then sends the hostname of the machine on which it runs to the master
code = "import socket, time, random; host = socket.gethostname(); time.sleep(random.randint(0,10)); channel.send(host)"


#this familiar block of code initializes teh cluster and sends code to each machine
#___________________
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
#______________________    

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
