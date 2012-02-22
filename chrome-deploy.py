# -*- coding: utf-8 -*-
#
# Purpose:
#    Find chrome-win32-<revision>.zip file in the current directory,
#    having the biggest revision, and extract it to destination directory.
#
# Requirements: 
#    Python
#    PyWin32 (http://sourceforge.net/projects/pywin32/) [Optionally]
#

import os
import shutil
import zipfile


DESTINATION = "W:/portable/_backup/chrome_my/Application"
EXCLUDES = [
  "Dictionaries",
  "extensions"
]


def find_latest_dist():
    dist, max_num = "", 0

    for name in sorted(os.listdir(".")):
        if name.startswith("chrome-win32-"):
            num = int(name[13:-4])
            if num > max_num:
                dist, max_num = name, num
    return dist

def extract(dist):
    f = zipfile.ZipFile(dist, "r")
    f.extractall()

def clean_and_replace_files(src, dest, excludes):
    for name in os.listdir(dest):
        if name in EXCLUDES:
            continue
        path = os.path.join(dest, name)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    for name in os.listdir(src):
        srcpath = os.path.join(src, name)
        destpath = os.path.join(dest, name)
        if os.path.isdir(srcpath):
            shutil.copytree(srcpath, destpath)
        else:
            shutil.copy(srcpath, destpath)

def print_new_version(dest):
    try:
        from win32api import GetFileVersionInfo, LOWORD, HIWORD
        
        filename = os.path.join(dest, "chrome.exe")
        info = GetFileVersionInfo(filename, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        print "%d,%d,%d,%d" % (HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls))
    except:
        pass


dist = find_latest_dist()

print "Extracting %s..." % dist
extract(dist)

print "Replacing..."
clean_and_replace_files("./chrome-win32", DESTINATION, EXCLUDES)

print "Cleanup..."
shutil.rmtree("chrome-win32")

print_new_version(DESTINATION)
