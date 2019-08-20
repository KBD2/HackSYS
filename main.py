__version__ = 'ALPHA 2.3.0'

import sys as sysModule
import time

try:
    import colorama
except:
    print("You need the colorama module! (python -m pip install colorama)")
    sysModule.exit()

from imports import (utils, terminal, system, commands, save)
colorama.init()

from colorama import Fore

sysCont = system.SystemsController()
#If user broke their system then quit
bootPath = system.FilePath(
    'sys/boot.sys',
    sysCont.userSystem.fileSystem,
    True,
    system.sysFileHashes['boot.sys']
    )
if bootPath.status < 0:
    sysCont.userSystem.status = system.Statuses.UNBOOTABLE
comCont = commands.CommandController()

terminal = terminal.Terminal(comCont)
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
    comCont.outType = [commands.OutTypes.TERMINAL]
    terminal.out('')
    if ret == 99:
        sysModule.exit()
    else:
        save.save(sysCont)
        continue
 
