__version__ = '1.1.0'

import json
import os
import commands, system
import pickle
import gzip

def save(sysCont):
    with gzip.open('saves/saveFile.dat', 'wb') as file:
        data = pickle.dumps(sysCont)
        file.write(data)

def load():
    if 'saveFile.dat' not in os.listdir('saves'):
        return False
    else:
        with gzip.open('saves/saveFile.dat', 'rb') as file:
            sysCont = pickle.load(file)
        return sysCont
        
