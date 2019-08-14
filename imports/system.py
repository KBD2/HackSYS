__version__ = '2.1.3'

'''Module to create a virtual system with an assigned IP, independent
filesystem, and statuses, must be loaded along with other imports'''

from imports import utils
import json
import random
from enum import Enum

#Filetype constants
class FileTypes(Enum):
    DIR = 0
    TXT = 1
    BIN = 2
    DAT = 3
    SYS = 4

SYSTEM_DEFAULT_FILESYSTEM = {
    'home': {
        'type': FileTypes.DIR,
        'welcome.txt': {
            'type': FileTypes.TXT,
            'content': "Welcome to your new system!"
            }
        },
    'bin': {
        'type': FileTypes.DIR
        },
    'sys': {
        'type': FileTypes.DIR,
        'boot.sys': {
            'type': FileTypes.SYS,
            'content': "1100111100100101000101011011101010101100001111010010101\
0000110100110111010001101001001111111111101001110000111011100010111101111010010\
1010001000010100011100101111111011111111101000001100110011001100111001110111001\
1110100000011101101001001111111011011101000011100101011100010011011011000001010\
0001100101001011000101010000110001110110000111010010101111110000011001111011010\
1111011001001010000001000011011010010000010101010000010111101111001000001010101\
11101101010011001000100111001100001011101111001101"
            }
        }
    }

class System:

    '''A virtual system'''

    def __init__(self, IP, OSManu, connected, randomHomeFiles = True):
        self.IP = IP
        self.fileSystem = FileSystem(SYSTEM_DEFAULT_FILESYSTEM)
        self.OSManu = OSManu
        self.connected = connected

    def exit(self):
        self.fileSystem.exit()

class FileSystem:

    '''Holds a filesystem, and can view and manipulate it
    with an inbuilt working directory'''

    def __init__(self, contents={}):
        self.path = contents
        self.workingDirectory = []
        self.workDirContents = self.getContents([])

    def getContents(self, direcList=[], reference=False):
        '''Gets the contents of an absolute path list'''
        tempWorkDir = self.path # This is the only place self.path should be used
        for direc in direcList:
            tempWorkDir = tempWorkDir[direc]
        if reference:
            return tempWorkDir
        else:
            return tempWorkDir.copy()

    def getPath(self):
        '''Returns the working directory as a string'''
        pathAsString = '/' + '/'.join(self.workingDirectory)
        return pathAsString

    def listDir(self, terminal):
        '''Outputs the contents of the current directory
        to the terminal'''
        terminal.out('Type\tSize\tName\n')
        for item in self.workDirContents:
            if item != 'type':
                line = FileTypes(self.workDirContents[item]['type']).name + '\t'
                if 'content' in self.workDirContents[item]:
                    line += str(len(self.workDirContents[item]['content']))
                line += '\t' + item
                terminal.out(line)
        return 0

    def checkIsValidPath(self, path):
        '''Checks the path provided exists'''
        #  0: path is valid
        # -1: path does not exist
        # -2: path exists but is not a dir
        assert type(path) is FilePath
        tempWorkDir = self.getContents()
        for count, item in enumerate(path):
            if item not in tempWorkDir:
                return -1
            elif tempWorkDir[item]['type'] != FileTypes.DIR:
                return -2
            else:
                tempWorkDir = tempWorkDir[item]
        return 0

    def changeDir(self, path):
        '''Changes the directory to the supplied path'''
        #        0: Successful
        # -1 to -2: From checkIsValidPath
        assert type(path) is FilePath
        self.workingDirectory = path.iterList.copy()
        self.workDirContents = self.getContents(self.workingDirectory)
        return 0

    def make(self, path, fileName, typ, content=None):
        '''Makes an item of the specified type'''
        #        0: Successful
        #       -1: Path already exists
        assert type(path) is FilePath
        tempWorkDir = path.iterList.copy()
        tempWorkDirContents = self.getContents(self.workingDirectory, True)
        if fileName in tempWorkDirContents:
            return -1
        else:
            tempWorkDirContents[fileName] = {'type': typ}
            if typ != FileTypes.DIR:
                tempWorkDirContents[fileName]['content'] = content
            self.workDirContents = self.getContents(self.workingDirectory)
            return 0

    def remove(self, path, fileName):
        '''Removes the item at the given path'''
        #        0: Successful
        #       -1: Path doesn't exist
        assert type(path) is FilePath
        tempWorkDir = path.iterList.copy()
        tempWorkDirContents = self.getContents(tempWorkDir, True)
        if fileName not in tempWorkDirContents:
            return -1
        else:
            del tempWorkDirContents[fileName]
            self.correctWorkingDirectory()
            return 0

    def correctWorkingDirectory(self):
        '''Corrects errors in the working directory caused
        by deleted files'''
        tempWorkDirContents = self.getContents()
        for count, item in enumerate(self.workingDirectory):
            if not item in tempWorkDirContents:
                self.workingDirectory = self.workingDirectory[:count]
            else:
                tempWorkDirContents = tempWorkDirContents[item].copy()

    def output(self, path, fileName):
        '''Outputs the contents of the file in the supplied path'''
        #      str: Successful
        #       -1: Path doesn't exist
        #       -2: Path is a directory
        assert type(path) is FilePath
        tempWorkDir = path.iterList.copy()
        tempWorkDirContents = self.getContents(tempWorkDir)
        if fileName not in tempWorkDirContents:
            return -1
        elif tempWorkDirContents[fileName]['type'] == FileTypes.DIR:
            return -2
        else:
            return tempWorkDirContents[fileName]['content']

    def exit(self):
        '''Soft inits the system, call this when disconnecting'''
        self.workingDirectory = []
        self.workDirContents = self.getContents()

class FilePath:
    
    def __init__(self, path, fileSystem):
        assert type(path) is str
        self.iterList = []
        if len(path) > 0 and path[0] == '/':
            path = path[1:]
            self.iterList = path.split('/')
        else:
            self.iterList = fileSystem.workingDirectory.copy()
            for item in path.split('/'):
                if item == '.':
                    continue
                elif item == '..':
                    if self.iterList:
                        self.iterList.pop()
                    else:
                        continue
                else:
                    self.iterList.append(item)
        if self.iterList == ['']:
            self.iterList = []
        self.length = len(self.iterList)
        self.status = fileSystem.checkIsValidPath(self)

    def __iter__(self):
        return (i for i in self.iterList)

    def __getitem__(self, index):
        return self.iterList[index]

class SystemsController:

    '''A wrapper to make systems easier to work with'''
    
    def __init__(self):
        self.loadDefaultSystems()
        self.userSystem = self.getName(self.systemDict['userSystem'].IP)
        self.currSystem = self.systemDict[self.userSystem]

    def loadDefaultSystems(self):
        defaultSystems = json.load(open('data/defaultsystems.json', 'r'))
        self.systemDict = {}
        self.systemLookup = {} # Like a reverse DNS server
        for sys in defaultSystems:
            IP = utils.randIP()
            self.systemDict[sys] = System(IP, utils.randOSCompany(), defaultSystems[sys]['connected'])
            self.systemLookup[IP] = sys
        return 0

    def getConnectedIPs(self, IP):
        systemName = self.getName(IP)
        connectedIPs = []
        for name in self.systemDict[systemName].connected:
            connectedIPs.append(self.systemDict[name].IP)
        return connectedIPs

    def getName(self, IP):
        if IP not in self.systemLookup:
            return -1
        else:
            return self.systemLookup[IP]

    def switchSystems(self, IP):
        # -1: IP is not valid
        ret = self.getName(IP)
        if ret == -1:
            return ret
        else:
            self.currSystem.fileSystem.exit()
            self.currSystem = self.systemDict[ret]
            return 0
