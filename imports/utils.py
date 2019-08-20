__version__ = '1.1.3'

import random
import time
from colorama import Fore
from imports import system

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

def serverBootSequence(sys, terminal):
    terminal.out(sys.OSManu, Fore.WHITE)
    time.sleep(1)
    terminal.out("Validating Boot Files", Fore.WHITE, True, False)
    for i in range(3):
        time.sleep(0.5)
        terminal.out(".", Fore.WHITE, True, False)
    terminal.out("\t", Fore.BLACK, True, False)
    time.sleep(0.5)
    if sys.status == system.Statuses.UNBOOTABLE:
        terminal.error("[BOOT.SYS MISSING]")
        return -1
    else:
        terminal.out("[OK]")
    terminal.out("{}KB Memory ({}KB extended)".format(
        2**random.randint(10,14),
        2**random.randint(10,14)
        ), Fore.WHITE)
    time.sleep(0.5)
    terminal.out("{}\" Disk".format(random.choice([3.5,5.2])), Fore.WHITE)
    time.sleep(0.5)
    terminal.out("Checking Disk", Fore.WHITE, True, False)
    for i in range(3):
        time.sleep(0.5)
        terminal.out(".", Fore.WHITE, True, False)
    terminal.out('')
    for i in range(8):
        if random.randrange(0,4) == 0:
            terminal.out("BLOCK {}\t\t\t\t".format(i), Fore.WHITE, True, False)
            terminal.error("[ERROR]")
        else:
            terminal.out("BLOCK {}\t\t\t\t".format(i), Fore.WHITE, True, False)
            terminal.out("[OK]")
    terminal.out("Connecting to Network", Fore.WHITE, True, False)
    for i in range(3):
        time.sleep(0.5)
        terminal.out(".", Fore.WHITE, True, False)
    terminal.out("\nIP Address: {}".format(sys.IP), Fore.WHITE)
    terminal.out("System OK Proceed to terminal", Fore.WHITE)
    time.sleep(0.5)
    return 0
