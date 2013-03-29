import sys
from math import log

class sim:
    def __init__(self, ds):
        self.ds = ds

    def get_neighbors(self, target):
        host, index = self.ds.hashwords[target]
        gotem = []
        all_neighbors = []

        #tell all the machines to find out if this word is 
        # in their shit

        for ch in self.ds.channels:
            ch.send(("_IN_LISTWORDS_DATA", (host, index)))
            gotem.append(ch)
        while len(gotem) > 0:
            for i in range(len(gotem)):
                try:
                    em.extend(gotem[i].receive(1))
                    del gotem[i]
                except:
                    pass


        return em

    def kNN(self, k, A, B, C, sim="el_one"):
        ''' return the k nearest neighbors of A who could vote on either
        B or C according to sim'''

        A_ptr = self.ds.hashwords[A]
        B_ptr = self.ds.hashwords[B]
        C_ptr = self.ds.hashwords[C]
        A_obj = self.ds.lookup(self.ds.hashwords[A], decode=False)
        gotem = []
        ret_sims = []

        for ch in self.ds.channels:
            ch.send(("_GET_SIMS", A_obj, B_ptr, C_ptr, sim))
            gotem.append(ch)
        while len(gotem) > 0:
            for i in range(len(gotem)):
                try:
                    ret_sims.extend(gotem[i].receive(1))
                    del gotem[i]
                except:
                    pass

        ret_sims.sort(key=lambda x: x[1])
        #print(ret_sims[0])
        
        return ret_sims[:k]

    def vote(self, li):
        b_wins = sum([x[2] for x in li])
        if b_wins>0:
            return 1
        elif (b_wins==0):
            return 0
        else:
            return -1

'''
    def vote(self, li, B, C):
        b_wins = 0
        for x in li:
            X_obj = x[0]
            B_tup = self.ds.hashwords[B]
            C_tup = self.ds.hashwords[C]
            try:
                B_occurs = X_obj.data[B_tup]
            except:
                B_occurs = 0
            try:
                C_occurs = X_obj.data[C_tup]
            except:
                C_occurs = 0
                      
            if (B_occurs > C_occurs):
                b_wins += 1
        if (b_wins > len(li)-b_wins):
            return 1
        elif (b_wins == len(li)-b_wins):
            return 0
        else:
            return -1

        


    def el_one(self, target, other):
        summand = 0
        t_occurs = target.count
        o_occurs = other.count
        context = set(target.data.keys())
        context.update(other.data.keys())
#        print("computing sim for "+target.literal+" and "+other.literal+" using "
                    #+str(len(context))+" vectors", end=":\t")
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

 #       print(summand)

        return summand
        

    def skew(self, target, other, alpha=0.99):
        summand = 0
        t_occurs = target.count
        o_occurs = other.count
        context = set(target.data.keys()).update(other.data.keys())
        for con in context:
            try:
                target_con = target.data[con]/t_occurs
            except: 
                target_con = 0
            try:
                other_con = other.data[con]/o_occurs
            except:
                other_con = 0
        
            summand += other_con * (log(other_con) - log(alpha * (target_con) +
                        (1-alpha) * (other_con)))

        return summand
'''
