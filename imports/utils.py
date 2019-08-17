__version__ = '1.1.0'

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

def randSystemName():
    possPrefixes = [
        "com.",
        "ext.",
        "net.",
        "ftp.",
        "ssh.",
        "web."
        ]
    possMiddles = [
        "google.",
        "apple.",
        "webserver.",
        "website.",
        "application.",
        "government.",
        "yahoo.",
        "foundation."
        ]
    possSuffixes = [
        "4Chan",
        "Maps",
        "Connection",
        "Surveillance",
        "HiddenCamera",
        "Suspicious",
        "NotTheFBI",
        "127.0.0.1",
        "Virus",
        "Backend",
        "Frontend",
        "Status",
        "System",
        "FreeMovies",
        "Private",
        "Hack",
        "Dark",
        "Witness",
        "SCP"
        ]
    return ''.join([
        random.choice(possPrefixes),
        random.choice(possMiddles),
        random.choice(possSuffixes)
        ])
