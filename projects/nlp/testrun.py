import sys
import parser
import updated_sims
from time import strftime, localtime, time
import os
import configure


def one_run(c, train_list, f):
    start_time = time()
    train_data = parser.parse(c.dir, train_list, c.plus, c.minus, c.cluster)

    # sim test
    sim_class = updated_sims.sim(train_data)

    for j in range(5):
        el_correct_answers = [0,0,0,0,0,0,0]
        el_ties = [0,0,0,0,0,0,0,0]
        cos_correct_answers = [0,0,0,0,0,0,0]
        cos_ties = [0,0,0,0,0,0,0,0]
        skew_correct_answers = [0,0,0,0,0,0,0,0]
        skew_ties = [0,0,0,0,0,0,0,0]
        total = 0
        kl = [10, 25, 50, 100, 200, 500, 1000]
        result_file = f + str(j) + "_" + strftime("%b%d-%H%M", localtime())
        print("bout to run this here experiment")
        with open(os.path.join("./results/", "answers_" + result_file),'w') as result_fi:
            with open(c.experiment_file + str(j), 'r') as fi:
                for line in fi:
                    A,B,C = line.split()

                    #get neighs for largest k
                    el_neighs = sim_class.kNN(kl[-1], A, B, C)
                    cos_neighs = sim_class.kNN(kl[-1], A, B, C, "cos")
                    skew_neighs = sim_class.kNN(kl[-1], A, B, C, "skew")
                    #iterate over all values of k passing  it to vote
                    for i,k in enumerate(kl):
                        el_sc_ret = sim_class.vote(el_neighs[:k])
                        cos_sc_ret = sim_class.vote(cos_neighs[:k])
                        skew_sc_ret = sim_class.vote(skew_neighs[:k])
                        if (el_sc_ret == 1):
                            el_correct_answers[i] += 1
                        elif (el_sc_ret == 0):
                            el_ties[i] += 1
                        result_fi.write(str(k) + " : " + str(el_sc_ret) + " -> " + line)
                        if (cos_sc_ret == 1):
                            cos_correct_answers[i] += 1
                        elif (cos_sc_ret == 0):
                            cos_ties[i] += 1
                        result_fi.write(str(k) + " : " + str(cos_sc_ret) + " -> " + line)
                        if (skew_sc_ret == 1):
                            skew_correct_answers[i] += 1
                        elif (skew_sc_ret == 0):
                            skew_ties[i] += 1
                        result_fi.write(str(k) + " : "  + str(skew_sc_ret) + " -> " + line)

                    total += 1

        for i,k in enumerate(kl):
            print("for k = "+str(k))
            print("eel one This machine answered " + str(el_correct_answers[i]) + " out of "+ str(total))
            print("that's " + str(el_correct_answers[i]/total) +"%")
            print("there were " + str(el_ties[i]) + " ties")
            print("******************************************************")

            print("cos This machine answered " + str(cos_correct_answers[i]) + " out of "+ str(total))
            print("that's " + str(cos_correct_answers[i]/total) +"%")
            print("there were " + str(cos_ties[i]) + " ties")
            print("******************************************************")
            
            print("skew this machine answered " + str(skew_correct_answers[i]) + " out of "+ str(total))
            print("that's " + str(skew_correct_answers[i]/total) +"%")
            print("there were " + str(skew_ties[i]) + " ties")
            print("******************************************************")

        with open(os.path.join("./results/", result_file), 'w') as out:
            out.write("using " + sys.argv[1] + " as conf file \n")
            out.write("took " + str(time() - start_time) + " seconds.\n")
            for i,k in enumerate(kl):
                out.write("\n** el one ** \n k: "+str(k)+"\ntotal: " + str(total) + "\n correct: " + 
                        str(el_correct_answers[i]) + "\n ties: " + str(el_ties[i])) 
                out.write("\n** cos ** \n k: "+str(k)+"\ntotal: " + str(total) + "\n correct: " + 
                        str(cos_correct_answers[i]) + "\n ties: " + str(cos_ties[i])) 
                out.write("\n** skew ** \n k: "+str(k)+"\n total: " + str(total) + "\n correct: " + 
                        str(skew_correct_answers[i]) + "\n ties: " + str(skew_ties[i])) 

    train_data.shutdown()


if __name__ == "__main__":
    c = configure.cfg(sys.argv[1])

    for f in os.listdir("files"):
        if f[0] != '.':
            print("Running test with " + f + " as corpus file")
            with open(os.path.join('files/',f)) as fi:
                train_list = [x.strip() for x in fi]
            one_run(c, train_list, f)
