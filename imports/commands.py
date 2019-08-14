__version__ = '1.1.0'

from imports import system

class HelpCommand:
    
    def __init__(self):
        self.meta = {
            'descriptor': "Lists all commands, descriptors, and parameters. Parameters: None",
            'params': 0
            }

    def run(self, sys, terminal, systemDict, *args):
        for command in comList:
            terminal.out(command + ': ' + comList[command].meta['descriptor'])
        return 0

class ListCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Lists all files and directories in the current working directory. Parameters: None",
            'params': 0
            }

    def run(self, sys, terminal, systemDict, *args):
        sys.fileSystem.listDir(terminal)
        return 0

class ChangeDirCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Changes the current working directory to the supplied absolute or relative path. Parameters: Path",
            'params': 1
            }

    def run(self, sys, terminal, systemDict, *args):
        path = system.FilePath(args[0])
        ret = sys.fileSystem.changeDir(path)
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

    def run(self, sys, terminal, systemDict, *args):
        path = system.FilePath(args[0])
        ret = sys.fileSystem.output(path)
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
    pass

comList = {
    'help': HelpCommand(),
    'ls': ListCommand(),
    'cd': ChangeDirCommand(),
    'cat': OutputCommand()
    }
