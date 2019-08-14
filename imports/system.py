__version__ = '2.1.1'

'''Module to create a virtual system with an assigned IP, independent
filesystem, and statuses, must be loaded along with other imports'''

from imports import utils
import json
import random

#Filetype constants
TYPE_DIR    = 0
TYPE_TEXT   = 1
TYPE_BINARY = 2
TYPE_DATA   = 3
TYPE_SYSTEM = 4

TYPE_NAMES = (
    'DIR',
    'TXT',
    'BIN',
    'DAT',
    'SYS'
    )

SYSTEM_DEFAULT_FILESYSTEM = {
    'home': {
        'type': TYPE_DIR,
        'welcome.txt': {
            'type': TYPE_TEXT,
            'content': "Welcome to your new system!"
            }
        },
    'bin': {
        'type': TYPE_DIR
        },
    'sys': {
        'type': TYPE_DIR,
        'boot.sys': {
            'type': TYPE_SYSTEM,
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
                line = TYPE_NAMES[self.workDirContents[item]['type']] + '\t'
                if 'content' in self.workDirContents[item]:
                    line += str(len(self.workDirContents[item]['content']))
                line += '\t' + item
                terminal.out(line)
        return 0

    def checkIsValidPath(self, path, ignoreLastItem=False):
        '''Checks the path provided exists'''
        #  0: path is valid
        # -1: path does not exist
        # -2: path exists but is not a dir
        assert type(path) is FilePath
        if path.isAbsolute:
            tempWorkDir = self.getContents()
        else:
            tempWorkDir = self.workDirContents
        if ignoreLastItem:
            toCheck = path[:-1]
        else:
            toCheck = path[:]
        for count, item in enumerate(toCheck):
            if item not in tempWorkDir:
                return -1
            elif tempWorkDir[item]['type'] != TYPE_DIR:
                return -2
            else:
                tempWorkDir = tempWorkDir[item]
        return 0

    def changeDir(self, path):
        '''Changes the directory to the supplied path'''
        #        0: Successful
        # -1 to -2: From checkIsValidPath
        assert type(path) is FilePath
        ret = self.checkIsValidPath(path)
        if ret < 0:
            return ret
        else:
            if path.isAbsolute:
                self.workingDirectory = path.iterList.copy()
            else:
                for item in path:
                    self.workingDirectory.append(item)
            self.workDirContents = self.getContents(self.workingDirectory)
            return 0

    def make(self, path, typ, content=None):
        '''Makes an item of the specified type'''
        #        0: Successful
        # -1 to -2: From checkIsValidPath
        #       -3: Path already exists
        assert type(path) is FilePath
        ret = self.checkIsValidPath(path, True)
        if ret < 0:
            return ret
        else:
            tempWorkDir = []
            if path.isAbsolute:
                tempWorkDir = path.iterList.copy()
            else:
                tempWorkDir = self.workingDirectory.copy()
                for item in path[:-1]:
                    tempWorkDir.append(item)
            tempWorkDirContents = self.getContents(self.workingDirectory, True)
            if path[-1] in tempWorkDirContents:
                return -3
            else:
                tempWorkDirContents[path[-1]] = {'type': typ}
                if typ != TYPE_DIR:
                    tempWorkDirContents[path[-1]]['content'] = content
                self.workDirContents = self.getContents(self.workingDirectory)
                return 0

    def remove(self, path):
        '''Removes the item at the given path'''
        #        0: Successful
        # -1 to -2: From checkIsValidPath
        #       -3: Path doesn't exist
        assert type(path) is FilePath
        ret = self.checkIsValidPath(path, True)
        if ret < 0:
            return ret
        else:
            tempWorkDir = []
            if path.isAbsolute:
                tempWorkDir = path.iterList[:-1].copy()
            else:
                tempWorkDir = self.workingDirectory.copy()
                for item in path[:-1]:
                    tempWorkDir.append(item)
            tempWorkDirContents = self.getContents(tempWorkDir, True)
            if path[-1] not in tempWorkDirContents:
                return -3
            else:
                del tempWorkDirContents[path[-1]]
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

    def output(self, path):
        '''Outputs the contents of the file in the supplied path'''
        #      str: Successful
        # -1 to -2: From checkIsValidPath
        #       -3: Path doesn't exist
        #       -4: Path is a directory
        assert type(path) is FilePath
        ret = self.checkIsValidPath(path, True)
        if ret < 0:
            return ret
        else:
            tempWorkDir = []
            if path.isAbsolute:
                tempWorkDir = path.iterList[:-1].copy()
            else:
                tempWorkDir = self.workingDirectory.copy()
                for item in path[:-1]:
                    tempWorkDir.append(item)
            tempWorkDirContents = self.getContents(tempWorkDir, True)
            if path[-1] not in tempWorkDirContents:
                return -3
            elif tempWorkDirContents[path[-1]]['type'] == TYPE_DIR:
                return -4
            else:
                return tempWorkDirContents[path[-1]]['content']

    def exit(self):
        '''Soft inits the system, call this when disconnecting'''
        self.workingDirectory = []
        self.workDirContents = self.getContents()

class FilePath:
    
    def __init__(self, path):
        assert type(path) is str
        self.iterList = []
        self.isAbsolute = False
        if path[0] == '/':
            path = path[1:]
            self.isAbsolute = True
        self.iterList = path.split('/')
        if self.iterList == ['']:
            self.iterList = []
        self.length = len(self.iterList)

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
