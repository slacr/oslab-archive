import sys
from subprocess import check_output as subp_co
from copy import deepcopy
from math import log
from math import sqrt

class sim_class:

    def el_one(target, other):
        ''' compute L1 norm similiarity measure '''
        summand = 0
        t_occurs = target.count
        o_occurs = other.count
        context = set(target.data.keys())
        context.update(other.data.keys())

        for con in context:
            try:
                target_con = target.data[con]/t_occurs
            except: 
                target_con = 0
            try:
                other_con = other.data[con]/o_occurs
            except:
                other_con = 0
        
            summand += abs(target_con - other_con)


        return summand
        
    def cos(target, other):
        ''' compute cosine similarity measure'''
        numerator = 0
        den0 = 0
        den1 = 0
        t_occurs = target.count
        o_occurs = other.count
        context = set(target.data.keys())
        context.update(other.data.keys())
        for con in context:
            try:
                target_con = target.data[con]/t_occurs
            except: 
                target_con = 0
            try:
                other_con = other.data[con]/o_occurs
            except:
                other_con = 0
            numerator += target_con * other_con
            den0 += target_con ** 2
            den1 += other_con ** 2
        if den0 == 0 or den1 == 0:
            return 0
        else:
            return (numerator / sqrt(den0 * den1))
            


    def skew(target, other, alpha=0.99):
        ''' compute skew similarity measure '''            
        summand = 0
        t_occurs = target.count
        o_occurs = other.count
        context = set(other.data.keys())
        for con in context:
            other_con = other.data[con]/o_occurs
            try:
                target_con = target.data[con]/t_occurs
            except: 
                target_con = 0

            summand += other_con * (log(other_con) - log((alpha * (target_con)) + ((1 - alpha) * (other_con))))

        return summand

class prole_ds:
    def __init__(self, chan_index):
        self.listwords = []
        self.wordcount = 0
        self.chan_index = chan_index

    def add_word(self, literal):
        index = len(self.listwords)
        self.listwords.append(word_obj(index, literal))
        return index

    def closest_count(self, b_count, strike):
        best = -1
        min = 1000000
        for i in [j for j in range(len(self.listwords)) if j not in strike]:
            difference = self.listwords[i].count - b_count
            if difference < min:
                min = difference
                best = i
        return best, i, self.chan_index


    def lookup(self, index):
        ''' finds and returns a word object '''
        word = self.listwords[index]
        encoded = (word.index, word.literal, word.count, word.data)
        return encoded

    def all_relns(self):
        ''' returns all unique relations in the datastructure as a list of tuples'''
        li = []
        for word in self.listwords:
            li.extend([(word.literal, other) for other in word.data.keys()])
        return li

    def get_sims(self, A_encoded, B_ptr, C_ptr, sim):
        '''this now sorts by sim'''
        A_neighbors = []
        #sim_instance = sim_class
        sim_fn = getattr(sim_class, sim)
        A_obj = word_obj(A_encoded[0], A_encoded[1], A_encoded[2], A_encoded[3])

        for i, word in enumerate(self.listwords):
            B_count = 0
            C_count = 0
            vote = 0
            append = False
            try:
                B_count = word.data[B_ptr]
                append = True
                C_count = word.data[C_ptr]
            except:
                try:
                    C_count = word.data[C_ptr]
                    append = True
                except: 
                    pass
            if B_count > C_count:
                vote = 1
            if C_count > B_count:
                vote = -1
            if append:
                assert(word.literal != A_obj.literal)
                A_neighbors.append((i, word, vote, word.literal))
            


        sim_results = [((self.chan_index,i), sim_fn(A_obj, x), vote, lit) for i,x,vote,lit in A_neighbors]
        return sim_results

    
    def exists(self, index, B):
        ''' B is a machine index pair'''
        try:
            x = self.listwords[index].data[B]
            return x
        except:
            return 0
            

    def ret_count(self, index):
        return self.listwords[index].count


class word_obj:
    def __init__(self, index, literal, count=0, data={}):
        self.index = index
        self.literal = literal
        self.count = count
        self.data = deepcopy(data)

    #takes others as a set of numbers which correspond to others
    def update(self, others):
        self.count += 1
        for other in others:
            try:
                self.data[other] += 1
            except:
                self.data[other] = 1
        return 1

    def in_data(self, candidate):
        ''' unsorted way '''
        try:
            x = self.data[candidate]
            return 1
        except:
            return 0

    
    def info(self):
        items = []
        fstring = self.literal + " occurs " + str(self.count) + " times and has " +\
                str(len(self.data.items())) + " word-friends in this context: \n"
        for x in self.data.items():
            #fstring = "\n".join([fstring, str(x)])
            items.append(x)
        return fstring, items

def check_mem():
    # NOTE: this sys.platform will fail when stops existing
    if sys.platform == "darwin":
        my_mem = str(subp_co(["top", "-l 1"]))
        x = my_mem.index("PhysMem:")
        y = my_mem[x:].index("M free")
        tmp = my_mem[x:x+y].split()
    else:    
        my_mem = str(subp_co(["free","-m"]))
        x = my_mem.index("cache:")
        y = my_mem[x:].index("\\n")
        tmp = my_mem[x:x+y].split()
    return int(tmp[-1])
    

if __name__ == "__channelexec__":
    recv = ""
    while recv is not "_DIE":
        recv = channel.receive()
        if recv[0] == "_ADD":
            literal = recv[1]
            index = my_ds.add_word(literal)
        elif recv[0] == "_UPDATE":
            index = recv[1]
            others = recv[2]
            retval = my_ds.listwords[index].update(others)
        elif recv[0] == "_MEM_AVAIL":
            channel.send(check_mem())
        elif recv[0] == "_LOOKUP":
            index = recv[1]
            channel.send(my_ds.lookup(index))
        elif recv[0] == "_INFO":
            index = recv[1]
            channel.send(my_ds.listwords[index].info())
        elif recv[0] == "_GET_SIMS":
            A_obj = recv[1]
            B_ptr = recv[2]
            C_ptr = recv[3]
            sim = recv[4]
            channel.send(my_ds.get_sims(A_obj, B_ptr, C_ptr, sim))
        elif recv[0] == "_CREATE_DS":
            chan_index = recv[1]
            my_ds = prole_ds(chan_index)
        elif recv[0] == "_ALL_RELNS":
            channel.send(my_ds.all_relns())
        elif recv[0] == "_RET_COUNT":
            channel.send(my_ds.ret_count(recv[1]))
        elif recv[0] == "_CLOSEST_COUNT":
            channel.send(my_ds.closest_count(recv[1], recv[2]))
        elif recv[0] == "_EXISTS":
            channel.send(my_ds.exists(recv[1], recv[2]))
            
if __name__ == "__main__":
    print(check_mem())
