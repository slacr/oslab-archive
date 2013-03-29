#very simple example of how to establish a cluster and send and receive messages. Note that all nodes in 'nodes.txt' must work as this has no errorhandling
import sys, execnet

# open hosts file to add all the cluster nodes to this program
hosts = ["slacr-sleek"]

# make a connection to each node, these will be added automatically to execnet.default_group

for host in hosts:
    print("sshing into : " + host)
    gw = execnet.makegateway("ssh="+host)
    
# make a list to hold the "channels" by which we receive information from th remote hosts
channels = []

# code to be executed on the remote machine - self evident? it gets the host name of the machine on which it is run and send that bak to main d00d.
code = "import socket; channel.send(socket.gethostname())"

#excecute code on each node
for machine in execnet.default_group:
    print(machine)
    channels.append(machine.remote_exec(code))

# create a multi-channel connection to receive all the results at once
multi = execnet.MultiChannel(channels)

#receive the results 
results = multi.receive_each()

for x in results:
    print(x)


