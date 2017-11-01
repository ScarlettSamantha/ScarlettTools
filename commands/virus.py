import re
import glob
import os
import threading

from queue import Queue

class Virus:

    @classmethod
    def find(cls, file_pattern = None, regex = None):
        compress_queue = Queue()

        def check(path):
            try:
                for i, line in enumerate(open(file)):
                    for match in re.finditer(pattern, line):
                        data = list(match.groups())
                        if data[2]:
                            data[2] = data[2][:30]
                        return '!!! Found in file %s on line %s: %s' % (os.path.abspath(file), i + 1, match.groups())
            except UnicodeDecodeError:
                return '!!Read-error in %s' % os.path.abspath(file)
            except FileNotFoundError:
                pass
            return "Clean"

        def process_queue(t):
            print('Starting thread %s' % t)
            while True:
                file_data = compress_queue.get()
                r = check(file_data)
                if r is not None:
                    print('Thread %s: %s' % (t, r))
                compress_queue.task_done()

        pattern = re.compile(
            "\@?(eval|base64_decode|gzinflate)\(?(base64_decode|gzinflate|\"|')\((.+|gzinflate)\)\;"
            if regex is None else
            regex
        )

        for file in glob.glob("./**/*.php" if file_pattern is None else file_pattern, recursive=True):
            if os.path.isdir(os.path.abspath(file)):
                continue
            compress_queue.put(file)
            #yield("Checked %s" % os.path.abspath(file))

        for i in range(8*4):
            t = threading.Thread(target=process_queue, args=(i,))
            t.daemon = True
            t.start()

        compress_queue.join()

