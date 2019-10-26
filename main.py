__version__ = 'ALPHA 2.4.0'

import sys as sysModule
import time

try:
    import colorama
except:
    print("You need the colorama module! (python -m pip install colorama)")
    sysModule.exit()

sysModule.path.insert(1, './imports')
import utils, terminal, system, commands, save
system.init(system)
colorama.init()

from colorama import Fore

sysCont = save.load()
if not sysCont:
    sysCont = system.SystemsController()
#If user broke their system then quit
bootPath = system.FilePath(
    'sys/boot.sys',
    sysCont.userSystem.fileSystem,
    True,
    system.sysFileHashes['boot.sys']
    )
if bootPath.status != system.PathStatuses.PATH_VALID:
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
        while True: continue
    userInput = terminal.get(sysCont.userSystem.IP + sysCont.userSystem.fileSystem.getPath())
    ret = comCont.feed(userInput, sysCont, sysCont.userSystem, terminal)
    comCont.outType = [commands.OutTypes.TERMINAL]
    terminal.out('')
    if ret == 99:
        sysModule.exit()
    else:
        save.save(sysCont)
        continue
