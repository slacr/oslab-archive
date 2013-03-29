class cfg:
    def __init__(self, fi):
        with open(fi) as f:
            for line in f:
                line = line.strip().split("=")
                try:
                    x = int(line[1])
                except:
                    try:
                        x = float(line[1])
                    except:
                        x = line[1]
                setattr(self,line[0],x)


