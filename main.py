__version__ = 'ALPHA 2.2.0'

import sys

try:
    import colorama
except:
    print("You need the colorama module! (python -m pip install colorama)")
    sys.exit()

if 'idlelib.run' in sys.modules:
    print("You probably want to run this from the command line.")

from imports import (utils, terminal, system, commands)
colorama.init()

from colorama import Fore

sysCont = system.SystemsController()
comCont = commands.CommandController()

terminal = terminal.Terminal()
terminal.out(colorama.Style.BRIGHT, colorama.Fore.GREEN, False, False)
terminal.out("Terminal Interpreter v.{}".format(__version__))

while True:
    userInput = terminal.get(sysCont.currSystem.IP + sysCont.currSystem.fileSystem.getPath())
    ret = comCont.feed(userInput, sysCont, terminal)
    terminal.out('')
    if ret == -99:
        sys.exit()
    continue
