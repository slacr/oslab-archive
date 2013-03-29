import sys
import os
import parser
import configure



def get_AB():

    '''gets all AB pairs from test data s.t. A in one and B in one'''

    c = configure.cfg(sys.argv[1])
    with open("files/test") as test_files:
        test_list = [x.strip() for x in test_files]
        test_data = parser.parse(c.dir, test_list, c.plus, c.minus, c.cluster)

    with open("files/one") as train_files:
        train_list = [x.strip() for x in train_files]
        train_data = parser.parse(c.dir, train_list, c.plus, c.minus, c.cluster)

    #could items have all the items whose keys are not in test_data removed?
    items = [x for x in test_data.hashwords.items() if x[0] in train_data.hashwords.keys()]


    with open("files/AB.tmp","w") as out:
        for A,A_ptr in items:
            A_obj = test_data.lookup(A_ptr)
            for B_ptr,count in A_obj.data.items():
                if count > 1:
                    try:
                        B = test_data.wordshash[B_ptr]
                        train_data.hashwords[B]
                        outstr = A + " " + B + "\n"
                        out.write(outstr)
                    except:
                        pass


get_AB()
