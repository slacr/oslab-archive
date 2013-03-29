import sys
import execnet
import crack
import math
from time import sleep
from threading import Thread

# max_task_size is how long most of the spawned tasks on the proletariat machines
# will run for. generally, 200,000,000 takes roughly 27 minutes. 
# for testing purposes 20,000 suffices
max_task_size = 20000000

passwd = "zzzzz"

DONE = False
VERBOSE = False

tasks = []
chans = {}
gateways = {}
task_tracker = {}


def init():
    ''' create the cluster by add_prole for each host '''
    with open('hosts.live') as hosts:
        for line in hosts:
            line = line.split()
            for i in range(int(line[1])):
                host = line[0]
                ident = host + "_" + str(i)
                if VERBOSE: 
                    print("making gateway " + str(i) + " (ssh) to " + host)
                add_prole(ident)

def add_prole(ident):
    ''' for a given host, try to spawn the crack module on that host
    if it succeeds, add the channel to chans, the gateway to gateways
    and put this host in the task_tracker''' 

    host = ident.split("_")[0]
    try:           
        # establish connection to 'host'
        gw = execnet.makegateway("ssh="+host+"//id="+ident+"//python=python3//chdir=./execnet/crackr/")

        # run crack module on 'host'
        ch = gw.remote_exec(crack)
        ch.send((passwd, max_task_size))

        # put this chan, gw into a list of them
        chans[ident] = ch
        gateways[ident] = gw

        # task_tracker keeps track of what set of strings this machine/core
        # is working on so that if it fails these strings won't be skipped
        task_tracker[ident] = 0

        if VERBOSE: print("added " + ident)
        return 0

    except: 
        if VERBOSE: print("fail to add " + ident)
        return -1

def heartbeat():
    while not DONE:
        sleep(277)
        print("doing heartbeat()")
        for ident, gw in gateways.items():
            try:
                gw.remote_status()
            except IOError:
                if VERBOSE: print(ident + " was found to be dead by heartbeat()")
                # try to restart this prole
                error_handle(ident)


def update_proles():
    while not DONE:
        sleep(311)
        print("doing update_proles()")
        try:
            with open("hosts.live") as fi:
                for line in fi:
                    line = line.split()
                    for i in range(int(line[1])):
                        ident = line[0] + "_" + str(i)
                        if ident not in chans.keys():
                            add_prole(ident)
        except IOError as e:
            print(e.stderror)

def error_handle(ident):
    if VERBOSE:
        print("gotta remove " + ident + " fukt")
        print(ident + " was working on " + str(task_tracker[ident]))

    # whatever this prole was working on
    # put it back in the list of tasks to delegate
    if task_tracker[ident] != 0:
        tasks[:0] = [task_tracker[ident]]


    try:
        if VERBOSE: print("trying to restart gateway")
        assert(add_prole(ident)==0)
 
    except:
        del chans[ident]
        gateways[ident].exit()
        del gateways[ident]
        if VERBOSE: print("could not restart " + ident + ". sry")


def loop():
    ''' delegates tasks to proles who need something to do'''
    global chans, DONE

    chan_tmp = [x for x in chans.items()]
    for ident, ch in chan_tmp:
        if VERBOSE: print(ident, ch)
        try:
            recv = ch.receive(0.1)
            if recv[0] == 1: 
                print("match == "+str(recv[1]))
                DONE = True
            elif recv[0] == 0:
                print("last_val checked == "+str(recv[1]))
                if len(tasks) > 0: 
                    next_val = tasks.pop(0)
                    print("next == "+str(next_val))
                    ch.send(next_val)
                    task_tracker[ident] = next_val
                else:
                    task_tracker[ident] = 0
                    print("no more tasks")
            
        except ch.TimeoutError:
            if len(tasks) == 0: 
                print("no tasks")
                track_tmp = [x for x in task_tracker.items()]
                for k,v in track_tmp:
                    if v == 0:
                        ch.send("_KILL")
                        del chans[k]
                        del task_tracker[k]
                if len(task_tracker.items()) == 0:
                    DONE = True
        except:
            error_handle(ident)

def make_tasks():

    global tasks

#   for all the arrays
    for i in range(1,8):
        array = [0 for x in range(i)]
        tasks.append([x for x in array])

         # crack.l is the alphabet from which strings are created
        this_space = crack.l**i
        l_task_size = convert_l(max_task_size)
        while this_space > max_task_size:
            crack.l_inc(array, l_task_size)
            if array == -1: this_space = 0
            else:
                tasks.append([x for x in array])
                this_space -= max_task_size


def convert_l(x):
    '''where l is the langage size
       returns a base l representation of x
       used create the list of tasks'''
    l = crack.l
    i = 0
    while l**(i+1) <= x: i += 1
    result = [0 for n in range(i+1)]
    while i>0:
        p = math.floor(x / (l**i))
        x = x - ((l**i)*p)
        result[i] = p
        i -= 1
    result[0] = x
    result.reverse()
    return result


def killall():
    execnet.default_group.terminate(timeout=0.01)
    print("killed all in default group")

if __name__ == "__main__":

    try: 
        passwd = sys.argv[1]
        if len(sys.argv) > 2:
            assert(sys.argv[2] == "-v")
            VERBOSE = True
    except:
        print("usage == \n python3 bosses.py passwd [-v]")
        exit()

    # before running this program, the user should have created a 
    # hosts.live file in their current working directory using 
    # the /home/slacr/tools/mkhosts.py script


    # init() creates the cluster
    init()

    # make_tasks() breaks the search space into chunks to be
    # distributed
    make_tasks()

    update_thread = Thread(target=update_proles)
    heartbeat_thread = Thread(target=heartbeat)
    

    update_thread.start()
    heartbeat_thread.start()

    while not DONE:
        print(len(tasks))
        loop()
        sleep(10)

    update_thread.join()
    heartbeat_thread.join()

    killall()

