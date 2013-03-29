import multiprocessing, os, pickle, time

while True:
    direc = os.listdir(os.getcwd())
    if "piPe" in direc:
        time.sleep(1)
        end = pickle.load(open("piPe","rb"))
        end.send("got it")
