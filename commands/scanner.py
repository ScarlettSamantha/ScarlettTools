import re
import glob
import os
import multiprocessing
import time
import tqdm


class TqdmUpTo(tqdm.tqdm):
    """Provides `update_to(n)` which uses `tqdm.update(delta_n)`."""
    def update_to(self, b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)  # will also set self.n = b * bsize


class Scanner:
    FILE_FINE = 0
    FILE_DIRTY = 1
    FILE_ERROR = 2
    FILE_NOFO = 3

    MODE_LINE = 0
    MODE_FILE = 1

    definitions = []
    regexes = [
        # Not very sensitive. Nested string obfuscation.
        (r"\@?(eval|base64_decode|gzinflate)\(?(base64_decode|gzinflate|\"|')\((.+|gzinflate)\)\;",
         "(Warning: Nested-Obfusication)"),
        # Very sensitive. (@todo make less sensitive) unidoced string detection
        #(r"\\(x[0-9a-zA-Z]){0,3}", "(Notice: Unicoded strings)"),
        (r'[\@]?(define)\([\"]WSO_[a-zA-Z]*[\"]\,[\s]?[\"][0-9]*\.[0-9]*\.?[0-9]*?[\"]\);', "(Warning: WSO dectected)")
    ]

    def __init__(self):
        self.scan_queue = multiprocessing.JoinableQueue()

        self.manager = multiprocessing.Manager()

        self.message_queue = self.manager.list()
        self.matched_list = self.manager.list()

        self.non_matches = multiprocessing.Value('i', 0)
        self.matches = multiprocessing.Value('i', 0)
        self.read_errors = multiprocessing.Value('i', 0)

        self.scan_mode = self.MODE_LINE

        self.workers = []

    def scan(self, file_pattern=None):
        print('Compiling %s definitions' % self.regexes.__len__())
        self.compile_definitions()
        print('Scanning file-system for files.')
        for file in glob.glob("./**/*.php" if file_pattern is None else file_pattern, recursive=True):
            try:
                if os.path.isdir(os.path.abspath(file)) or os.path.getsize(os.path.abspath(file)) > 500000:
                    continue
            except FileNotFoundError:
                continue
            self.scan_queue.put(file)

        gui = multiprocessing.Process(target=self.gui_process)
        gui.start()

        self.message_queue.append('Found %s files' % self.scan_queue.qsize())

        threads_needed = multiprocessing.cpu_count()
        #threads_needed = 1
        self.message_queue.append('Starting %s threads' % threads_needed)

        self.workers = [multiprocessing.Process(target=self.process_queue) for _ in range(threads_needed)]
        for p in self.workers:
            p.start()

        self.scan_queue.join()
        for p in self.workers:
            p.terminate()

        time.sleep(1)

        gui.terminate()

        print('Done matches[%i], read-errors[%i], non-matches[%i]' % (self.matches.value, self.read_errors.value, self.non_matches.value))
        return

    def check(self, path):
        try:
            # To keep the scoping ok.
            f = ''
            for linenum, line in enumerate(open(path)):
                # Loop trough compiled definitions
                if self.scan_mode == self.MODE_LINE:
                    if self.scan_string(line, path, linenum) == self.FILE_DIRTY:
                        self.matches.value += 1
                elif self.scan_mode == self.MODE_FILE:
                    f += line
            if self.scan_mode == self.MODE_FILE and f is not None and f is not '':
                z = self.scan_string(f, path, None)
                if z.__len__() > 0:
                    self.matches.value += z.__len__()
        # System cant handle binary files yet.
        except UnicodeDecodeError:
            return self.FILE_ERROR
        except FileNotFoundError:
            return self.FILE_NOFO
        return self.FILE_FINE

    def scan_string(self, s, path, line=None):
        rca = []
        for r in self.definitions:
            regex, cregex, comment = r
            rmr = cregex.search(s)
            #print(rmr)
            if rmr is not None:
                self.message_queue.append('Found in %s|%s %s' % (os.path.abspath(path), line if line else '?', comment))
                rca.append(1)
        return rca

    def process_queue(self):
        while True:
            file_path = self.scan_queue.get()
            if file_path is None:
                break
            r = self.check(file_path)
            if r == self.FILE_FINE:
                self.non_matches.value += 1
            elif r in (self.FILE_NOFO, self.FILE_ERROR):
                self.read_errors.value += 1
            self.scan_queue.task_done()

    def gui_process(self):
        """
        Will render the CLI gui and keep looping until terminated or queue is empty at which point it will
        self terminate by returning a Null
        :return: void
        """
        ti = self.scan_queue.qsize()
        t = TqdmUpTo(total=self.scan_queue.qsize(), unit='Files')

        while True:
            try:
                t.update(ti - self.scan_queue.qsize())
                ti = self.scan_queue.qsize()
                if self.message_queue.__len__() > 0:
                    for m in self.message_queue:
                        TqdmUpTo.write(m)
                        self.message_queue.remove(m)
                    # We dont need more then 60fps in the terminal :P
            except BrokenPipeError:
                continue

    def compile_definitions(self):
        for r in self.regexes:
            rc, comment = r
            rco = re.compile(rc, re.IGNORECASE | re.MULTILINE)
            self.definitions.append((r, rco, comment))


if __name__ == '__main__':
    p = Scanner()
    p.scan()