__version__ = '1.4.1'

from imports import system
from colorama import Fore

class HelpCommand:
    
    def __init__(self):
        self.meta = {
            'descriptor': "Lists all commands, descriptors, and parameters.",
            'params': [0,1],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        if len(args) == 0:
            terminal.out("Commands:\n")
            for command in comList:
                terminal.out(command)
            return 0
        else:
            selected = args[0]
            if selected not in comList:
                terminal.out("{} is not a command!")
                return -1
            else:
                metaData =  comList[args[0]].meta
                terminal.out(args[0] + ":")
                terminal.out(metaData['descriptor'])
                if metaData['params'][1] - metaData['params'][0] > 0:
                    terminal.out("Number of parameters: {} to {}".format(metaData['params'][0], metaData['params'][1]))
                else:
                    terminal.out("Number of parameters: {}".format(metaData['params'][0]))
                if metaData['switches']:
                    terminal.out("Switches: {}".format(', '.join(switch for switch in metaData['switches'])))

class ListCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Lists all files and directories in the current working directory.",
            'params': [0,0],
            'switches': ['-r']
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        tempWorkDirContents = sysCont.currSystem.fileSystem.workDirContents.copy()
        if kwargs['-r']:
            self.outDir(tempWorkDirContents, 0, terminal)
        else:
            terminal.out('Type\tSize\tName\n')
            for item in tempWorkDirContents:
                if item != 'type':
                    line = system.FileTypes(tempWorkDirContents[item]['type']).name + '\t'
                    if tempWorkDirContents[item]['type'] != system.FileTypes.DIR:
                        line += str(len(tempWorkDirContents[item]['content']))
                    line += '\t' + item
                    terminal.out(line)
        return 0

    def outDir(self, conts, tabs, terminal):
        for item in conts:
            if conts[item]['type'] == system.FileTypes.DIR:
                terminal.out('\t' * tabs + item, Fore.MAGENTA)
                self.outDir(conts[item]['content'], tabs + 1, terminal)
            else:
                terminal.out(' ' * tabs + item, Fore.WHITE)

class ChangeDirCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Changes the current working directory to the supplied absolute or relative path.",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        path = system.FilePath(args[0], sysCont.currSystem.fileSystem)
        if path.status == -1:
            terminal.out("{} is not a valid path!".format(args[0]), Fore.RED)
            return -1
        elif path.status == -2:
            terminal.out("{} is valid but is not a directory!".format(args[0]), Fore.RED)
            return -1
        else:
            sysCont.currSystem.fileSystem.changeDir(path)
            return 0

class OutputCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Outputs the contents of the file at the specified path.",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        dirPath = args[0].split('/')
        path = system.FilePath('/'.join(dirPath[:-1]), sysCont.currSystem.fileSystem)
        if path.status == -1:
            terminal.out("{} is not a valid path!".format(args[0]), Fore.RED)
            return -1
        elif path.status == -2:
            terminal.out("{} is valid but is not a directory!".format(args[0]), Fore.RED)
            return -1
        else:
            out = sysCont.currSystem.fileSystem.output(path, dirPath[-1])
            if out is not None:
                if out == -1:
                    terminal.out("{} does not exist!".format(args[0]), Fore.RED)
                    return -1
                elif out == -2:
                    terminal.out("{} is a directory!".format(args[0]), Fore.RED)
                    return -1
                else:
                    terminal.out(out)
                    return 0

class ScanCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Scans the current system for connected systems.",
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
            'descriptor': "Connects to the supplied IP.",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        ret = sysCont.switchSystems(args[0])
        if ret == -1:
            terminal.out("Not a valid IP!", Fore.RED)
            return -1
        else:
            terminal.out(sysCont.currSystem.OSManu)
            terminal.out("Successfully connected.")
            return 0

class DisconnectCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Disconnects to your home system.",
            'params': [0,0],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        sysCont.switchSystems(sysCont.systemDict[sysCont.userSystem].IP)
        return 0

class ExitCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Exits the terminal.",
            'params': [0,0],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        return -99

class AliasCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Aliases the supplied name to the supplied command.",
            'params': [2,2],
            'switches': None
            }

    def run(self, sysCont, terminal, *args, **kwargs):
        if args[1] not in comList:
            terminal.out("Command does not exist!", Fore.RED)
            return -1
        elif args[0] in comList:
            terminal.out("That is already a command!", Fore.RED)
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
            terminal.out("Command does not exist!", Fore.RED)
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
                                terminal.out("Not a valid switch!", Fore.RED)
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
                        terminal.out("This command does not have any switches!", Fore.RED)
                        return -1
                    else:
                        terminal.out("Switches must come before parameters!", Fore.RED)
                        return -1
                else:
                    params.append(part)
                count += 1
            if len(params) < comList[partCommand].meta['params'][0] or len(params) > comList[partCommand].meta['params'][1]:
                terminal.out("Incorrect number of parameters!", Fore.RED)
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
