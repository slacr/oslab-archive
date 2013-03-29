import sys, hashlib, math

LOG = 0

DEBUG = False

language = [x for x in "abcdefghijklmnopqrstuvwxyz"]
l = len(language)

def l_inc(array, inc):
    '''not to be used for l<3'''
    if len(array) < len(inc): return -1
    carry = 0
    array.reverse()
    inc.reverse()
    for i in range(len(inc)):
        tmp = (array[i] + inc[i] + carry)
        array[i] = tmp % l
        carry = math.floor(tmp/l)
    while carry > 0:
        if len(array) > i+1:
            i += 1
            tmp = array[i] + carry
            carry = math.floor( tmp / l)
            array[i] = tmp % l
        else:
            print("ran out of room")
            array = -1
            return -1
    array.reverse()
    inc.reverse()
    return 0


def crack(passwd, init_val, span):
    global DEBUG
    i = 0
    while i < span:
        val_str = "".join([language[x] for x in init_val]).encode("ascii")
        hashed = hashlib.sha1(val_str).hexdigest()
        if DEBUG: print(str(val_str) + " " + hashed + " " + passwd)
        if hashed == passwd:
            if DEBUG: print("kazaa! " + str(val_str))
            return (1, val_str)
        else:
            last_val = [x for x in init_val]
            x = l_inc(init_val,[1])
            if x == -1:
                init_val = [x for x in last_val]
                return (0, init_val)

        i += 1
    return (0, init_val)

def crackr(passwd, span):
    #initial send! i am ready to start @ it!
    channel.send((0,0))
    while True:
        init_val = channel.receive()
        if init_val == "_KILL": break
        code, last_val = crack(passwd, init_val, span)
        if LOG > 1: 
            with open('log','a') as log: log.write("got "+str(code)+"\n")
        channel.send((code,last_val))
        

if __name__ == "__channelexec__":
    (passwd, span) = channel.receive()
   # if LOG > 1: 
    #    with open('log','a') as log: log.write("got "+str(passwd)+"\n")
    passwd = hashlib.sha1(passwd.encode("ascii")).hexdigest()
    crackr(passwd, span)

if __name__ == "__main__":
    #DEBUG = True
    passwd = hashlib.sha1(sys.argv[1].encode("ascii")).hexdigest()
    init_val = [int(x) for x in sys.argv[2]]
    crack(passwd, init_val, 200000000)
