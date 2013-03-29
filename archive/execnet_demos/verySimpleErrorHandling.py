#very simple example of how to establish a cluster and send and receive messages with error handling. All code is the same as verySimple.py unless otherwise noted
import sys, execnet
hosts = open("nodes.txt")

#this is different! This loop, pay attn!
#_______________________________________
for host in hosts:
    #your nodes.txt shouldn't have any extra whitespace, but just in case
    host = host.strip()

    #printing the ip of the machine is good for knowing what the computer is doing
    print("making gateway (ssh) to "+host)

    #this try/except statement makes sure our ssh connection worked.
    try:
        #here we add an id field to our gateway object for easier reference in the future
        #also we ensure that our nodes are running python3 so they can execute the python3 code we send them
        gw = execnet.makegateway("ssh="+host+"//id="+host+"//python=python3")

    #if the above command fails this code will execute and the master program will continue to run w/o the failed node
    except:
        print(host + " failed \n contents of execnet.default_group = ")

        #printing is a good way to know what nodes are in your default_group. note that the failed node is not because it failed.

        print(execnet.default_group)

#_____________________________

channels = []

code = "import socket; channel.send(socket.gethostname())"

for machine in execnet.default_group:
    print(machine)
    channels.append(machine.remote_exec(code))

multi = execnet.MultiChannel(channels)
results = multi.receive_each()

for x in results:
    print(x)


