__version__ = 'ALPHA 2.1.0'

from imports import (utils, terminal, system, commands)
import sys


sysCont = system.SystemsController()
comCont = commands.CommandController()

terminal = terminal.Terminal()
terminal.out("Terminal Interpreter v.{}".format(__version__))

while True:
    userInput = terminal.get(sysCont.currSystem.IP + sysCont.currSystem.fileSystem.getPath())
    ret = comCont.feed(userInput, sysCont, terminal)
    terminal.out('')
    if ret == -99:
        sys.exit()
    continue
