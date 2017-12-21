import os
import html


class Ctn:

    @classmethod
    def convert(cls, i_file: str, output: str=None, delimiter: str=';', decode: bool=True):
        c = cls(i_file, output, delimiter, decode)
        c.parse_file()
        c.to_file()

    def __init__(self, file: str, output: str=None, delimiter: str=';', decode: bool=True):
        self.output = []
        self.file = os.path.abspath(file)
        self.in_fp = None
        self.decode = decode
        self.delimiter = delimiter
        self.out_f = '/tmp/conversion_output.txt' if output is None else output
        self.in_fp = open(file, mode='r')

    def parse_file(self) -> None:
        print('Taking input from %s and outputing to %s with delimiter %s' % (self.file, self.out_f, self.delimiter))
        for i, line in enumerate(self.in_fp):
            if i == 0:
                continue
            if self.decode:
                line = html.unescape(line)
            source, destination = line.split(self.delimiter)
            self.convert_line(source=source, destination=destination, permanent=True)

    def convert_line(self, source, destination, permanent=True) -> None:
        self.output.append('rewrite ^%s$ %s%s' % (source, destination.rstrip(), ' permanent;' if permanent else ';'))

    def to_file(self) -> None:
        f = open(self.out_f, 'w+')
        f.truncate(0)
        f.seek(0)
        f.write('\r\n'.join(self.output))
        f.flush()
        f.close()
