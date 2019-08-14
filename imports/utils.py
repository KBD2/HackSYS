__version__ = '1.0.1'

import random

def randIP():
    octets = []
    for octet in range(4):
        octets.append(random.randrange(0,256))
    return '.'.join(str(octet) for octet in octets)

def randOSCompany():
    possPrefixes = [
        "Saiyama",
        "Nanotech",
        "Boston",
        "Tesla",
        "Brunton",
        "Nanjing",
        "CamTech",
        "AyyMD"
        ]
    possMiddles = [
        "Systems",
        "Technology",
        "Computers",
        "Software",
        "OS"
        ]
    possSuffixes = [
        "Incorporated",
        "Corp.",
        "Ltd.",
        "Co."
        ]
    return ' '.join([
        random.choice(possPrefixes),
        random.choice(possMiddles),
        random.choice(possSuffixes)
        ])
