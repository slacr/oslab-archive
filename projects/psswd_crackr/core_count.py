import sys

def get_core_count():
    with open('/proc/cpuinfo') as fi:
        for line in fi:
            print(line)
            if line.find("cores")>0:
                line = line.split(":")
                return line[1].strip()
    return 1

print(get_core_count())
