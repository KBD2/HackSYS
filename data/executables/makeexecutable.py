import json
import random
import hashlib
execNames = open('commandlist.txt', 'r').read().split('\n')
for i in execNames:
    contents = ''.join(str(random.choice([0,1])) for i in range(random.randrange(100,500)))
    contentHash = hashlib.md5(bytes(contents, 'ascii')).hexdigest()
    execData = {
        'name': i,
        'content': contents,
        'hash': contentHash
        }
    execFilename = i + '.json'
    with open(execFilename, 'w') as file:
        json.dump(execData, file)
