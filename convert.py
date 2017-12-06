import os, sys

class Csvtonginx():
    SEPERATOR = ';'
    def __init__(self):
        self.output = []

    def convert(self, f):
        print(f)
        for linenum, line in enumerate(open(os.path.abspath(f))):
            if linenum == 0:
                continue
            store, path, source, dest, options = line.split(self.SEPERATOR)
            self.output.append(self.convertLine(source=source, dest=dest, permanent=True if 'P' in options else False))
        self.writetofile('\r\n'.join(self.output), '/home/arekana/output.txt')

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
        return 'rewrite ^/%s?(\.html)?$ /%s %s;' % (source, dest, 'permanent' if permanent else '')


if __name__ == '__main__':
    if sys.argv.__len__() == 1:
        print('Please give me a file to convert')
        sys.exit(1)
    c = Csvtonginx()
    c.convert(sys.argv[1])
