import json
import random
import hashlib
execName = input("Command name?")
protected = False
if input("Protected (y/n)") == "y":
    protected = True
contents = ''.join(str(random.choice([0,1])) for i in range(random.randrange(100,500)))
contentHash = hashlib.md5(bytes(contents, 'ascii')).hexdigest()
execData = {
    'name': execName,
    'content': contents,
    'hash': contentHash,
    'protected': protected
    }
execFilename = execName + '.json'
with open(execFilename, 'w') as file:
    json.dump(execData, file)
