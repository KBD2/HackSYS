__version__ = '1.8.0'

from imports import (system, utils)
from colorama import Fore
import hashlib
import random
import json

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
                terminal.error("{} is not a command!".format(selected))
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

class ExitCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Exits the terminal.",
            'params': [0,0],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        return -99

class AliasCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Aliases the supplied name to the supplied command.",
            'params': [2,2],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        sys.aliasTable[args[0]] = args[1]
        return 0

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
            if name not in contents:
                terminal.error("{} does not exist!".format(name))
                return -1
            elif contents[name]['type'] == system.FileTypes.DIR:
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
        if partCommand in sys.aliasTable:
            try:
                return self.feed(sys.aliasTable[partCommand] + ' ' + ' '.join(parts[1:]), sysCont, sys, terminal)
            except RecursionError:
                terminal.out("Too much recursion!")
                return -1
        partCommandFileName = partCommand + '.bin'
        userFileSystem = sysCont.userSystem.fileSystem.path
        workSysWorkDirCont = sys.fileSystem.getContents(sys.fileSystem.workingDirectory)
        sysPath = system.FilePath('/sys', sys.fileSystem)
        if sysPath.status < 0:
            terminal.error("SYSTEM ERROR: CANNOT FIND SYSTEM DIRECTORY")
            return -1
        elif 'command.sys' not in userFileSystem['sys']['content']:
            terminal.error("SYSTEM ERROR: CANNOT FIND COMMAND EXECUTABLE")
            return -1
        else:
            commandDir = sys.fileSystem.path['sys']['content']['command.sys']
            commandHash = hashlib.md5(bytes(commandDir['content'], 'ascii')).hexdigest()
            if commandHash != sysCont.sysSysData['command.sys']['hash']:
                terminal.error("SYSTEM ERROR: INVALID COMMAND EXECUTABLE")
                return -1
        currBinPath = system.FilePath('/bin', sys.fileSystem)
        userBinPath = system.FilePath('/bin', sysCont.userSystem.fileSystem)
        if currBinPath.status < 0:
            found = False
        elif partCommandFileName not in sys.fileSystem.getContents(['bin']):
            found = False
        elif sys.fileSystem.getContents(['bin'])[partCommandFileName]['type'] != system.FileTypes.BIN:
            found = False
        else:
            found = True
            execDir = sys.fileSystem.getContents(['bin'])
        if not found:
            if userBinPath.status < 0:
                terminal.error("Cannot find executable file!")
                return -1
            elif partCommandFileName not in sys.fileSystem.getContents(['bin']):
                terminal.error("Cannot find executable file!")
                return -1
            elif sys.fileSystem.getContents(['bin'])[partCommandFileName]['type'] != system.FileTypes.BIN:
                terminal.error("Cannot find executable file!")
                return -1
            else:
                execDir = sysCont.userSystem.getContents(['bin'])
        execHash = hashlib.md5(bytes(execDir[partCommandFileName]['content'], 'ascii')).hexdigest()
        if execHash not in comList:
            terminal.error(partCommandFilename + " is not a valid executable file!")
            return -1
        else:
            command = comList[execHash]
            comSwitches = command.meta['switches']
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
            if len(params) < command.meta['params'][0] or len(params) > command.meta['params'][1]:
                terminal.error("Incorrect number of parameters!")
                return -1
            else:
                return command.run(sysCont, sys, terminal, *params, **switches)

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

def getHash(fileName):
    with open('data/executables/' + fileName) as file:
        fileData = json.loads(file.read())
    return fileData['hash']

def getContent(fileName):
    with open('data/executables/' + fileName) as file:
        fileData = json.loads(file.read())
    return fileData['content']

comList = {
    getHash('HelpCommand.json'): HelpCommand(),
    getHash('ListCommand.json'): ListCommand(),
    getHash('ChangeDirCommand.json'): ChangeDirCommand(),
    getHash('OutputCommand.json'): OutputCommand(),
    getHash('ScanCommand.json'): ScanCommand(),
    getHash('ExitCommand.json'): ExitCommand(),
    getHash('TerminalOutCommand.json'): TerminalOutCommand(),
    getHash('RestartCommand.json'): RestartCommand(),
    getHash('FileDeleteCommand.json'): FileDeleteCommand(),
    getHash('AliasCommand.json'): AliasCommand()
    }

#For use when making a system
comTable = {
    'help.bin':     'HelpCommand.json',
    'ls.bin':       'ListCommand.json',
    'cd.bin':       'ChangeDirCommand.json',
    'cat.bin':      'OutputCommand.json',
    'netstat.bin':  'ScanCommand.json',
    'exit.bin':     'ExitCommand.json',
    'echo.bin':     'TerminalOutCommand.json',
    'restart.bin':  'RestartCommand.json',
    'rm.bin':       'FileDeleteCommand.json',
    'alias.bin':    'AliasCommand.json'
    }
