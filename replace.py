# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 06:45:25 2014

@author: apple
"""
from os import walk
from imagehandler import executeCmd
from imageutil import ImageUtil
import sys

def replaceAll(strText, replaced, replacement):
    #print "waiting"
    return strText.replace(replaced, replacement)
    
    #Replace all in python
def findAllFiles(directory, files):    
    for (dirpath, dirnames, filenames) in walk(directory):
        files.extend([{"path":directory,"fullPath":dirpath + "/" + fl, "fileName":fl}  for fl in filenames])
        #print dirnames
        #for dr in dirnames:
        #    findAllFiles(directory +"/" + dr, files)

def insertPadding(filename, padding):
    pos = filename.rfind('.')
    if pos > 0:
        return filename[:pos] + padding + filename[pos:];
    return filename + padding

def generateAllImages(path):
    files = []
    findAllFiles(path, files)
    for fl in files:
        fullPath = fl.get('fullPath')
        subFix = getSubfix(fullPath)
        stripped = stripeSubfix(fullPath)
        if subFix=="JPG" or subFix=="JPEG" or subFix=="jpg" or subFix=="jpeg" or subFix=="png":
            if stripped[-2:] != 'tb' and stripped[-2:] != 'nm' and stripped[-2:] != 'cv':
                createAllImage(fullPath)

def createAllImage(fullPath):
    print "generate image for path:%s" % fullPath
    try:
        ImageUtil.resize(fullPath, 80, 'tb')
        ImageUtil.resize(fullPath, 180, 'cv')
        ImageUtil.resize(fullPath, 640, 'nm')
    except:
        print 'encounter error'

def stripeSubfix(filename):
    pos = filename.rfind('.')
    if pos > 0:
        return filename[:pos]
    return filename
    
def getSubfix(filename):
    pos = filename.rfind('.')
    if pos > 0:
        return filename[pos+1:]
    return ''
    
def cpFile(src, dest):
    command = 'cp %s %s' % (src, dest)
    print 'command is:%s', command
    executeCmd(command)

def findAllUnderDirectory(prefix, directory):
    #print "print directory"
    files = []
    findAllFiles(directory, files)
    #res = []
    for fl in files:
        if fl.get('fileName')[:2] == "EZ":
            fl['found'] = True
            fl['targetName'] = fl.get('fileName')[2:]
            fl['replaced'] = stripeSubfix(fl.get('fileName'))
            fl['replacement'] = fl['replaced'][2:]
        else:
            fileName = fl.get('fileName')
            if fileName.endswith('.h') or fileName.endswith('.H') or fileName.endswith('.m') or fileName.endswith('.M'):
                fl['isSource'] = True
            else:
                fl['isSource'] = False
            fl['found'] = False
            fl['targetName'] = fl.get('fileName')        
    return files


def getContent(fullPath):
    with open(fullPath, 'r') as content_file:
        return content_file.read()
        
def saveFile(content, fullPath):
    with open(fullPath,'w') as f:
        f.write(content)
#the main process will handle the whole thing.
#I love this game.
def mainProcess(prefix, directory, destDir):
    files = findAllUnderDirectory(prefix, directory)
    for qualifiedFile in files:
        
        if not qualifiedFile.get('isSource'):
            cpFile(qualifiedFile.get('fullPath'), destDir+"/"+qualifiedFile.get('fileName'))
            continue
        strText = getContent(qualifiedFile.get('fullPath'))
        for item in files:
            if item['found']:
                strText = replaceAll(strText, item.get('replaced'), item.get('replacement'))
            else:
                print 'completed text'
        saveFile(strText, destDir+"/"+qualifiedFile.get('targetName'))

if __name__ == "__main__":
    path = sys.argv[1]
    #destPath = sys.argv[2]
    #print 'start processing %s to destPath %s' % (path, destPath)
    #mainProcess('EZ', path, destPath)
    generateAllImages(path)

    