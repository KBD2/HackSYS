__version__ = '1.11.1'

from imports import (system, utils)
from colorama import Fore
import hashlib
import random
import json
import time
from enum import Enum

class OutTypes(Enum):
    TERMINAL = 0
    FILEOVERWRITE = 1
    FILEAPPEND = 2

class CommandController:

    '''A wrapper to make parsing, validating, and executing commands easier'''

    def __init__(self):
        self.outType = [OutTypes.TERMINAL]

    def feed(self, command, sysCont, sys, terminal):
        if command == '':
            return 0
        command = self.handleSpaces(command)
        commands = command.split('¶')
        for command in commands:
            if '|' in command:
                outputType = command.count('|')
                outputFile = command[len(command) - command[-1::-1].find('|'):]
                outputFile = ''.join(char for char in outputFile if char not in [
                    '§',
                    '"',
                    "'"
                    ])
                outputPath = system.FilePath(outputFile, sys.fileSystem, True)
                if outputPath.status not in [0, -3]:
                    terminal.error("Invalid output path!")
                    return -1
                elif outputType == 2 and outputPath.status == -3:
                    terminal.error("{} doesn't exist!".format(outputFile))
                    return -1
                else:
                    outputFileName = outputPath.iterList[-1]
                    outputDirectory = sys.fileSystem.getContents(outputPath.iterList[:-1], True)
                    if outputFileName not in outputDirectory:
                        fileType = sys.fileSystem.getFileType(outputFileName)
                        if fileType == system.FileTypes.DIR.value:
                            fileType = system.FileTypes.MSC.value
                        sys.fileSystem.make(
                            system.FilePath(
                                outputFile[:-len(outputFileName)],
                                sys.fileSystem
                                ),
                            outputFileName,
                            fileType
                            )
                        sys.addLog(sys.IP, "Created " + '/' + '/'.join(
                            outputPath.iterList
                            ))
                        sys.fileSystem.workDirContents = sys.fileSystem.getContents(sys.fileSystem.workingDirectory)
                    if outputType == 1:
                        self.outType = [OutTypes.FILEOVERWRITE, sys.fileSystem, outputPath, sys]
                    elif outputType == 2:
                        self.outType = [OutTypes.FILEAPPEND, sys.fileSystem, outputPath, sys]
                command = command[:command.find('|')]
            parts = command.split('§')
            count = 0
            while count < len(parts):
                if parts[count] == '':
                    del parts[count]
                else:
                    count += 1
            if len(parts) == 0:
                return 0
            partCommand = parts[0]
            if partCommand in sys.aliasTable:
                try:
                    return self.feed(
                        sys.aliasTable[partCommand] + ' ' + ' '.join(parts[1:]),
                        sysCont,
                        sys,
                        terminal
                        )
                except RecursionError:
                    terminal.out("Too much recursion!")
                    return -1
            partCommandFileName = partCommand + '.bin'
            userFileSystem = sysCont.userSystem.fileSystem.path
            userPath = system.FilePath(
                '/sys/command.sys',
                sysCont.userSystem.fileSystem,
                True,
                system.getSysHash('command.json')
                )
            sysPath = system.FilePath(
                '/sys/command.sys',
                sys.fileSystem,
                True,
                system.sysFileHashes['command.sys']
                )
            if sysPath.status in [-1,-2,-3,-4]:
                terminal.error("SYSTEM ERROR: CANNOT FIND COMMAND EXECUTABLE")
                return -1
            elif sysPath.status == -5:
                terminal.error("SYSTEM ERROR: INVALID COMMAND EXECUTABLE")
                return -1
            binPath = system.FilePath(
                '/bin/' + partCommandFileName,
                sys.fileSystem,
                True
                )
            if binPath.status < 0:
                terminal.error("Cannot find {} executable file!".format(partCommand))
                return -1
            else:
                execDir = sys.fileSystem.getContents(['bin'])
            execHash = hashlib.md5(
                bytes(execDir[partCommandFileName]['content'], 'ascii')
                ).hexdigest()
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
                    ret = command.run(sysCont, sys, terminal, *params, **switches)
                    if ret == 99:
                        return ret
                    else:
                        continue

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
            elif char == ';':
                if lastQuote:
                    continue
                else:
                    string = string[:count] + '¶' + string[count + 1:]
                    continue
            elif char == '>':
                if lastQuote:
                    continue
                else:
                    string = string[:count] + '|' + string[count + 1:]
                    continue
        return string

class HelpCommand:
    
    def __init__(self):
        self.meta = {
            'descriptor': "Lists all commands. When given a command, gives a de\
tailed description.",
            'params': [0,1],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        out = []
        binPath = system.FilePath('/bin', sys.fileSystem)
        if binPath.status < 0:
            terminal.error("Cannot find executables directory!")
            return -1
        else:
            foundExecs = {}
            binContents = sys.fileSystem.getContents(['bin'])
            for item in binContents:
                if binContents[item]['type'] == system.FileTypes.BIN.value:
                    execHash = hashlib.md5(
                        bytes(binContents[item]['content'], 'ascii')
                        ).hexdigest()
                    if execHash in comList:
                        foundExecs[item[:-4]] = comList[execHash]
        if len(args) == 0:
            out.append("help <command> for a more detailed description.")
            out.append("Commands:\n")
            for command in foundExecs:
                out.append(command)
            terminal.out('\n'.join(out))
            return 0
        else:
            selected = args[0]
            if selected not in foundExecs:
                terminal.error("{} is not a command!".format(selected))
                return -1
            else:
                metaData =  foundExecs[selected].meta
                out.append(args[0] + ":")
                out.append(metaData['descriptor'])
                if metaData['params'][1] - metaData['params'][0] > 0:
                    out.append("Number of parameters: {} to {}".format(
                        metaData['params'][0],
                        metaData['params'][1])
                                 )
                else:
                    out.append("Number of parameters: {}".format(
                        metaData['params'][0]
                        ))
                if metaData['switches']:
                    out.append("Switches: {}".format(
                        ', '.join(switch for switch in metaData['switches'])
                        ))
                terminal.out('\n'.join(out))
                return 0

class ListCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Lists all files and directories in the current worki\
ng directory. Use the '-r' switch to recursively list all directories.",
            'params': [0,0],
            'switches': ['-r']
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        tempWorkDirContents = sys.fileSystem.workDirContents.copy()
        if kwargs['-r']:
            out = self.outDir(tempWorkDirContents, 0, terminal, sysCont, [])
            terminal.out('\n'.join(out))
        else:
            out = []
            out.append('Type\tSize\tName\n')
            for item in tempWorkDirContents:
                if item != 'type':
                    line = system.FileTypes(tempWorkDirContents[item]['type']).name + '\t'
                    if tempWorkDirContents[item]['type'] != system.FileTypes.DIR.value:
                        if tempWorkDirContents[item]['content'] is not None:
                            line += str(len(tempWorkDirContents[item]['content']))
                        else:
                            line += '0'
                    line += '\t' + item
                    out.append(line)
            terminal.out('\n'.join(out))
        return 0

    def outDir(self, conts, tabs, terminal, sysCont, out):
        for item in conts:
            if conts[item]['type'] == system.FileTypes.DIR.value:
                out.append('  ' * tabs + item)
                out = self.outDir(conts[item]['content'], tabs + 1, terminal, sysCont, out)
            else:
                out.append('  ' * tabs + item)
        return out

class ChangeDirCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Changes the current working directory to the supplie\
d absolute or relative path.",
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
        path = system.FilePath(args[0], sys.fileSystem, True)
        name = args[0].split('/')[-1]
        pathNoFile = system.FilePath(args[0][:-len(name)], sys.fileSystem)
        if path.status < 0:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        else:
            out = sys.fileSystem.output(pathNoFile, name)
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
        out = []
        connected = sysCont.getConnectedIPs(sys.IP)
        out.append("IP\t\tPort\tName\n")
        for item in connected:
            for i in range(random.randint(0,3)):
                out.append(utils.randIP()
                             + '\t'
                             + str(random.randint(0,99999))
                             + '\t'
                             + utils.randSystemName())
            out.append(item
                         + '\t'
                         + str(random.randint(0,99999))
                         + '\t'
                         +  sysCont.getName(item))
            for i in range(random.randint(0,3)):
                out.append(utils.randIP()
                             + '\t'
                             + str(random.randint(0,99999))
                             + '\t'
                             +  utils.randSystemName())
        terminal.out('\n'.join(out))
        return 0

class ExitCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Exits the terminal.",
            'params': [0,0],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        return 99

class AliasCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Aliases the supplied name to the supplied command. A\
 string may be used to alias a more detailed command, and parameters given to th\
e alias will be added to the command. Use the '-r' switch to delete an alias.",
            'params': [1,2],
            'switches': ['-r']
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        if kwargs['-r']:
            if args[0] in sys.aliasTable:
                del sys.aliasTable[args[0]]
                return 0
            else:
                terminal.error("{} is not an alias!".format(args[0]))
                return -1
        else:
            if len(args) < 2:
                terminal.error("Incorrect number of parameters!")
                return -1
            sys.aliasTable[args[0]] = args[1]
            return 0

class TerminalOutCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Outputs the given string. Use '-c' and specify a col\
our as the first parameter to output as one of the following:\nblue\ncyan\ngree\
n\nmagenta\nred\nwhite\nyellow\nUse '-nn' to stop a newline being added.",
            'params': [1,2],
            'switches': ['-c', '-nn']
            }
        self.colours = {
            'blue': Fore.BLUE,
            'cyan': Fore.CYAN,
            'green': Fore.GREEN,
            'magenta': Fore.MAGENTA,
            'red': Fore.RED,
            'white': Fore.WHITE,
            'yellow': Fore.YELLOW
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        if kwargs['-c']:
            if len(args) != 2:
                terminal.error("Incorrect number of parameters!")
                return -1
            elif args[0] not in self.colours:
                terminal.error("{} is not a colour!".format(args[0]))
                return -1
            else:
                colour = self.colours[args[0]]
        else:
            colour = Fore.GREEN
        if kwargs['-nn']:
            insertNewline = False
        else:
            insertNewline = True
        if kwargs['-c']:
            terminal.out(args[1], colour, True, insertNewline)
        else:
            terminal.out(args[0], colour, True, insertNewline)
        return 0

class RestartCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Restarts the system.",
            'params': [0,0],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        terminal.out("Restarting...")
        sys.restart(sysCont)
        time.sleep(2)
        utils.serverBootSequence(sys, terminal)
        return 0

class FileRemoveCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Removes the specified item, use * to remove all in t\
he specified path.",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        name = args[0].split('/')[-1]
        if name == '*':
            path = system.FilePath(args[0][:-len(name)], sys.fileSystem)
        else:
            path = system.FilePath(args[0], sys.fileSystem, True)
        if path.status < 0:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        else:
            if name == '*':
                contents = sys.fileSystem.getContents(path, True)
                items = list(contents.keys())
                for item in items:
                    ret = sys.fileSystem.remove(
                        path,
                        item,
                        blacklist=[system.FileTypes.DIR.value]
                        )
                    if ret == 0:
                        terminal.out("Removed " + item)
                        if sys.fileSystem.getFileType(item) != system.FileTypes.LOG.value:
                            sys.addLog(sys.IP, "Removed " + item)
                return 0
            else:
                path = system.FilePath(args[0][:-len(name)], sys.fileSystem)
                sys.fileSystem.remove(
                    path,
                    name,
                    blacklist=[system.FileTypes.DIR.value]
                    )
                if sys.fileSystem.getFileType(name) != system.FileTypes.LOG.value:
                    sys.addLog(sys.IP, "Removed " + name)
                return 0

class FolderRemoveCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Removes the specified directory, use * to remove all\
in the specified path.",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        name = args[0].split('/')[-1]
        if name == '*':
            path = system.FilePath(args[0][:-len(name)], sys.fileSystem)
        else:
            path = system.FilePath(args[0], sys.fileSystem)
        if path.status < 0:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        else:
            if name == '*':
                contents = sys.fileSystem.getContents(path, True)
                items = list(contents.keys())
                for item in items:
                    ret = sys.fileSystem.remove(
                        path,
                        item,
                        whitelist=[system.FileTypes.DIR.value]
                        )
                    if ret == 0:
                        terminal.out("Removed " + item)
                        sys.addLog(sys.IP, "Removed " + item)
                return 0
            else:
                path = system.FilePath(args[0][:-len(name)], sys.fileSystem)
                sys.fileSystem.remove(
                    path,
                    name,
                    whitelist=[system.FileTypes.DIR.value]
                    )
                sys.addLog(sys.IP, "Removed " + name)
                return 0

class MoveCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Moves the file at the specified path to th\
e second specified path.",
            'params': [2,2],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        nameGet = args[0].split('/')[-1]
        pathTest = system.FilePath(args[0], sys.fileSystem, True)
        if pathTest.status < 0:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        pathGet = system.FilePath(args[0][:-len(nameGet)], sys.fileSystem)
        nameSet = args[1].split('/')[-1]
        pathSet = system.FilePath(args[1][:-len(nameSet)], sys.fileSystem)
        if pathSet.status < 0:
            terminal.error("{} is not a valid path!".format(args[1]))
            return -1
        ret = sys.fileSystem.move(pathGet, nameGet, pathSet, nameSet)
        sys.addLog(sys.IP, "Moved {} to {}".format(args[0], args[1]))
        return 0

class FileMakeCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Creates an empty file at the specified path.",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        name = args[0].split('/')[-1]
        makePath = system.FilePath(args[0][:-len(name)], sys.fileSystem)
        if makePath.status < 0:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        else:
            typ = sys.fileSystem.getFileType(name)
            if typ == system.FileTypes.DIR.value:
                typ = system.FileTypes.MSC.value
            ret = sys.fileSystem.make(makePath, name, typ)
            if ret == -1:
                terminal.error("{} already exists!".format(args[0]))
                return -1
            else:
                sys.addLog(sys.IP, "Created {}".format(args[0]))
            return 0

class FolderMakeCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Creates an empty folder at the specified path.",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, *args, **kwargs):
        name = args[0].split('/')[-1]
        makePath = system.FilePath(args[0][:-len(name)], sys.fileSystem)
        if makePath.status < 0:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        else:
            ret = sys.fileSystem.make(
                makePath,
                name,
                system.FileTypes.DIR.value,
                {}
                )
            if ret == -1:
                terminal.error("{} already exists!".format(args[0]))
                return -1
            else:
                sys.addLog(sys.IP, "Created {}".format(args[0]))
            return 0

def getExecHash(fileName):
    with open('data/executables/' + fileName, 'r') as file:
        fileData = json.loads(file.read())
    return fileData['hash']

def getExecContent(fileName):
    with open('data/executables/' + fileName) as file:
        fileData = json.loads(file.read())
    return fileData['content']

comList = {
    getExecHash('HelpCommand.json'): HelpCommand(),
    getExecHash('ListCommand.json'): ListCommand(),
    getExecHash('ChangeDirCommand.json'): ChangeDirCommand(),
    getExecHash('OutputCommand.json'): OutputCommand(),
    getExecHash('ScanCommand.json'): ScanCommand(),
    getExecHash('ExitCommand.json'): ExitCommand(),
    getExecHash('TerminalOutCommand.json'): TerminalOutCommand(),
    getExecHash('RestartCommand.json'): RestartCommand(),
    getExecHash('FileRemoveCommand.json'): FileRemoveCommand(),
    getExecHash('FolderRemoveCommand.json'): FolderRemoveCommand(),
    getExecHash('AliasCommand.json'): AliasCommand(),
    getExecHash('MoveCommand.json'): MoveCommand(),
    getExecHash('FileMakeCommand.json'): FileMakeCommand(),
    getExecHash('FolderMakeCommand.json'): FolderMakeCommand()
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
    'rm.bin':       'FileRemoveCommand.json',
    'rmdir.bin':    'FolderRemoveCommand.json',
    'alias.bin':    'AliasCommand.json',
    'mv.bin':       'MoveCommand.json',
    'touch.bin':    'FileMakeCommand.json',
    'mkdir.bin':    'FolderMakeCommand.json'
    }

comContent = {}
for item in comTable.values():
    comContent[item] = getExecContent(item)
