#--python
import time
import os

class Logger(object):
    def __init__(self, path='./logs'):
        self.flog_ = None
        self.clog_ = None
        self.plog_ = None
        self.slog_ = None
        self.path_ = path

    def init(self,
             file_mersenne = 'log-mersennes',       # 
             file_connections = 'log-connections',  # connection information
             file_primes = 'log-primes',            # what was concluded 
             file_summary = 'log-summary'):         # bragging log

        if not os.path.isdir(self.path_):
            os.makedirs(self.path_)

        self.flog_ = self.open_logfile(file_mersenne)
        self.clog_ = self.open_logfile(file_connections)
        self.plog_ = self.open_logfile(file_primes)
        self.slog_ = self.open_logfile(file_summary)
        self.slog("""
--------------------------------------------------------------------------------------
|  time    |  # |   p   |     M      | digitsM |    clock time   |      wall time
--------------------------------------------------------------------------------------
""")
        return self

    def flog(self, msg):
        self.LOG(self.flog_, msg)

    def clog(self, msg):
         self.LOG(self.clog_, msg)

    def plog(self, msg):
        self.LOG(self.plog_, msg)

    def slog(self, msg):
        self.LOG(self.slog_, msg)

    def open_logfile(self, filename):
        """ Open a file or error if there's an issue

        Args:
        filename: file to open
        
        Returns: f, file handle
      
        Raises: IOError if the file doesn't open
        """ 
        try:
            logname = time.strftime(filename + '.%Y%m%d')
            logpath = os.path.join(self.path_, logname)
            f = open(logpath, 'a') # open file for appending
        except IOError:
            print("Couldn't open file %s\n", logpath)
        return f

    def LOG(self, fh, msg):
        timestamp = time.strftime("%T : ")
        fh.write(timestamp + msg + "\n")
        fh.flush()
    


