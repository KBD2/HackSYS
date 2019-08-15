__version__ = '1.0.3'

import sys
import time

class Terminal:
    def out(self, message, slowWrite=True, insertNewline=True):
        assert type(message) is str # stdout only wants str
        if slowWrite:
            for char in message:
                sys.stdout.write(char)
                sys.stdout.flush()
                #time.sleep(0.01)
        else:
            sys.stdout.write(message)
            sys.stdout.flush()
        if insertNewline:
            sys.stdout.write('\n')
            sys.stdout.flush()

    def get(self, start="", strip=True):
        if start != "":
            self.out(start, True, False)
        inpChars = "> "
        self.out(inpChars, True, False)
        message = sys.stdin.readline()
        if strip:
            message = message.strip()
        return message
