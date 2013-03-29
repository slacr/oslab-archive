#bs_splitter.py version 0.9.1
#use: python3 bs_splitter.py file "experiment name" [outdir]
# if outdir is not given, ./bs_splitter_output will be used

import sys, os

num = 0
outdir = "bs_splitter_output"

def parse(step):
    step = step.split()
    stepDict = {}
    for x in step:
        x = x.split('"')
        if len(x) >= 2:
            key = x[0][:-1]
            stepDict[key] = x[1]
    return stepDict
            

def stepToEnum(experiment, filestring):
    global num
    start = experiment.find("<stepp")
    if start == -1:
        num += 1
        outName = os.path.join(outdir, filestring)
        with open(outName, "w") as fi:
            experiment = '<?xml version="1.0" encoding="us-ascii"?>\n<!DOCTYPE experiments SYSTEM "behaviorspace.dtd">\n<experiments>\n' + experiment + '\n</experiments>'
            fi.write(experiment)
    else:
        end = experiment[start:].find("/>")+start+2
        di = parse(experiment[start:end])
        while di["first"] <= (di["last"] + di["step"]):
            formalString = '\n<enumeratedValueSet variable="{0}"><value value="{1}"/></enumeratedValueSet>\n'.format(di["variable"], di["first"])
            nexperiment = experiment[:start] + formalString + experiment[end:]
            nfilestring = filestring + "_" + di["variable"] + "-" + di["first"]
            di["first"] = str(eval(di["first"]+ " + " + di["step"]))
            stepToEnum(nexperiment, nfilestring)

if __name__ == "__main__":        
    try: 
            with open(sys.argv[1], 'r') as f:
                f = f.read()
            exp = f.find("<experiments>")
            f = f[exp:]
            tag = f.find(sys.argv[2])
            if(tag > 0):
                f = f[(tag-20):]
                end = f.find("</experiment>") + 13
                f = f[:end]
                print(f)

                y = input("yes?")

                

                try:
                    outdir = sys.argv[3]
                except:
                    pass

                if not os.path.exists(outdir):
                    try:
                        os.mkdir(outdir)
                    except:
                        print("error creating output directory :(\n")
                        exit(1)
                else:
                    if not os.path.isdir(outdir):
                        print("output directory is already used as a filename, no good\n")
                        exit(1)

                stepToEnum(f, "splitted_" + sys.argv[1])
            else:
                print("experiment " + sys.argv[2] + " not found.\n")
    except:
        print('\n\nimproper invocation. to use, type\n\tpython3 bs_splitter.py file "experiment name" [outdir]\n\nif no outdir is given, output will be placed in ./bs_splitter_output/\n')

