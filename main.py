__version__ = 'ALPHA 2.2.2'

import sys as sysModule
import time

try:
    import colorama
except:
    print("You need the colorama module! (python -m pip install colorama)")
    sysModule.exit()

from imports import (utils, terminal, system, commands)
colorama.init()

from colorama import Fore

sysCont = system.SystemsController()
comCont = commands.CommandController()

terminal = terminal.Terminal()
terminal.out(colorama.Style.BRIGHT, colorama.Fore.GREEN, False, False)

if 'idlelib.run' in sysModule.modules:
    print("You probably want to run this from the command line.")
else:
    terminal.out("""
    ██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██╗   ██╗███████╗\n\
    ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝╚██╗ ██╔╝██╔════╝\n\
    ███████║███████║██║     █████╔╝ ███████╗ ╚████╔╝ ███████╗\n\
    ██╔══██║██╔══██║██║     ██╔═██╗ ╚════██║  ╚██╔╝  ╚════██║\n\
    ██║  ██║██║  ██║╚██████╗██║  ██╗███████║   ██║   ███████║\n\
    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝\n\
    version {}
    """.format(__version__))
    time.sleep(2)
    utils.serverBootSequence(sysCont.userSystem, terminal)

while True:
    if sysCont.userSystem.status == system.Statuses.UNBOOTABLE:
        terminal.error("ERROR: SYSTEM UNBOOTABLE")
        time.sleep(60*60*24)
    userInput = terminal.get(sysCont.userSystem.IP + sysCont.userSystem.fileSystem.getPath())
    ret = comCont.feed(userInput, sysCont, sysCont.userSystem, terminal)
    terminal.out('')
    if ret == -99:
        sysModule.exit()
    continue
 
