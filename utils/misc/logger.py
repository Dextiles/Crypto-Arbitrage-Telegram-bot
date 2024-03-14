class Logger:
    def __init__(self, filename):
        self.filename = filename
        self.logfile = None

    def __enter__(self):
        self.logfile = open(self.filename, 'a')
        return self

    def __exit__(self, type, value, traceback):
        self.logfile.close()
