import sys
import execnet
import prole_client
from collections import deque
from threading import Thread
from time import time

class local_ds:

    def __init__(self):
        self.send_queue = deque()

    def send(self, recv):
        if recv[0] == "_ADD":
            literal = recv[1]
            index = self.my_ds.add_word(literal)
        elif recv[0] == "_UPDATE":
            index = recv[1]
            others = recv[2]
            retval = self.my_ds.listwords[index].update(others)
        elif recv[0] == "_MEM_AVAIL":
            self.send_queue.append(prole_client.check_mem())
        elif recv[0] == "_LOOKUP":
            index = recv[1]
            self.send_queue.append(self.my_ds.lookup(index))
        elif recv[0] == "_INFO":
            index = recv[1]
            self.send_queue.append(self.my_ds.listwords[index].info())
        elif recv[0] == "_CREATE_DS":
            chan_index = recv[1]
            self.my_ds = prole_client.prole_ds(chan_index)
        elif recv[0] == "_GET_SIMS":
            A_obj = recv[1]
            B_ptr = recv[2]
            C_ptr = recv[3]
            sim = recv[4]
            self.t = Thread(target=self.send_queue.append, args=(self.my_ds.get_sims(A_obj, B_ptr, C_ptr, sim),))
            self.t.start()
        elif recv[0] == "_ALL_RELNS":
            self.send_queue.append(self.my_ds.all_relns())
        elif recv[0] == "_RET_COUNT":
            self.send_queue.append(self.my_ds.ret_count(recv[1]))
        elif recv[0] == "_CLOSEST_COUNT":
            self.send_queue.append(self.my_ds.closest_count(recv[1], recv[2]))
        elif recv[0] == "_EXISTS":
            self.send_queue.append(self.my_ds.exists(recv[1], recv[2]))
            
    def receive(self, timeout=500):
        then = time()
        now = then
        while now - then < timeout:
            try:
                return self.send_queue.popleft()
                if self.t:
                    self.t.join()
            except:
                pass
            finally:
                now = time()


class boss_ds:
    def __init__(self, cluster_file):
        self.hashwords = {}
        self.wordshash = {}
        self.hashcount = {}
        self.channels = []
        self.hosts_count = []
        self.wordcount = 0
        self.best_host = 0

        self.cluster_init(cluster_file)
        #self.find_best_host()
        
        
    def find_best_host(self):
        best = -1
        for i, ch in enumerate(self.channels):
            ch.send(("_MEM_AVAIL",))
            tmp = ch.receive() 
            print(i, tmp)
            if tmp > best:
                best = tmp
                self.best_host = i
        print("best host = " + str(self.best_host))

    def exists(self, A, B):
        '''exists takes tuples A and B and finds if B is in A.data '''
        host, index = A
        self.channels[host].send(("_EXISTS", index, B))
        return self.channels[host].receive()

    def find_c(self, A, B):
        '''finds a word C with similar frequency to B where AC does not exist'''
        A_obj = self.lookup(self.hashwords[A])
        b_host, b_index = self.hashwords[B]
        self.channels[b_host].send(("_RET_COUNT", b_index))
        B_count = self.channels[b_host].receive()
        strike = [[] for x in range(len(self.channels))]
        gotem = []
        em = []
        for item in A_obj.data.keys():
            strike[item[0]].append(item[1])
        for i, ch in enumerate(self.channels):
            ch.send(("_CLOSEST_COUNT", B_count, strike[i]))
            em.append(ch.receive())

        em.sort(key=lambda x: x[1])
        return (em[0][2], em[0][1])



    def cluster_init(self, cluster_file):
        # init local_ds
        self.channels.append(local_ds())
        self.hosts_count.append(0)
        self.channels[0].send(("_CREATE_DS", len(self.channels) - 1))
        
        # nlp_cluster is a file of hosname, python_path pairs (so it werks on mac too)
        with open(cluster_file) as nodes:
            for node in nodes:
                hostname, py_path = node.split()
                try:
                    gw = execnet.makegateway("ssh="+hostname+"//python="+py_path)
                    self.channels.append(gw.remote_exec(prole_client))
                    self.channels[-1].send(("_CREATE_DS", len(self.channels) - 1))
                    self.hosts_count.append(0)
                except:
                    print("failed to add " + hostname)

    def lookup(self, tup, decode=True):
        host, index = tup
        self.channels[host].send(("_LOOKUP", index))
        encoded = self.channels[host].receive()
        if decode:
            decoded = prole_client.word_obj(encoded[0], encoded[1], encoded[2], encoded[3])
        else:
            decoded = encoded
        return decoded

    def info(self, literal):
        machine, index = self.hashwords[literal]
        self.channels[machine].send(("_INFO", index))
        fstring, data = self.channels[machine].receive()
        print(fstring)
        #for tup, count in data:
        #    print(self.lookup(tup), end=" ")
        #    print(count)

    def update(self, tup, others):
        self.hashcount[self.wordshash[tup]] += 1
        host, index = tup
        self.channels[host].send(("_UPDATE", index, others))


    def add_word(self, literal):
        
        count = self.hosts_count[self.best_host]
        machine = self.channels[self.best_host]
        machine.send(("_ADD", literal))
        self.hashwords[literal] = (self.best_host,count)
        self.wordshash[(self.best_host,count)] = literal
        self.hashcount[literal] = 0
        self.hosts_count[self.best_host] += 1

        return self.best_host, count

    def all_child_relns(self):
        ret = []
        for ch in self.channels:
            print("ch : " + str(self.channels.index(ch)))
            ch.send(("_ALL_RELNS",))
            ret.extend(ch.receive())

        return ret

    def create_count_list(self):
        self.sorted_counts = sorted(self.hashcount.items(), key=lambda x: x[1])
        for i, tup in enumerate(self.sorted_counts):
            self.hashcount[tup[0]] = i


    def shutdown(self):
        execnet.default_group.terminate(1)



if __name__ == "__main__":
    me = boss_ds()
    me.add_word("100")
    me.add_word("30000")
    me.add_word("100000000")
    me.add_word("birdman")
    me.update(me.hashwords["birdman"], {(0,0),(0,1)})
    print(me.lookup(me.hashwords["birdman"]))
    me.info("birdman")
