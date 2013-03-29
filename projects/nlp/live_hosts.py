import sys
import subprocess

def main():
    works = []
    with open(sys.argv[1]) as fi:
        for host in fi:
            host = host.strip()
            try:
                x = subprocess.check_output(['ssh', host,'-o', 'BatchMode=yes', 'which python3'])
                host = host + " " + x.decode()
                works.append(host)
            except:
                pass
    with open(sys.argv[2],'w') as out:
        for worker in works:
            out.write(worker)

if __name__ == "__main__":
    main()

