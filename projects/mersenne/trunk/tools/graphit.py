#!/usr/bin/python

"""This is only a test. Attempting to graph something with matplotlib.

   It looks like plt.plot can graph all the primes filters in one graph
   so if this thing ever works I'll do that. The format is (I think)
   plt.plot(dates, values, 'attr', dates, values, 'attr', dates, values, 'attr')
"""
import primes
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

datefile = "./plot-data/llt-graph"
f = open(datefile, "r")

# ps has nothing to do with dates, classy xxx
ps =  primes.generate_primes(10000)
dates = f.read().splitlines()

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(dates, 'ro')
outputfile = ('llt.' + time.strftime('%H-%M') + '.png')
fig.savefig('./graphs/' + outputfile)
