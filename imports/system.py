__version__ = '2.7.5'

'''Module to create a virtual system with an assigned IP, independent
filesystem, and statuses, must be loaded along with other imports'''

import utils, commands
import json
import random
from enum import Enum
import hashlib
import copy
import time
import re
import pickle
import os

class Statuses(Enum):
    ONLINE = 0
    OFFLINE = 1
    UNBOOTABLE = 2

class File:

    typeRegex = re.compile('\.[a-zA-Z]+$')
    
    def __init__(self, name, content=None):
        self._type = self.findType(name)
        self._content = content
        if self._content is not None:
            self._hash = hashlib.md5(bytes(self._content, 'ascii')).hexdigest()
        

    def getContent(self):
        return self._content

    def getHash(self):
        if self._content is not None:
            return self._hash
        else:
            return None

    def getType(self):
        return self._type

    def findType(self, name):
        ret = self.typeRegex.search(name)
        if ret:
            self._type = ret[0][1:].upper()
        else:
            self._type = ''

    def update(self, content):
        self.__init__(content)

    def __deepcopy__(self, ctx):
        newFile = File(self._content)
        return newFile

class Directory:

    def __init__(self):
        self.subdirectories = {}
        self.files = {}

    def __deepcopy__(self, ctx):
        """Generates a copy of this directory
using recursive copying of subdirectories"""
        subdirectories = {}
        files = {}
        for subdirectory in self.subdirectories:
            subdirectories[subdirectory] = copy.deepcopy(self.subdirectories[subdirectory])
        for file in self.files:
            files[file] = copy.deepcopy(self.files[file])
        newDir = Directory()
        newDir.subdirectories = subdirectories
        newDir.files = files
        return newDir

class SystemsController:

    '''A wrapper to make systems easier to work with'''
    
    def __init__(self):
        self.systemDict = {}
        self.systemLookup = {}
        self.loadDefaultSystems()
        self.userSystem = self.systemDict['userSystem']

    def loadDefaultSystems(self):
        with open('data/defaultsystems.json', 'r') as file:
            defaultSystems = json.loads(file.read())
        for sys in defaultSystems:
            IP = utils.randIP()
            self.systemDict[sys] = System(
                IP,
                utils.randOSCompany(),
                defaultSystems[sys]
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

class FilePath:

    '''Turns a string into a validated path, with support for files and content
    validation'''
    
    def __init__(self, path, fileSystem, isFile=False, fileHash=None):
        #  0: path is valid
        # -1: path does not exist
        # -2: path exists but is not a directory
        # -3: file doesn't exist
        # -5: file exists, but hash doesn't match
        # -6: empty path
        self.iterList = []
        if len(path) > 0 and path[0] == '/':
            path = path[1:]
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
        self.iterList = list(item for item in self.iterList if item != '')
        self.length = len(self.iterList)
        if isFile:
            if self.length == 0:
                self.status = -6
                return
            fileName = self.iterList[-1]
            filePath = self.iterList[:-1]
            self.status = fileSystem.checkIsValidPath(filePath)
            if self.status == 0:
                directory = fileSystem.getDirectory(filePath)
                if fileName not in directory.files:
                    self.status = -3
                    return
                else:
                    file = directory.files[fileName]
                    if fileHash is not None:
                        if file.getHash() == fileHash:
                            return
                        else:
                            self.status = -5
                            return
                    else:
                        return
            else:
                return
        else:
            self.status = fileSystem.checkIsValidPath(self.iterList)
            return

    def __iter__(self):
        return (i for i in self.iterList)

    def __getitem__(self, index):
        return self.iterList[index]

class System:

    '''A virtual system'''

    def __init__(self, IP, OSManu, sysData):
        self.IP = IP
        self.fileSystem = FileSystem(copy.deepcopy(SYSTEM_DEFAULT_FILESYSTEM))
        self.OSManu = OSManu
        self.connected = sysData['connected']
        self.status = Statuses.ONLINE
        self.aliasTable = {}
        self.userLoggedIn = False
        self.namedSystems = {}
        self.login = sysData['login']
        binPath = self.fileSystem.path.subdirectories['bin']
        for item in sysData['executables']:
            fileName = commands.comTable[item]
            fileContent = commands.comContent[fileName]
            binPath.files[item] = File(fileContent)

    def exit(self):
        self.fileSystem.exit()

    def restart(self, sysCont):
        self.exit()
        bootFilePath = FilePath(
            'sys/boot.sys',
            self.fileSystem,
            True,
            sysFileHashes['boot.sys']
            )
        if bootFilePath.status < 0:
            self.status = Statuses.UNBOOTABLE
            return -1
        else:
            self.status = Statuses.ONLINE
            return 0

    def addLog(self, IP, log):
        logPath = FilePath('/log', self.fileSystem)
        if logPath.status < 0:
            self.fileSystem.path['log'] = Directory()
        logContent = self.fileSystem.getDirectory(['log'], True)
        concatenated = '{}@{}-{}'.format(IP, time.strftime('%H:%M:%S'), log)
        logContent[concatenated + '.log'] = File(concatenated)
        self.fileSystem.workDirContents = self.fileSystem.getDirectory(
            self.fileSystem.workingDirectory
            )
        return 0

class FileSystem:

    '''Holds a filesystem, and can view and manipulate it
    with an inbuilt working directory'''

    def __init__(self, contents={}):
        self.path = contents
        self.workingDirectory = []
        self.workDirContents = self.getDirectory()

    def getDirectory(self, direcList=[]):
        '''Gets the contents of an absolute path list'''
        tempWorkDir = self.path # This is the only place self.path should be used
        for direc in direcList:
            tempWorkDir = tempWorkDir.subdirectories[direc]
        return tempWorkDir

    def getPath(self):
        '''Returns the working directory as a string'''
        pathAsString = '/' + '/'.join(self.workingDirectory)
        return pathAsString

    def changeDir(self, path):
        '''Changes the directory to the supplied path'''
        #        0: Successful
        # -1 to -2: From checkIsValidPath
        assert type(path) is FilePath
        self.workingDirectory = path.iterList.copy()
        self.workDirContents = self.getDirectory(self.workingDirectory)
        return 0

    def make(self, path, fileName, content=None):
        '''Makes an item of the specified type'''
        #   0: Successful
        #  -1: Path already exists
        assert type(path) is FilePath
        tempWorkDir = self.getDirectory(path.iterList)
        if fileName in tempWorkDir.files:
            return -1
        else:
            tempWorkDir.files[fileName] = File(content)
            self.workDirContents = self.getDirectory(self.workingDirectory)
            return 0

    def remove(self, path, name):
        '''Removes the item at the given path'''
        #  0: Successful
        # -1: Path doesn't exist
        assert type(path) is FilePath
        tempWorkDir = self.getDirectory(path.iterList, True)
        if name not in tempWorkDir.files:
            return -1
        else:
            del tempWorkDir.files[name]
            self.correctWorkingDirectory()
            self.workDirContents = self.getDirectory(self.workingDirectory)
            return 0

    def correctWorkingDirectory(self):
        '''Corrects errors in the working directory caused
        by deleted files'''
        tempWorkDir = self.getDirectory()
        for count, item in enumerate(self.workingDirectory):
            if not item in tempWorkDir.subdirectories:
                self.workingDirectory = self.workingDirectory[:count]
            else:
                tempWorkDir = tempWorkDir.subdirectories[item]

    def output(self, path, fileName):
        '''Outputs the contents of the file in the supplied path'''
        # str: Successful
        #  -1: Path doesn't exist
        #  -2: Path is a directory
        assert type(path) is FilePath
        tempWorkDir = self.getDirectory(path.iterList)
        return tempWorkDir.files[fileName].getContent

    def exit(self):
        '''Soft inits the system, call this when disconnecting'''
        self.workingDirectory = []
        self.workDirContents = self.getDirectory()

    def move(self, pathGet, nameGet, pathSet, nameSet, isDir=False):
        '''Moves the file at path 1 to the file at path 2'''
        #  0: Successful
        # -1: Path doesn't exist
        # -2: Path is a directory
        getDir = self.getDirectory(pathGet.iterList)
        setDir = self.getDirectory(pathSet.iterList)
        if isDir:
            setDirContents.subdirectories[nameSet] = getDirContents.subdirectories[nameGet]
            del getDirContents.subdirectories[nameGet]
        else:
            setDirContents.files[nameSet] = getDirContents.files[nameGet]
            del getDirContents.files[nameGet]
            setDirContents.files[nameSet].update(nameSet, setDirContents.files[nameSet].getContent)
        self.correctWorkingDirectory()
        self.workDirContents = self.getDirectory(self.workingDirectory)
        return 0

    def checkIsValidPath(self, pathList):
        '''Checks the path provided exists'''
        #  0: path is valid
        # -1: path does not exist
        # -2: path exists but is not a dir
        tempWorkDir = self.getDirectory()
        for count, item in enumerate(pathList):
            if item not in tempWorkDir.subdirectories:
                return -1
            else:
                tempWorkDir = tempWorkDir.subdirectories[item]
        return 0

    def handleFileOutput(self, output, terminal, message):
        outputDir = self.getDirectory(output[2].iterList[:-1], True)
        name = output[2].iterList[-1]
        if output[0] == commands.OutTypes.FILEOVERWRITE:
            outputDir.files[name].update(name, message)
        elif output[0] == commands.OutTypes.FILEAPPEND:
            if outputDir.files[name].getContent() is not None:
                outputDir.files[name].update(name, outputDir.files[name].getContent() + message)
            else:
                outputDir.files[name].update(name, message)
        return 0

def getSysHash(fileName):
    path = 'data/system/'
    if 'data' not in os.listdir():
        path = '../' + path
    with open(path + fileName, 'r') as file:
        fileData = json.loads(file.read())
    return fileData['hash']

def getSysContent(fileName):
    path = 'data/system/'
    if 'data' not in os.listdir():
        path = '../' + path
    with open(path + fileName, 'r') as file:
        fileData = json.loads(file.read())
    return fileData['content']

sysFileHashes = {
    'command.sys': getSysHash('command.json'),
    'boot.sys': getSysHash('boot.json')
    }

sysFileContents = {
    'command.sys': getSysContent('command.json'),
    'boot.sys': getSysContent('boot.json')
    }

with open('imports/DEFAULTSYSTEM.pkl', 'rb') as file:
    SYSTEM_DEFAULT_FILESYSTEM = pickle.load(file)
