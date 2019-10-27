__version__ = '3.0.1'

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

class PathStatuses(Enum):
    PATH_VALID = 0
    PATH_NOT_EXIST = 1
    PATH_NOT_DIR = 2
    FILE_NOT_EXIST = 3
    INVALID_HASH = 4
    PATH_EMPTY = 5

class File:

    typeRegex = re.compile('\.[a-zA-Z0-9]+$')
    
    def __init__(self, name, content=None):
        self._name = name
        self.findType(self._name)
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

    def update(self, name, content):
        self.__init__(name, content)

    def __deepcopy__(self, ctx):
        newFile = File(self._name, self._content)
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
                sys,
                defaultSystems[sys]
                )
            self.systemLookup[IP] = sys
        return 0

    def getConnected(self, name):
        connected = []
        for name in self.systemDict[name].connected:
            connected.append(self.systemDict[name])
        return connected

    def getName(self, IP):
        if IP not in self.systemLookup:
            return -1
        else:
            return self.systemLookup[IP]

class FilePath:

    '''Turns a string into a validated path, with support for files and content
    validation'''
    
    def __init__(self, path, fileSystem, isFile=False, fileHash=None):
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
                self.status = PathStatuses.PATH_EMPTY
                return
            fileName = self.iterList[-1]
            filePath = self.iterList[:-1]
            status = fileSystem.checkIsValidPath(filePath)
            if status:
                directory = fileSystem.getDirectory(filePath)
                self.directory = directory
                if fileName not in directory.files:
                    self.status = PathStatuses.FILE_NOT_EXIST
                    return
                else:
                    file = directory.files[fileName]
                    if fileHash is not None:
                        if file.getHash() == fileHash:
                            self.status = PathStatuses.PATH_VALID
                            return
                        else:
                            self.status = PathStatuses.INVALID_HASH
                            return
                    else:
                        self.status = PathStatuses.PATH_VALID
                        return
            else:
                self.status = PathStatuses.PATH_NOT_EXIST
                return
        else:
            if fileSystem.checkIsValidPath(self.iterList):
                self.status = PathStatuses.PATH_VALID
                self.directory = fileSystem.getDirectory(self.iterList)
            else:
                self.status = PathStatuses.PATH_NOT_EXIST
            return

    def __iter__(self):
        return (i for i in self.iterList)

    def __getitem__(self, index):
        return self.iterList[index]

class System:

    '''A virtual system'''

    def __init__(self, IP, name, sysData):
        self.IP = IP
        self.name = name
        self.fileSystem = FileSystem(copy.deepcopy(SYSTEM_DEFAULT_FILESYSTEM))
        self.OSManu = utils.randOSCompany()
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
            binPath.files[item] = File(item, fileContent)

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
        if bootFilePath.status != PathStatuses.PATH_VALID:
            self.status = Statuses.UNBOOTABLE
            return -1
        else:
            self.status = Statuses.ONLINE
            return 0

    def addLog(self, IP, log):
        logPath = FilePath('/log', self.fileSystem)
        if logPath.status != PathStatuses.PATH_VALID:
            self.fileSystem.path.subdirectories['log'] = Directory()
        logDirectory = self.fileSystem.getDirectory(['log'])
        concatenated = '{}@{}-{}'.format(IP, time.strftime('%H:%M:%S'), log)
        fileName = concatenated + '.log'
        logDirectory.files[fileName] = File(fileName, concatenated)
        self.fileSystem.workDirContents = self.fileSystem.getDirectory(
            self.fileSystem.workingDirectory
            )
        return 0

class FileSystem:

    '''Holds a filesystem, and can view and manipulate it
    with an inbuilt working directory'''

    def __init__(self, contents):
        self.path = contents
        self.workingDirectory = []
        self.workDir = self.getDirectory()

    def getDirectory(self, direcList=[]):
        '''Gets the contents of an absolute path list'''
        tempWorkDir = self.path
        for direc in direcList:
            tempWorkDir = tempWorkDir.subdirectories[direc]
        return tempWorkDir

    def getPath(self):
        '''Returns the working directory as a string'''
        pathAsString = '/' + '/'.join(self.workingDirectory)
        return pathAsString

    def changeDir(self, path):
        '''Changes the directory to the supplied path'''
        self.workingDirectory = path.iterList.copy()
        self.workDir = path.directory
        return 0

    def make(self, path, fileName, content=None):
        '''Makes an item of the specified type'''
        if fileName in path.directory.files:
            return -1
        else:
            path.directory.files[fileName] = File(fileName, content)
            self.workDir = self.getDirectory(self.workingDirectory)
            return 0

    def makeDirectory(self, path, dirName):
        if dirName in path.directory.subdirectories:
            return -1
        else:
            path.directory.subdirectories[dirName] = Directory()
            self.workDir = self.getDirectory(self.workingDirectory)
            return 0

    def remove(self, path, name, isDirectory=False):
        '''Removes the item at the given path'''
        if isDirectory:
            contents = path.directory.subdirectories
        else:
            contents = path.directory.files
        if name not in contents:
            return -1
        else:
            del contents[name]
            self.correctWorkingDirectory()
            self.workDir = self.getDirectory(self.workingDirectory)
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
        tempWorkDir = self.getDirectory(path.iterList)
        return tempWorkDir.files[fileName].getContent()

    def exit(self):
        '''Soft inits the system, call this when disconnecting'''
        self.workingDirectory = []
        self.workDir = self.getDirectory()

    def move(self, pathGet, nameGet, pathSet, nameSet, isDir=False):
        '''Moves the file at path 1 to the file at path 2'''
        if isDir:
            directory = pathGet.directory.subdirectories[nameGet]
            pathSet.directory.subdirectories[nameSet] = directory
            del pathGet.directory.subdirectories[nameGet]
        else:
            file = pathGet.directory.files[nameGet]
            pathSet.directory.files[nameSet] = file
            del getDirContents.files[nameGet]
            file.update(nameSet, file.getContent)
        self.correctWorkingDirectory()
        self.workDir = self.getDirectory(self.workingDirectory)
        return 0

    def checkIsValidPath(self, pathList):
        '''Checks the path provided exists'''
        tempWorkDir = self.getDirectory()
        for count, item in enumerate(pathList):
            if item not in tempWorkDir.subdirectories:
                return False
            else:
                tempWorkDir = tempWorkDir.subdirectories[item]
        return True

    def handleFileOutput(self, outType, output, message):
        name = output.iterList[-1]
        if outType == 1:
            output.directory.files[name].update(name, message)
        elif outType == 2:
            if output.directory.files[name].getContent() is not None:
                output.directory.files[name].update(name, output.directory.files[name].getContent() + message)
            else:
                output.directory.files[name].update(name, message)
        return 0

def getSysHash(fileName):
    with open('data/system/' + fileName, 'r') as file:
        fileData = json.loads(file.read())
    return fileData['hash']

def getSysContent(fileName):
    with open('data/system/' + fileName, 'r') as file:
        fileData = json.loads(file.read())
    return fileData['content']

def init(self):
    self.sysFileHashes = {
        'command.sys': getSysHash('command.json'),
        'boot.sys': getSysHash('boot.json')
        }

    self.sysFileContents = {
        'command.sys': getSysContent('command.json'),
        'boot.sys': getSysContent('boot.json')
        }
    with open('imports/DEFAULTSYSTEM.pkl', 'rb') as file:
        self.SYSTEM_DEFAULT_FILESYSTEM = pickle.load(file)
