__version__ = 'ALPHA 1.0.1'

from imports import (terminal, system, utils, commands)
import random

systemDict = {}

IP = utils.randIP()
systemDict[IP] = system.System(IP, utils.randOSCompany())

userSystem = random.choice(list(systemDict.keys()))
currSystem = systemDict[userSystem]

terminal = terminal.Terminal()
terminal.out("Terminal Interpreter v.{}".format(__version__))

while True:
    userInput = terminal.get(currSystem.IP + currSystem.fileSystem.getPath())
    params = userInput.split(' ')
    if params[0] not in commands.comList:
        terminal.out("Not a valid command!\n")
    else:
        paramNums = len(params[1:])
        if paramNums != commands.comList[params[0]].meta['params']:
            terminal.out("Invalid number of parameters!")
        else:
            args = tuple(params[1:])
            commands.comList[params[0]].run(currSystem, terminal, systemDict, *args)
            terminal.out('')
            continue
