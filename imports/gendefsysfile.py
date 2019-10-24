"""
Generates a pickled file containing the
default system directories.
"""
from system import (Directory, File)
import pickle
import json

top = Directory()
top.subdirectories = {
    'home': Directory(),
    'bin': Directory(),
    'sys': Directory(),
    'log': Directory()
    }
top.subdirectories['sys'].files = {
    'command.sys': File('command.sys', json.load(open('../data/system/command.json', 'r'))['content']),
    'boot.sys': File('boot.sys', json.load(open('../data/system/boot.json', 'r'))['content'])
    }

with open('DEFAULTSYSTEM.pkl', 'wb') as file:
    pickle.dump(top, file)
