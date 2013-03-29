import sys, execnet

# open hosts file to add all the cluster nodes to this program
hosts = open("nodes.txt")

# make a connection to each node, these will be added automatically to execnet.default_group

for host in hosts:
    host = host.strip()
    gw = execnet.makegateway("ssh="+host)
    
# make a list to hold the "channels" by which we receive information from th remote hosts
li = []

# code to be executed on the remote machine
code = "import socket; channel.send(socket.gethostname())"

#excecute code on each node
for machine in execnet.default_group:
    print(machine)
    li.append(machine.remote_exec(code))

# create a multi-channel connection to receive all the results at once
multi = execnet.MultiChannel(li)

#receive the results 
results = multi.receive_each()

for x in results:
    print(x)


