import multiprocessing, pickle, os

start, end = multiprocessing.Pipe()
pickle.dump(end, open("piPe", 'wb'))
x = start.recv()
print(x)
