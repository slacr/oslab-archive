import sys, math

language = [x for x in "abcdefghijklmnopqrstuvwxyz"]
l = len(language)

def l_inc(array, inc):
    '''not to be used for l>3'''
    if len(array) < len(inc): return -1
    carry = 0
    array.reverse()
    inc.reverse()
#    print("array.reverse " + str(array))
#    print("inc.reverse = " + str(inc))
    for i in range(len(inc)):
        tmp = (array[i] + inc[i] + carry)
        array[i] = tmp % l
        carry = math.floor(tmp/l)
#        print(array, carry, l)
    while carry > 0:
        if len(array) > i+1:
            i += 1
#            print("i is : " + str(i))
            tmp = array[i] + carry
            carry = math.floor( tmp / l)
            array[i] = tmp % l
#            print(array, carry, l)
        else:
            print("ran out of room")
            array = -1
            return -1
    array.reverse()
    inc.reverse()
    return 0

