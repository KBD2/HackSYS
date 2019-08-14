__version__ = '1.2.0'

from imports import system

class HelpCommand:
    
    def __init__(self):
        self.meta = {
            'descriptor': "Lists all commands, descriptors, and parameters. Parameters: None",
            'params': 0
            }

    def run(self, sysCont, terminal, *args):
        for command in comList:
            terminal.out(command + ': ' + comList[command].meta['descriptor'])
        return 0

class ListCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Lists all files and directories in the current working directory. Parameters: None",
            'params': 0
            }

    def run(self, sysCont, terminal, *args):
        sysCont.currSystem.fileSystem.listDir(terminal)
        return 0

class ChangeDirCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Changes the current working directory to the supplied absolute or relative path. Parameters: Path",
            'params': 1
            }

    def run(self, sysCont, terminal, *args):
        path = system.FilePath(args[0])
        ret = sysCont.currSystem.fileSystem.changeDir(path)
        if ret == -1:
            terminal.out("{} is not a valid path!".format(args[0]))
            return -1
        elif ret == -2:
            terminal.out("{} is valid but is not a directory!".format(args[0]))
            return -1
        else:
            return 0

class OutputCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Outputs the contents of the file at the specified path. Parameters: Path",
            'params': 1
            }

    def run(self, sysCont, terminal, *args):
        path = system.FilePath(args[0])
        ret = sysCont.currSystem.fileSystem.output(path)
        if ret == -1:
            terminal.out("{} is not a valid path!".format(args[0]))
            return -1
        elif ret == -2:
            terminal.out("{} is valid but is not a directory!".format(args[0]))
            return -1
        elif ret == -3:
            terminal.out("{} does not exist!".format(args[0]))
            return -1
        elif ret == -4:
            terminal.out("{} is a directory!".format(args[0]))
        else:
            if ret is not None:
                terminal.out(ret)
            return 0

class ScanCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Scans the current system for connected systems. Parameters: None",
            'params': 0
            }

    def run(self, sysCont, terminal, *args):
        connected = sysCont.getConnectedIPs(sysCont.currSystem.IP)
        terminal.out("Connected IPs:")
        for item in connected:
            terminal.out(item)
        return 0

class ConnectCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Connects to the supplied IP. Parameters: IP",
            'params': 1
            }

    def run(self, sysCont, terminal, *args):
        ret = sysCont.switchSystems(args[0])
        if ret == -1:
            terminal.out("Not a valid IP!")
            return -1
        else:
            terminal.out(sysCont.currSystem.OSManu)
            terminal.out("Successfully connected.")
            return 0

class DisconnectCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Disconnects to your home system. Parameters: None",
            'params': 0
            }

    def run(self, sysCont, terminal, *args):
        sysCont.switchSystems(sysCont.systemDict[sysCont.userSystem].IP)
        return 0

class ExitCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Exits the terminal. Parameters: None",
            'params': 0
            }

    def run(self, sysCont, terminal, *args):
        return -99

class AliasCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Aliases the supplied name to the supplied command. Parameters: Name, Command",
            'params': 2
            }

    def run(self, sysCont, terminal, *args):
        if args[1] not in comList:
            terminal.out("Command does not exist!")
            return -1
        else:
            comList[args[0]] = comList[args[1]]
            return 0

comList = {
    'help': HelpCommand(),
    'ls': ListCommand(),
    'cd': ChangeDirCommand(),
    'cat': OutputCommand(),
    'scan': ScanCommand(),
    'connect': ConnectCommand(),
    'disconnect': DisconnectCommand(),
    'exit': ExitCommand(),
    'alias': AliasCommand()
    }
