#!/usr/bin/env python
import os

class Tail(object):
    def __init__(self, fname, max_size=1000000):
        self.fname = os.path.abspath(fname)
        self.max_size = max_size
        self.file = None
        self.pos = 0
        self.buf = ''
        self._reopen(False)

    def _open_or_none(self, fname):
        try:
            return open(fname)
        except:
            return None

    def _reopen(self, start):
        if self.file:
            self.file.close()
        self.file = self._open_or_none(self.fname)
        self.pos = 0
        if self.file and not start:
            self.pos = os.fstat(self.file.fileno()).st_size

    def __iter__(self):
        if not self.file:
            self._reopen(True)
        try:
            need_reopen = not os.path.samestat(os.fstat(self.file.fileno()), os.stat(self.fname))
        except:
            need_reopen = True
        if self.file:
            newpos = os.fstat(self.file.fileno()).st_size
            if newpos > self.pos + self.max_size:
                self.pos = newpos
                self.buf = ''
                return
            self.file.seek(self.pos)
            if self.buf:
                self.buf += self.file.readline()
            if self.buf.endswith('\n') or len(self.buf) > self.max_size:
                yield self.buf
                self.buf = ''
            line = None
            for line in self.file:
                if line.endswith('\n'):
                    yield line
            if line and not line.endswith('\n'):
                self.buf = line
            self.pos = self.file.tell()
        if need_reopen:
            self._reopen(True)

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

if __name__ == '__main__':
    import sys
    import time
    tail = Tail(sys.argv[1])
    while True:
        time.sleep(0.1)
        for line in tail:
            sys.stdout.write(line)
            sys.stdout.flush()
