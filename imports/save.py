__version__ = '0.0.2'

import json
import os
import commands, system
import pickle

def save(sysCont):
    with open('saves/saveFile.pkl', 'wb') as file:
        pickle.dump(sysCont, file)

def load():
    if 'saveFile.json' not in os.listdir('saves'):
        return False
    else:
        with open('saves/saveFile.pkl', 'rb') as file:
            sysCont = pickle.load(file)
        return sysCont
        
