import sys
from os.path import join as p_join
import data_structure as d
from collections import deque

def tokenize(line, use_punct=True):
    # NOTE: this tokenizer sux
     # edit: a little bit less, still doesn't account for ellipses
    if use_punct:
        punct = ["\"", "?", ";", ":", "!", "(", ")", "[", "]", "/"]
        for x in punct:
            repl = "".join([" ", x, " "])
            line = line.replace(x, repl)
    i = 0
    while i < len(line):
        if line[i] == "." or line[i] == ",":
        
            try:
                assert(line[i+1:i+2].isdigit())
            except:
                if i+1 < len(line):
                    endpiece = line[i+1:]
                else:
                    endpiece = ""
                line = line[:i] + " " + line[i] + " " + endpiece
                i += 2
        i += 1
        
    return line.lower().split()


def parse(DIR, file_list, plus, minus, cluster_file="no_cluster", init=None):

    '''parse takes:
    DIR = a working directory, ususally "/home/slacr/clean_bnc"
    file_list = a list of files to parse, i.e. train, test
    plus, minus = window size parameters
    cluster_file = machines/path-to-python pairs in a file
    init = this function can be called with a data structure to use

    parse populates the datastructure pointed to by "data" 
    with colocation data for each word in the corpus
    (i.e. for two words A and B, how often B appears within 
    a specified window of A. This may be asymmetric if the window 
    is asymmetric)'''


    doccount = 1
    if init is None:
       data = d.boss_ds(cluster_file)
    else:
        data = init

    win_size = plus + minus + 1
    win_target = minus
    window = deque([-1 for x in range(win_size)], win_size)

    # this inial population of teh window saves us from having to check 
    # if window[win_target] anymore
    with open(p_join(DIR,file_list[0])) as fi:
        for line in fi:
            for word in tokenize(line):


                data.wordcount += 1

                # this try/except statement is a fast way to 
                # know if word is in our datastructure already
                try:
                    host, index = data.hashwords[word]
                except:
                    host, index = data.add_word(word)
                    data.best_host = (data.best_host + 1) % len(data.channels)

                if window[win_target] is not -1:
                    tmpset = set([x for i,x in enumerate(window) if i is not win_target])
                    data.update(window[win_target], tmpset)

                window.append((host, index))


    # now we do the rest of the files
    for doc in file_list[1:]:

        doccount += 1
       # print("working on document " + str(doccount) + " of " + str(len(file_list)))

        # opens a file to iterate through
        with open(p_join(DIR,doc)) as fi:
            for line in fi: 
                for word in tokenize(line):
                    data.wordcount += 1
                    try:
                        host, index = data.hashwords[word]
                    except:
                        host, index = data.add_word(word)
                        data.best_host = (data.best_host+1) % len(data.channels)


                    tmpset = set([x for i,x in enumerate(window) if i is not win_target])
                    data.update(window[win_target], tmpset)

                    # move the window 1 word foward
                    window.append((host, index))

    # bookkeeping: we need to ensure that the last word is accounted for as a target word
    while window[win_target] is not -1:
        data.wordcount += 1
        tmpset = set([x for i,x in enumerate(window) if i is not win_target and x is not -1])
        data.update(window[win_target], tmpset)
        window.append(-1)
                
    
    return data


if __name__ == "__main__":
    '''this is for testing the tokenizer'''
    while True:
        print(tokenize(input("wat: ")))
