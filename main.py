__version__ = 'ALPHA 2.0.0'

from imports import (utils, terminal, system, commands)
import sys


sysCont = system.SystemsController()

terminal = terminal.Terminal()
terminal.out("Terminal Interpreter v.{}".format(__version__))

while True:
    userInput = terminal.get(sysCont.currSystem.IP + sysCont.currSystem.fileSystem.getPath())
    params = userInput.split(' ')
    if params[0] not in commands.comList:
        terminal.out("Not a valid command!\n")
    else:
        paramNums = len(params[1:])
        if paramNums != commands.comList[params[0]].meta['params']:
            terminal.out("Invalid number of parameters!")
        else:
            args = tuple(params[1:])
            ret = commands.comList[params[0]].run(sysCont, terminal, *args)
            terminal.out('')
            if ret == -99:
                sys.exit()
            continue
