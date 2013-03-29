import sys
import os
import parser
import configure

def prune_AB():

    ''' from AB.tmp, remove all AB s.t. AB in ninetynine'''

    c = configure.cfg(sys.argv[1])
    with open("files/ninetynine") as files:
        lines = [x.strip() for x in files]
        nine_data = parser.parse(c.dir, lines, c.plus, c.minus, c.cluster)

    with open("files/AB.tmp") as AB:
        with open("files/AB.final","w") as out:
            for line in AB:
                A,B = line.split()
                A_ptr = nine_data.hashwords[A]
                B_ptr = nine_data.hashwords[B]
                if nine_data.exists(A_ptr, B_ptr) == 0:
                    out.write(line)

prune_AB()
