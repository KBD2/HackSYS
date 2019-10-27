__version__ = '1.14.1'

import system, utils
from colorama import Fore
import hashlib
import random
import json
import time
from enum import Enum
import os
import copy
import re

class CommandStatuses(Enum):
    COMMAND_VALID = 0
    COMMAND_INVALID = 1
    INVALID_NO_OUTFILE = 2
    INVALID_ORDER_OUT = 3
    INVALID_ORDER_SWITCH = 4
    INVALID_MULTIPLE_OUT = 5

class Command:

    switchRegex = re.compile('-[a-zA-Z0-9]+')
    singleQuoteRegex = re.compile('(\'.*?\')')
    doubleQuoteRegex = re.compile('\".*?\"')
    outputRegex = re.compile('>{1,2}')
    miscRegex = re.compile('[^\s\'\"]+')
    partsRegex = re.compile('(-[^\s\'\"]+)|(\".*?\")|(\'.*?\')|>{1,2}|([^\s\'\"]+)')

    def __init__(self, rawCommand):
        self.command = ""
        self.switches = []
        self.args = []
        self.outFile = None
        self.outType = None
        state = 0
        for c, item in enumerate(re.finditer(self.partsRegex, rawCommand)):
            itemStr = item.group()
            switchMatch = self.switchRegex.match(itemStr)
            miscMatch = self.miscRegex.match(itemStr)
            singleMatch = self.singleQuoteRegex.match(itemStr)
            doubleMatch = self.doubleQuoteRegex.match(itemStr)
            outMatch = self.outputRegex.match(itemStr)
            if c == 0:
                if miscMatch:
                    self.command = itemStr
                    state = 1
                else:
                    self.status = CommandStatuses.COMMAND_INVALID
                    return
            elif switchMatch:
                if state != 1:
                    self.status = CommandStatuses.INVALID_ORDER_SWITCH
                    return
                self.switches.append(itemStr)
            elif outMatch:
                if state not in [1,2]:
                    self.status = CommandStatuses.INVALID_ORDER_OUT
                    return
                state = 3
                self.outType = itemStr.count('>')
            elif miscMatch or singleMatch or doubleMatch:
                if state == 1:
                    state = 2
                elif state == 4:
                    self.status = CommandStatuses.INVALID_MULTIPLE_OUT
                    return
                elif state == 3:
                    state = 4
                    self.outFile = itemStr
                if state == 2:
                    if miscMatch:
                        self.args.append(itemStr)
                    else:
                        self.args.append(itemStr[1:-1])
        if self.outType is not None and self.outFile is None:
            self.status = CommandStatuses.INVALID_NO_OUTFILE
        else:
            self.status = CommandStatuses.COMMAND_VALID
            return
                

class CommandController:

    '''A wrapper to make parsing, validating, and executing commands easier'''

    def __init__(self):
        self.outputType = 0

    def feed(self, commandRaw, sysCont, sys, terminal):
        systemPath = system.FilePath(
            '/sys/command.sys',
            sys.fileSystem,
            True,
            system.sysFileHashes['command.sys']
            )
        if systemPath.status != system.PathStatuses.PATH_VALID:
            terminal.error("COMMAND.SYS ERROR")
            return -1
        if commandRaw == '':
            return 0
        commandsRaw = self.getRawCommands(commandRaw)
        commands = []
        for rawCommand in commandsRaw:
            commands.append(Command(rawCommand))
        for command in commands:
            self.outputType = 0
            if command.status == CommandStatuses.COMMAND_INVALID:
                terminal.error("Invalid command!")
                continue
            elif command.status == CommandStatuses.INVALID_NO_OUTFILE:
                terminal.error("No output file has been provided!")
                continue
            elif command.status == CommandStatuses.INVALID_ORDER_OUT:
                terminal.error("Invalid output symbol placement!")
                continue
            elif command.status == CommandStatuses.INVALID_ORDER_SWITCH:
                terminal.error("Invalid switch placement!")
                continue
            elif command.status == CommandStatuses.INVALID_MULTIPLE_OUT:
                terminal.error("Multiple output files provided!")
                continue
            if command.command in sys.aliasTable:
                self.feed(
                    sys.aliasTable[command.command]
                      + ' '
                      + ' '.join(command.switches)
                      + ' '.join(command.args)
                      + ' '
                      + {
                          '1': '>',
                          '2': '>>'
                          }[str(command.outType)] if command.outType is not None else ''
                      + ' '
                      + command.outFile if command.outFile is not None else '',
                    sysCont,
                    sys,
                    terminal
                    )
                continue
            fileName = command.command + '.bin'
            contextTest = system.FilePath(
                './' + fileName,
                sys.fileSystem,
                True
                )
            systemTest = system.FilePath(
                '/bin/' + fileName,
                sys.fileSystem,
                True
                )
            if contextTest.status == system.PathStatuses.PATH_VALID:
                context = contextTest.directory
            elif systemTest.status == system.PathStatuses.PATH_VALID:
                context = systemTest.directory
            else:
                terminal.error("Cannot find {} executable!".format(command.command))
                continue
            file = context.files[fileName]
            if file.getHash() in comList:
                kwargs = {}
                switches = comList[file.getHash()].meta['switches']
                if switches is not None:
                    for switch in switches:
                        kwargs[switch] = False
                for switch in command.switches:
                    if switch in kwargs:
                        kwargs[switch] = True
                    else:
                        terminal.error("{} is not a switch!".format(switch))
                if command.outType is not None:
                    outFileTest = system.FilePath(command.outFile, sys.fileSystem, True)
                    if outFileTest.status != system.PathStatuses.PATH_VALID:
                        if command.outType == 2:
                            terminal.error("Output file does not exist!")
                            continue
                        else:
                            filePath = system.FilePath(command.outFile, sys.fileSystem, True)
                            sys.fileSystem.make(filePath, command.outFile.split('/')[-1])
                            sys.addLog(sys.IP, 'Created {}'.format(command.outFile))
                    self.outputType = command.outType
                    self.contextFileSystem = sys.fileSystem
                    self.contextOutputPath = system.FilePath(command.outFile, sys.fileSystem, True)
                comList[file.getHash()].run(
                    sysCont,
                    sys,
                    terminal,
                    self,
                    *command.args,
                    **kwargs
                    )
            else:
                terminal.error("Error in {} executable!".format(fileName))

    def getRawCommands(self, commandRaw):
        commandsRaw = []
        buffer = ""
        string = None
        for char in commandRaw:
            if char == '"':
                if string == '"':
                    string = None
                elif string == None:
                    string = '"'
            elif char == '\'':
                if string == '\'':
                    string = None
                elif string == None:
                    string = '\''
            elif char == ';':
                if string is None:
                    commandsRaw.append(buffer)
                    buffer = ""
            else:
                buffer += char
        if buffer != "":
            commandsRaw.append(buffer)
        return commandsRaw
                    

class HelpCommand:
    
    def __init__(self):
        self.meta = {
            'descriptor': "Lists all commands. When given a command, gives a de\
tailed description.",
            'params': [0,1],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
        out = []
        binPath = system.FilePath('/bin', sys.fileSystem)
        if binPath.status != system.PathStatuses.PATH_VALID:
            terminal.error("Cannot find executables directory!")
            return -1
        else:
            foundExecs = {}
            binDir = sys.fileSystem.getDirectory(['bin'])
            for item in binDir.files:
                file = binDir.files[item]
                if file.getType() == 'BIN':
                    if file.getHash() in comList:
                        foundExecs[item[:-4]] = comList[file.getHash()]
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

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
        if kwargs['-r']:
            out = self.outDir(sys.fileSystem.workDir, 0, terminal, sysCont, [])
            terminal.out('\n'.join(out))
        else:
            out = []
            out.append('Type\tSize\tName\n')
            for name in sys.fileSystem.workDir.subdirectories:
                line = 'DIR' + '\t\t' + name
                out.append(line)
            for name, item in sys.fileSystem.workDir.files.items():
                line = item.getType() + '\t'
                if item.getContent() is not None:
                    line += str(len(item.getContent()))
                else:
                    line += '0'
                line += '\t' + name
                out.append(line)
            terminal.out('\n'.join(out))
        return 0

    def outDir(self, conts, tabs, terminal, sysCont, out):
        for item in conts.subdirectories:
            out.append('  ' * tabs + item)
            out = self.outDir(conts.subdirectories[item], tabs + 1, terminal, sysCont, out)
        for item in conts.files:
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

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
        path = system.FilePath(args[0], sys.fileSystem)
        if path.status == system.PathStatuses.PATH_NOT_EXIST:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        elif path.status == system.PathStatuses.PATH_NOT_DIR:
            terminal.error("{} is valid but is not a directory!".format(args[0]))
            return -1
        else:
            sys.fileSystem.changeDir(path)
            return 0

class OutputCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Outputs the contents of the file at the specified pa\
th. Use '-p' to pretty print.",
            'params': [1,1],
            'switches': ['-p']
            }

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
        path = system.FilePath(args[0], sys.fileSystem, True)
        name = args[0].split('/')[-1]
        pathNoFile = system.FilePath(args[0][:-len(name)], sys.fileSystem)
        if path.status != system.PathStatuses.PATH_VALID:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        else:
            out = sys.fileSystem.output(pathNoFile, name)
            if kwargs['-p']:
                skip = False
                for count, char in enumerate(out):
                    if skip:
                        skip = False
                        continue
                    if char == '\\':
                        if out[count + 1] == 'n':
                            skip = True
                            terminal.out('', Fore.GREEN, False)
                        elif out[count + 1] == 't':
                            skip = True
                            terminal.out('\t', Fore.GREEN, False, False)
                        elif out[count + 1] == '\\':
                            skip = True
                            terminal.out('\\', Fore.GREEN, True, False)
                        else:
                            terminal.error("\nUnrecognised escape sequence!")
                            return -1
                    else:
                        terminal.out(char, Fore.GREEN, True, False)
                terminal.out('')
                return 0
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

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
        out = []
        connected = sysCont.getConnected(sys.name)
        out.append("IP\t\tPort\tName\n")
        for item in connected:
            for i in range(random.randint(0,3)):
                out.append(utils.randIP()
                             + '\t'
                             + str(random.randint(0,99999))
                             + '\t'
                             + utils.randSystemName())
            out.append(item.IP
                         + '\t'
                         + str(random.randint(0,99999))
                         + '\t'
                         +  sysCont.getName(item.IP))
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

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
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

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
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

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
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

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
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

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
        name = args[0].split('/')[-1]
        if name == '*':
            path = system.FilePath(args[0][:-len(name)], sys.fileSystem)
        else:
            path = system.FilePath(args[0], sys.fileSystem, True)
        if path.status != system.PathStatuses.PATH_VALID:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        else:
            if name == '*':
                directory = copy.deepcopy(sys.fileSystem.getDirectory(path))
                items = directory.files.items()
                for key, item in items:
                    ret = sys.fileSystem.remove(
                        path,
                        key
                        )
                    if ret == 0:
                        terminal.out("Removed " + item._name)
                        if item.getType() != 'LOG':
                            sys.addLog(sys.IP, "Removed " + key)
                return 0
            else:
                path = system.FilePath(args[0][:-len(name)], sys.fileSystem)
                file = path.directory.files[name]
                sys.fileSystem.remove(
                    path,
                    name
                    )
                if file.getType() != 'LOG':
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

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
        name = args[0].split('/')[-1]
        if name == '*':
            path = system.FilePath(args[0][:-len(name)], sys.fileSystem)
        else:
            path = system.FilePath(args[0], sys.fileSystem)
        if path.status != system.PathStatuses.PATH_VALID:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        else:
            if name == '*':
                directory = copy.deepcopy(sys.fileSystem.getDirectory(path))
                items = list(directory.subdirectories.keys())
                for item in items:
                    ret = sys.fileSystem.remove(path, item, True)
                    if ret == 0:
                        terminal.out("Removed " + item)
                        sys.addLog(sys.IP, "Removed " + item)
                return 0
            else:
                path = system.FilePath(args[0][:-len(name)], sys.fileSystem)
                sys.fileSystem.remove(path, name, True)
                sys.addLog(sys.IP, "Removed " + name)
                return 0

class MoveCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Moves the file at the specified path to the second s\
pecified path. Use '-d' to move directories. Use '-f' to force replace (can be \
destructive).",
            'params': [2,2],
            'switches': ['-f', '-d']
            }

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
        nameGet = args[0].split('/')[-1]
        if kwargs['-d']:
            pathTest = system.FilePath(args[0], sys.fileSystem)
        else:
            pathTest = system.FilePath(args[0], sys.fileSystem, True)
        if pathTest.status < 0:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        pathGet = system.FilePath(args[0][:-len(nameGet)], sys.fileSystem)
        nameSet = args[1].split('/')[-1]
        pathSet = system.FilePath(args[1][:-len(nameSet)], sys.fileSystem)
        if not kwargs['-f']:
            pathSetDir = sys.fileSystem.getDirectory(pathSet.iterList)
            if kwargs['-d']:
                setConts = pathSetDir.subdirectories
            else:
                setConts = pathSetDir.files
            if nameSet in setConts:
                terminal.error("{} already exists!".format(nameSet))
                return -1
        if pathSet.status < 0:
            terminal.error("{} is not a valid path!".format(args[1]))
            return -1
        ret = sys.fileSystem.move(pathGet, nameGet, pathSet, nameSet, kwargs['-d'])
        sys.addLog(sys.IP, "Moved {} to {}".format(args[0], args[1]))
        return 0

class FileMakeCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Creates an empty file at the specified path.",
            'params': [1,1],
            'switches': None
            }

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
        name = args[0].split('/')[-1]
        makePath = system.FilePath(args[0][:-len(name)], sys.fileSystem)
        if makePath.status != system.PathStatuses.PATH_VALID:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        else:
            ret = sys.fileSystem.make(makePath, name)
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

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
        name = args[0].split('/')[-1]
        makePath = system.FilePath(args[0][:-len(name)], sys.fileSystem)
        if makePath.status != system.PathStatuses.PATH_VALID:
            terminal.error("{} is not a valid path!".format(args[0]))
            return -1
        else:
            ret = sys.fileSystem.makeDirectory(
                makePath,
                name
                )
            if ret == -1:
                terminal.error("{} already exists!".format(args[0]))
                return -1
            else:
                sys.addLog(sys.IP, "Created {}".format(args[0]))
            return 0

class SecureShellCommand:

    def __init__(self):
        self.meta = {
            'descriptor': "Interacts with connected computers.",
            'params': [1,3],
            'switches': ['-n', '-l', '-dc', '-name']
            }

    def run(self, sysCont, sys, terminal, comCont, *args, **kwargs):
        if kwargs['-name']:
            if len(args) != 2:
                terminal.error("Invalid number of parameters!")
                return -1
            sys.namedSystems[args[1]] = args[0]
            return 0
        if not kwargs['-n']:
            if not utils.IPRegex.match(args[0]):
                terminal.error("Invalid IP!")
                return -1
            IP = args[0]
        else:
            if args[0] not in sys.namedSystems:
                terminal.error("Invalid name!")
                return -1
            IP = sys.namedSystems[args[0]]
        name = sysCont.getName(IP)
        if name not in sysCont.systemDict:
            time.sleep(5)
            terminal.out("Connection refused: No further information.")
            return 0
        if sysCont.systemDict[name].status != system.Statuses.ONLINE:
            time.sleep(5)
            terminal.out("Request timed out.")
            return 0
        if kwargs['-l']:
            if len(args) != 3:
                terminal.error("Invalid number of parameters!")
                return -1
            if [args[1], args[2]] == sysCont.systemDict[name].login:
                sysCont.systemDict[name].userLoggedIn = True
                terminal.out("Login was successful.")
                return 0
            else:
                terminal.out("Login unsuccessful: Incorrect details.")
                return 0
        if not sysCont.systemDict[name].userLoggedIn:
            terminal.out("Connection refused: Not logged in.")
            return 0
        comCont.feed(args[1], sysCont, sysCont.systemDict[name], terminal)

def getExecHash(fileName):
    path = 'data/executables/'
    if 'data' not in os.listdir():
        path = '../' + path
    with open(path + fileName, 'r') as file:
        fileData = json.loads(file.read())
    return fileData['hash']

def getExecContent(fileName):
    path = 'data/executables/'
    if 'data' not in os.listdir():
        path = '../' + path
    with open(path + fileName) as file:
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
    getExecHash('FolderMakeCommand.json'): FolderMakeCommand(),
    getExecHash('SecureShellCommand.json'): SecureShellCommand()
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
    'mkdir.bin':    'FolderMakeCommand.json',
    'ssh.bin':      'SecureShellCommand.json'
    }

comContent = {}
for item in comTable.values():
    comContent[item] = getExecContent(item)
