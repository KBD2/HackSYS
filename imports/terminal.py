__version__ = '1.1.2'

import sys
import time
from colorama import Fore
import commands
class Terminal:

    def __init__(self, comCont):
        self.comCont = comCont
    
    def out(self, message, colCode=Fore.GREEN, slowWrite=True, insertNewline=True):
        assert type(message) is str # stdout only wants str
        if self.comCont.outType[0] == commands.OutTypes.TERMINAL:
            if slowWrite:
                sys.stdout.write(colCode)
                for char in message:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(0.005)
            else:
                sys.stdout.write(colCode + message)
                sys.stdout.flush()
            if insertNewline:
                sys.stdout.write('\n')
                sys.stdout.flush()
        else:
            self.comCont.outType[1].handleFileOutput(self.comCont.outType, message)
        return 0

    def get(self, start="", strip=True):
        if start != "":
            self.out(start, Fore.GREEN, True, False)
        inpChars = "> "
        self.out(inpChars, Fore.GREEN, True, False)
        self.out('', Fore.WHITE, True, False)
        message = sys.stdin.readline()
        if strip:
            message = message.strip()
        return message

    def error(self, message):
        self.out(message, Fore.RED)
        return 0
