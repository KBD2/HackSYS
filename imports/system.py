__version__ = '2.4.0'

'''Module to create a virtual system with an assigned IP, independent
filesystem, and statuses, must be loaded along with other imports'''

from imports import (utils, commands)
import json
import random
from enum import Enum
import hashlib

#Filetype constants
class FileTypes(Enum):
    DIR = 0
    TXT = 1
    BIN = 2
    DAT = 3
    SYS = 4
    MSC = 99

class Statuses(Enum):
    ONLINE = 0
    OFFLINE = 1
    UNBOOTABLE = 2

SYSTEM_DEFAULT_FILESYSTEM = {
    'home': {
        'type': FileTypes.DIR,
        'content': {}
        },
    'bin': {
        'type': FileTypes.DIR,
        'content': {}
        },
    'sys': {
        'type': FileTypes.DIR,
        'content': {}
        }
    }

class System:

    '''A virtual system'''

    def __init__(self, IP, OSManu, sysData, sysSysData, randomHomeFiles = True):
        self.IP = IP
        self.fileSystem = FileSystem(SYSTEM_DEFAULT_FILESYSTEM.copy())
        self.OSManu = OSManu
        self.connected = sysData['connected']
        self.status = Statuses.ONLINE
        self.aliasTable = {}
        binPath = self.fileSystem.path['bin']['content']
        for item in sysData['executables']:
            fileName = commands.comTable[item]
            fileContent = commands.getContent(fileName)
            binPath[item] = {
                'type': FileTypes.BIN,
                'content': fileContent
                }
        sysPath = self.fileSystem.path['sys']['content']
        for item in sysSysData:
            sysPath[item] = {'type': FileTypes.BIN, 'content': sysSysData[item]['content']}

    def exit(self):
        self.fileSystem.exit()

    def restart(self, sysCont):
        self.exit()
        if 'sys' not in self.fileSystem.path:
            self.status = Statuses.UNBOOTABLE
            return -1
        elif self.fileSystem.path['sys']['type'] != FileTypes.DIR:
            self.status = Statuses.UNBOOTABLE
            return -1
        elif 'boot.sys' not in self.fileSystem.path['sys']['content']:
                self.status = Statuses.UNBOOTABLE
                return -1
        else:
            bootPath = self.fileSystem.path['sys']['content']['boot.sys']
            bootHash = hashlib.md5(bytes(bootPath['content'], 'ascii')).hexdigest()
            if bootHash != sysCont.sysSysData['boot.sys']['hash']:
                self.status = Statuses.UNBOOTABLE
                return -1
            else:
                self.status = Statuses.ONLINE
                return 0

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
            tempWorkDir = tempWorkDir[direc]['content']
        if reference:
            return tempWorkDir
        else:
            return tempWorkDir.copy()

    def getPath(self):
        '''Returns the working directory as a string'''
        pathAsString = '/' + '/'.join(self.workingDirectory)
        return pathAsString

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
                tempWorkDir = tempWorkDir[item]['content']
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
        #   0: Successful
        #  -1: Path already exists
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

    def remove(self, path, name, whitelist=None, blacklist=None):
        '''Removes the item at the given path'''
        #  0: Successful
        # -1: Path doesn't exist
        assert type(path) is FilePath
        tempWorkDir = path.iterList.copy()
        tempWorkDirContents = self.getContents(tempWorkDir, True)
        if name not in tempWorkDirContents:
            return -1
        elif whitelist and tempWorkDirContents[name]['type'] not in whitelist:
            return -2
        elif blacklist and tempWorkDirContents[name]['type'] in blacklist:
            return -2
        else:
            del tempWorkDirContents[name]
            self.correctWorkingDirectory()
            self.workDirContents = self.getContents(self.workingDirectory)
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
        # str: Successful
        #  -1: Path doesn't exist
        #  -2: Path is a directory
        assert type(path) is FilePath
        tempWorkDir = path.iterList.copy()
        tempWorkDirContents = self.getContents(tempWorkDir)
        if fileName not in tempWorkDirContents:
            return -1
        elif tempWorkDirContents[fileName]['type'] == FileTypes.DIR:
            return -2
        else:            return tempWorkDirContents[fileName]['content']

    def exit(self):
        '''Soft inits the system, call this when disconnecting'''
        self.workingDirectory = []
        self.workDirContents = self.getContents()

    def move(self, path1, name1, path2, name2):
        '''Moves the file at path 1 to the file at path 2'''
        #  0: Successful
        # -1: Path doesn't exist
        # -2: Path is a directoryS
        getDirContents = self.getContents(path1.iterList, True)
        if name1 not in getDirContents:
            return -1
        elif getDirContents[name1]['type'] == FileTypes.DIR:
            return -2
        else:
            setDirContents = self.getContents(path2.iterList, True)
            setDirContents[name2] = getDirContents.pop(name1)
            fileType = self.getFileType(name2)
            if fileType != FileTypes.DIR:
                setDirContents[name2]['type'] = fileType
            else:
                setDirContents[name2]['type'] = FileTypes.MSC
            self.correctWorkingDirectory()
            self.workDirContents = self.getContents(self.workingDirectory)
            return 0

    def getFileType(self, fileName):
        name = None
        for count in range(len(fileName) - 1, -1, -1):
            if fileName[count] == '.':
                name = fileName[count + 1:]
        try:
            fileType = FileTypes[name.upper()]
        except:
            fileType = FileTypes.MSC
        return fileType

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
        for count, item in enumerate(self.iterList):
            if item == '':
                del self.iterList[count]
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
        self.userSystem = self.systemDict['userSystem']

    def loadDefaultSystems(self):
        defaultSystems = json.load(open('data/defaultsystems.json', 'r'))
        self.sysSysData = {
            'boot.sys': json.load(open('data/system/boot.json', 'r')),
            'command.sys': json.load(open('data/system/command.json', 'r'))
            }
        self.systemDict = {}
        self.systemLookup = {}
        for sys in defaultSystems:
            IP = utils.randIP()
            self.systemDict[sys] = System(
                IP,
                utils.randOSCompany(),
                defaultSystems[sys],
                self.sysSysData
                )
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
