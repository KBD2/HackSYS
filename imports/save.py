__version__ = '0.0.1'

import json
import os
from imports import (commands, system)

def save(sysCont):
    with open('saves/saveFile.json', 'w') as file:
        saveData = {}
        for sys in sysCont.systemDict:
            saveData[sys] = [
                sysCont.systemDict[sys].IP,
                sysCont.systemDict[sys].OSManu,
                sysCont.systemDict[sys].status.name,
                sysCont.systemDict[sys].aliasTable,
                sysCont.systemDict[sys].connected,
                sysCont.systemDict[sys].fileSystem.path
                ]
        json.dump(saveData, file)

def load(sysCont):
    if 'saveFile.json' not in os.listdir('saves'):
        return False
    else:
        with open('saves/saveFile.json', 'r') as file:
            saveData = json.loads(file.read())
            for sys in saveData:
                sysCont.systemDict[sys] = system.System(
                    saveData[sys][0],
                    saveData[sys][1],
                    {
                        'connected': saveData[sys][4],
                        'executables': []
                    }
                    )
                sysCont.systemDict[sys].aliasTable = saveData[sys][3]
                sysCont.systemDict[sys].status = system.Statuses[saveData[sys][2]]
                sysCont.systemDict[sys].fileSystem.path = saveData[sys][5]
                sysCont.systemDict[sys].fileSystem.workDirContents = sysCont.systemDict[sys].fileSystem.getContents()
                sysCont.systemLookup[saveData[sys][0]] = sys
        return True
        