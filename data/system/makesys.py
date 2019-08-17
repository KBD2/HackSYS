import json
import random
import hashlib
sysNames = open('syslist.txt', 'r').read().split('\n')
for i in sysNames:
    contents = ''.join(str(random.choice([0,1])) for i in range(random.randrange(100,500)))
    contentHash = hashlib.md5(bytes(contents, 'ascii')).hexdigest()
    sysData = {
        'content': contents,
        'hash': contentHash
        }
    sysFilename = i + '.json'
    with open(sysFilename, 'w') as file:
        json.dump(sysData, file)
