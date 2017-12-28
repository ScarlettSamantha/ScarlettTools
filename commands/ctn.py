import os
import html


class Ctn:

    DEFAULT_FILE_LOCATION = '/tmp/conversion_output.txt'
    DEFAULT_DELIMITER = ';'

    MODE_APACHE = 0
    MODE_NGINX = 1
    METHOD = "do"

    def __init__(self, file: str, output: str=None, mode: int=MODE_NGINX, delimiter: str=DEFAULT_DELIMITER, decode: bool=True) -> None:
        self.output = []
        self.file = os.path.abspath(file)
        if os.path.exists(self.file) is False:
            print('Given file %s does not exist' % self.file)
            exit(1)
        self.in_fp = None
        self.decode = decode
        self.delimiter = delimiter
        self.out_f = self.DEFAULT_FILE_LOCATION if output is None else os.path.abspath(output)
        self.in_fp = open(file, mode='r')
        self.mode = mode

    def do(self):
        self.parse_file()
        self.to_file()

    def parse_file(self) -> None:
        str_args = (self.file, self.out_f, self.delimiter, 'Apache' if self.mode is self.MODE_APACHE else 'Nginx')
        print('Taking input from %s and outputting to %s with delimiter %s in %s mode' % str_args)
        del str_args
        for i, line in enumerate(self.in_fp):
            if i == 0:
                continue
            if self.decode:
                line = html.unescape(line)
            source, destination = line.split(self.delimiter)
            self.convert_line(source=source, destination=destination, permanent=True)

    def convert_line(self, source, destination, permanent=True) -> None:
        if self.mode == self.MODE_NGINX:
            self.output.append('rewrite ^%s$ %s%s' % (source, destination.rstrip(), ' permanent;' if permanent else ';'))
        elif self.mode == self.MODE_APACHE:
            self.output.append('RewriteRule "^%s$" "%s"%s' % (source, destination.rstrip(), ' [R]' if permanent else ''))

    def to_file(self) -> None:
        f = open(self.out_f, 'w+')
        f.truncate(0)
        f.seek(0)
        f.write(os.linesep.join(self.output))
        f.flush()
        f.close()

