#this example illustrates how to save network traffic by telling the remote machine to load code from the gluster file system (does this save network traffic?) Anyway, it's a good example of how to send a channel over a channel and then use that to communicate.

import sys, execnet, random


hosts = open("nodes.txt")

#chanList will hold our extra channel to each machine
chanList = []

#this code loads a module from the local file system, although ours isn't really local. meh... i'm not very excited about this code anymore.
code = "import gfsSimpleCode; chan = channel.receive(); gfsSimpleCode.execute(chan)"

for host in hosts:
    host = host.strip()
    print("making gateway (ssh) to "+host)
    gw = execnet.makegateway("ssh="+host+"//id="+host+"//chdir=execnet_examples/")
    
    chanList.append(gw.newchannel())

    

for i, machine in enumerate(execnet.default_group):
    print("opening channel to "+machine.id)
    ch = machine.remote_exec(code)
    ch.send(chanList[i])

for x in chanList:
    i = random.randint(0,10)
    print(x.receive() + " " + str(i))
    x.send(i)
    print(x.receive())
