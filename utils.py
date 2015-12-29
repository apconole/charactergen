#!/usr/bin/env python

import os
import random

try:
    import lxml.etree as ET
except:
    print "You must have ElementTree from lxml.etree"
    print "installed correctly in your PYTHONPATH"
    raise Exception("No lxml found")

def stat_xp_percent(statval):
    if statval >= 13 and statval < 16:
        return 5
    elif statval >= 16:
        return 10
    return 0

def get_stat_modifier(stat):
    if stat < 4:
        return -3
    elif stat >= 3 and stat <= 5:
        return -2
    elif stat >= 6 and stat <= 8:
        return -1
    elif stat >= 9 and stat <= 12:
        return 0
    elif stat >= 13 and stat <= 15:
        return 1
    elif stat >= 16 and stat <= 17:
        return 2
    return 3

def get_paths():
    paths = ["./", "/usr/share/chargen/backgrounds/"]
    if os.getenv("CHARGEN_PATH"):
        paths.insert(0, os.environ["CHARGEN_PATH"] + '/')
    return paths

def get_names(name):
    names = name.split(' ')

    if len(names) == 1:
        return names[0], ''
    
    return names[0], names[1]

def background_from():
    return random.choice(["decends from", "was adopted by", "knows only", "is born of", "hails from", "was raised by"])

def dieroll(sides=6, times=1):
    result = 0
    while times is not 0:
        result += random.randint(1, sides)
        times -= 1
    return result

def gen_stat(modifier, floor=3, ceiling=18):
    initial = dieroll(6, 3)
    initial += int(modifier)
    if initial < floor:
        initial = floor
    if initial > ceiling:
        initial = ceiling
    return initial

def read_xml_data(filename):
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except:
        root = None
    return root
