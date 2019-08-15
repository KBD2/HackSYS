__version__ = '1.3.1'

from imports import system

class HelpCommand:
    
    def __init__(self):
        self.meta = {
            'descriptor': "Lists all commands, descriptors, and parameters. Parameters: None",
            'params': [0,1],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        for command in comList:
            terminal.out(command + ': ' + comList[command].meta['descriptor'])
        return 0

class ListCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Lists all files and directories in the current working directory. Parameters: None",
            'params': [0,0],
            'switches': ['-r']
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        sysCont.currSystem.fileSystem.listDir(terminal)
        return 0

class ChangeDirCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Changes the current working directory to the supplied absolute or relative path. Parameters: Path",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        path = system.FilePath(args[0], sysCont.currSystem.fileSystem)
        if path.status == -1:
            terminal.out("{} is not a valid path!".format(args[0]))
            return -1
        elif path.status == -2:
            terminal.out("{} is valid but is not a directory!".format(args[0]))
            return -1
        else:
            sysCont.currSystem.fileSystem.changeDir(path)
            return 0

class OutputCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Outputs the contents of the file at the specified path. Parameters: Path",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        dirPath = args[0].split('/')
        path = system.FilePath('/'.join(dirPath[:-1]), sysCont.currSystem.fileSystem)
        if path.status == -1:
            terminal.out("{} is not a valid path!".format(args[0]))
            return -1
        elif path.status == -2:
            terminal.out("{} is valid but is not a directory!".format(args[0]))
            return -1
        elif path.status == -3:
            terminal.out("{} does not exist!".format(args[0]))
            return -1
        elif path.status == -4:
            terminal.out("{} is a directory!".format(args[0]))
        else:
            out = sysCont.currSystem.fileSystem.output(path, dirPath[-1])
            if out is not None:
                terminal.out(out)
            return 0

class ScanCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Scans the current system for connected systems. Parameters: None",
            'params': [0,0],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        connected = sysCont.getConnectedIPs(sysCont.currSystem.IP)
        terminal.out("Connected IPs:")
        for item in connected:
            terminal.out(item)
        return 0

class ConnectCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Connects to the supplied IP. Parameters: IP",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
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
            'params': [0,0],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        sysCont.switchSystems(sysCont.systemDict[sysCont.userSystem].IP)
        return 0

class ExitCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Exits the terminal. Parameters: None",
            'params': [0,0],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        return -99

class AliasCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Aliases the supplied name to the supplied command. Parameters: Name, Command",
            'params': [2,2],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        if args[1] not in comList:
            terminal.out("Command does not exist!")
            return -1
        elif args[0] in comList:
            terminal.out("That is already a command!")
            return -1
        else:
            comList[args[0]] = comList[args[1]]
            return 0

class CommandController:

    def __init__(self):
        pass

    def feed(self, command, sysCont, terminal):
        parts = command.split(' ')
        partCommand = parts[0]
        if partCommand not in comList:
            terminal.out("Command doesn't exist!")
            return -1
        else:
            comSwitches = comList[partCommand].meta['switches']
            params = []
            switches = {}
            count = 1
            if comSwitches:
                for part in parts[1:]:
                    if len(part) == 0:
                        continue
                    else:
                        if part[0] == '-':
                            if part in comSwitches:
                                switches[part] = True
                            else:
                                terminal.out("Not a valid switch!")
                                return -1
                        else:
                            break
                    count += 1
                for switch in comSwitches:
                    if switch not in switches:
                        switches[switch] = False
            for part in parts[count:]:
                if len(part) == 0:
                    continue
                elif part[0] == '-':
                    if not comSwitches:
                        terminal.out("This command does not have any switches!")
                        return -1
                    else:
                        terminal.out("Switches must come before parameters!")
                        return -1
                else:
                    params.append(part)
                count += 1
            if len(params) < comList[partCommand].meta['params'][0] or len(params) > comList[partCommand].meta['params'][1]:
                terminal.out("Incorrect number of parameters!")
                return -1
            else:
                return comList[partCommand].run(sysCont, terminal, *params, **switches)

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
