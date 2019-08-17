__version__ = '1.7.0'

from imports import (system, utils)
from colorama import Fore
import hashlib
import random

class HelpCommand:
    
    def __init__(self):
        self.meta = {
            'descriptor': "Lists all commands, descriptors, and parameters.",
            'params': [0,1],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        if len(args) == 0:
            terminal.out("Commands:\n")
            for command in comList:
                terminal.out(command)
            return 0
        else:
            selected = args[0]
            if selected not in comList:
                terminal.error("{} is not a command!")
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

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        tempWorkDirContents = sys.fileSystem.workDirContents.copy()
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
                terminal.out('  ' * tabs + item, Fore.MAGENTA)
                self.outDir(conts[item]['content'], tabs + 1, terminal)
            else:
                terminal.out('  ' * tabs + item, Fore.WHITE)

class ChangeDirCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Changes the current working directory to the supplied absolute or relative path.",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        path = system.FilePath(args[0], sys.fileSystem)
        if path.status == -1:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        elif path.status == -2:
            terminal.error("{} is valid but is not a directory!".format(args[0]))
            return -1
        else:
            sys.fileSystem.changeDir(path)
            return 0

class OutputCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Outputs the contents of the file at the specified path.",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        dirPath = args[0].split('/')
        path = system.FilePath('/'.join(dirPath[:-1]), sys.fileSystem)
        if path.status == -1:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        elif path.status == -2:
            terminal.error("{} is valid but is not a directory!".format(args[0]))
            return -1
        else:
            out = sys.fileSystem.output(path, dirPath[-1])
            if out is not None:
                if out == -1:
                    terminal.error("{} does not exist!".format(args[0]))
                    return -1
                elif out == -2:
                    terminal.error("{} is a directory!".format(args[0]))
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

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        connected = sysCont.getConnectedIPs(sys.IP)
        terminal.out("IP\t\tPort\tName\n")
        for item in connected:
            for i in range(random.randint(0,3)):
                terminal.out(utils.randIP() + '\t' + str(random.randint(0,99999)) + '\t' + utils.randSystemName())
            terminal.out(item + '\t' + str(random.randint(0,99999)) + '\t' +  sysCont.getName(item))
            for i in range(random.randint(0,3)):
                terminal.out(utils.randIP() + '\t' + str(random.randint(0,99999)) + '\t' +  utils.randSystemName())
        return 0

##class ConnectCommand:
##
##    def __init__(self):
##        self.meta = {
##            'descriptor': "Connects to the supplied IP.",
##            'params': [1,1],
##            'switches': None
##            }
##
##    def run(self, sysCont, sys, terminal, *args, **kwargs):
##        ret = sysCont.switchSystems(args[0])
##        if ret == -1:
##            terminal.error("Not a valid IP!")
##            return -1
##        else:
##            terminal.out(sysCont.currSystem.OSManu)
##            terminal.out("Successfully connected.")
##            return 0

##class DisconnectCommand:
##
##    def __init__(self):
##        self.meta = {
##            'descriptor': "Disconnects to your home system.",
##            'params': [0,0],
##            'switches': None
##            }
##
##    def run(self, sysCont, sys, terminal, *args, **kwargs):
##        sysCont.switchSystems(sysCont.systemDict[sysCont.userSystem].IP)
##        return 0

class ExitCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Exits the terminal.",
            'params': [0,0],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        return -99

##class AliasCommand:
##
##    def __init__(self):
##        self.meta = {
##            'descriptor': "Aliases the supplied name to the supplied command.",
##            'params': [2,2],
##            'switches': None
##            }
##
##    def run(self, sysCont, sys, terminal, *args, **kwargs):
##        if args[1] not in comList:
##            terminal.error("Command does not exist!")
##            return -1
##        elif args[0] in comList:
##            terminal.error("That is already a command!")
##            return -1
##        else:
##            comList[args[0]] = comList[args[1]]
##            return 0

class TerminalOutCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Outputs the given string.",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        terminal.out(args[0])
        return 0

class RestartCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Restarts the system.",
            'params': [0,0],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        sys.restart()
        return 0

class FileDeleteCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Deletes the specified file.",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        name = args[0].split('/')[-1]
        path = system.FilePath('/'.join(args[0].split('/')[:-1]), sys.fileSystem)
        if path.status == -1:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        elif path.status == -2:
            terminal.error("{} is valid but is not a directory!".format(args[0]))
            return -1
        else:
            contents = sys.fileSystem.getContents(path, True)
            if contents[name]['type'] == system.FileTypes.DIR:
                terminal.error("{} is a directory!".format(name))
                return -1
            else:
                del contents[name]
                return 0

class CommandController:

    def __init__(self):
        pass

    def feed(self, command, sysCont, sys, terminal):
        if command == '':
            return 0
        command = self.handleSpaces(command)
        parts = command.split('§')
        count = 0
        while count < len(parts):
            if parts[count] == '':
                del parts[count]
            else:
                count += 1
        partCommand = parts[0]
        partCommandFilename = partCommand + '.bin'
        userFileSystem = sysCont.systemDict[sysCont.userSystem].fileSystem.path
        if 'sys' not in userFileSystem:
            terminal.error("SYSTEM ERROR: CANNOT FIND SYSTEM DIRECTORY")
            return -1
        elif userFileSystem['sys']['type'] != system.FileTypes.DIR:
            terminal.error("SYSTEM ERROR: CANNOT FIND COMMAND EXECUTABLE")
            return -1
        elif 'command.sys' not in userFileSystem['sys']['content']:
            terminal.error("SYSTEM ERROR: CANNOT FIND COMMAND EXECUTABLE")
            return -1
        else:
            commandDir = userFileSystem['sys']['content']['command.sys']
            commandHash = hashlib.md5(bytes(commandDir['content'], 'ascii')).hexdigest()
            if commandHash != sysCont.sysSysData['command.sys']['hash']:
                terminal.error("SYSTEM ERROR: INVALID COMMAND EXECUTABLE")
        if 'bin' not in userFileSystem:
            terminal.error("Cannot find executable directory!")
            return -1
        elif partCommand + '.bin' not in userFileSystem['bin']['content']:
            terminal.error(partCommand + " executable cannot be found!")
            return -1
        else:
            execDir = userFileSystem['bin']['content']
            execHash = hashlib.md5(bytes(execDir[partCommandFilename]['content'], 'ascii')).hexdigest()
            if execHash not in sysCont.execHashes:
                terminal.error(partCommandFilename + " is not a valid executable file!")
                return -1
            else:
                commandName = sysCont.execHashes[execHash]
                comSwitches = comList[commandName].meta['switches']
                params = []
                switches = {}
                count = 1
                if comSwitches:
                    for part in parts[1:]:
                        if part[0] == '-':
                            if part in comSwitches:
                                switches[part] = True
                            else:
                                terminal.error("Not a valid switch!")
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
                            terminal.error("This command does not have any switches!")
                            return -1
                        else:
                            terminal.error("Switches must come before parameters!")
                            return -1
                    else:
                        params.append(part)
                    count += 1
                if len(params) < comList[commandName].meta['params'][0] or len(params) > comList[commandName].meta['params'][1]:
                    terminal.error("Incorrect number of parameters!")
                    return -1
                else:
                    return comList[commandName].run(sysCont, sysCont.systemDict[sysCont.userSystem], terminal, *params, **switches)

    def handleSpaces(self, string):
        spaceHolder = '§'
        lastQuote = None
        for count, char in enumerate(string):
            if char == '"' or char == "'":
                if not lastQuote:
                    lastQuote = char
                    string = string[:count] + '§' + string[count + 1:]
                else:
                    if lastQuote == char:
                        lastQuote = None
                        string = string[:count] + '§' + string[count + 1:]
            elif char == ' ' and not lastQuote:
                string = string[:count] + '§' + string[count + 1:]
        return string

comList = {
    'help': HelpCommand(),
    'ls': ListCommand(),
    'cd': ChangeDirCommand(),
    'cat': OutputCommand(),
    'netstat': ScanCommand(),
    'exit': ExitCommand(),
    'echo': TerminalOutCommand(),
    'restart': RestartCommand(),
    'rm': FileDeleteCommand()
    }
