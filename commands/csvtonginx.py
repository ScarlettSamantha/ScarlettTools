import os

class Csvtonginx():

    def __init__(self):
        self.output = []

    @classmethod
    def convert(self, f):
        for linenum, line in enumerate(open(os.path.abspath(f))):
            store, path, source, dest, options = line.split(',')
            self.output.append(self.convertLine(source=source, dest=dest, permanent=True if options.contains('P') else False))
        self.writetofile('\r\n'.join(self.output), './output.txt')

    @classmethod
    def writetofile(cls, data, path):
        f = open(path, 'w+')
        f.truncate(0)
        f.seek(0)
        f.write(data)
        f.flush()
        f.close()


    @classmethod
    def convertLine(cls, source, dest, permanent=True):
        return 'rewrite ^/%s?(\.html)?$ /%s.html %s;' % (source, dest, 'permanent' if permanent else '')