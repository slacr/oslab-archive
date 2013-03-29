import sys
import os
import parser
import configure
from random import shuffle


if __name__ == "__main__":
    #make datastructures
    c = configure.cfg(sys.argv[1])
    with open("test_corpus") as test_files:
        test_list = [x.strip() for x in test_files]
        test_data = parser.parse(c.dir, test_list, c.plus, c.minus)

    with open("files/one") as train_files:
        train_list = [x.strip() for x in train_files]
        one_data = parser.parse(c.dir, train_list, c.plus, c.minus)


    with open("files/ninetynine") as train_files:
        train_list = [x.strip() for x in train_files]

        nine_data = parser.parse(c.dir, train_list, c.plus, c.minus, c.cluster)

    # only words that exist in one_data
    items = [x for x in test_data.hashwords.items() if x[0] in one_data.hashwords.keys()]


    one_data.create_count_list()

    ABC_list = []
    for A,A_ptr in items:
        A_obj = test_data.lookup(A_ptr)
        for B_ptr,count in A_obj.data.items():
            if count > 1:
                try:
                    B = test_data.wordshash[B_ptr]
                    one_data.hashwords[B]


                    A_ptr = nine_data.hashwords[A]
                    B_ptr = nine_data.hashwords[B]
                    if nine_data.exists(A_ptr, B_ptr) == 0:

                        # here we have a valid AB pair s.t. A,B in one_data and AB not in nine_data

                        
                        B_count_index = one_data.hashcount[B]
                        done = False
                        i = 1
                        while not done:
                            if B_count_index+i >= len(one_data.sorted_counts):
                                break
                            p_C = one_data.sorted_counts[B_count_index+i][0]
                            if test_data.exists(A_ptr, test_data.hashwords[p_C]) == 0:
                                if nine_data.exists(nine_data.hashwords[A], nine_data.hashwords[p_C]) == 0:
                                    done = True
                            i += 1
                        if done:
                            ABC_list.append((A,B,p_C))

                        done = False
                        i = 1
                        while not done:
                            if B_count_index-i < 0:
                                break
                            p_C = one_data.sorted_counts[B_count_index-i][0]
                            if test_data.exists(A_ptr, test_data.hashwords[p_C]) == 0:
                                if nine_data.exists(nine_data.hashwords[A], nine_data.hashwords[p_C]) == 0:
                                    done = True
                            i += 1
                        if done:
                            ABC_list.append((A,B,p_C))

                except:
                    pass

    shuffle(ABC_list)
    x = len(ABC_list)//5
    y = 0
    for i in range(5):
        with open(c.testfile + str(i),"w") as out:
            for A,B,C in ABC_list[y:y+x]:
                out.write(A + " " + B + " " + C + "\n")
        y = y+x

