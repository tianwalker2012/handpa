# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 06:45:25 2014

@author: apple
"""
from os import walk
from imagehandler import executeCmd
import sys
import os

def replaceAll(strText, replaced, replacement):
    #print "waiting"
    return strText.replace(replaced, replacement)
    
    #Replace all in python
def appendSubDirs(dirs):
    res = []
    for dr in dirs:
        res.append(dr)
    return "/".join(res)

def subtractDir(baseDir, fullDir):
    subDir = fullDir[len(baseDir):];
    if subDir[:1] == '/':
        return subDir[1:]
    return subDir  
  
def findAllFiles(directory, files, subDir):    
    for (dirpath, dirnames, filenames) in walk(directory):
        files.extend([{"path":directory,"fullPath":dirpath + "/" + fl, "fileName":fl, "subDir":subtractDir(directory,dirpath)}  for fl in filenames])
        #print filenames
        #print dirnames
        #for dr in dirnames:
        #    findAllFiles(directory +"/" + dr, files, subDir+"/"+dr if subDir != "" else dr)


def makeIfNone(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)

def stripeSubfix(filename):
    pos = filename.rfind('.')
    if pos > 0:
        return filename[:pos]
    return filename
    
def cpFile(src, dest):
    command = 'cp %s %s' % (src, dest)
    print 'command is:%s', command
    executeCmd(command)



def findAllUnderDirectory(prefix, directory):
    #print "print directory"
    files = []
    findAllFiles(directory, files, "")
    #res = []
    for fl in files:
        if fl.get('fileName')[:2] == "EZ":
            fl['found'] = True
            fl['replaced'] = stripeSubfix(fl.get('fileName'))
            fl['replacement'] = fl['replaced'][2:]
            fl['isSource'] = True
            fl['targetName'] = fl['subDir']+"/"+fl.get('fileName')[2:] if fl['subDir'] != "" else fl.get('fileName')[2:]
        else:
            fileName = fl.get('fileName')
            if fileName.endswith('.h') or fileName.endswith('.H') or fileName.endswith('.m') or fileName.endswith('.M'):
                fl['isSource'] = True
            else:
                fl['isSource'] = False
            fl['found'] = False
            fl['targetName'] = fl['subDir']+"/"+fl.get('fileName') if fl['subDir'] != "" else fl.get('fileName')
            #fl['targetName'] = fl['subDir']+"/"+ fl.get('fileName')
        
    
    return files


def getContent(fullPath):
    with open(fullPath, 'r') as content_file:
        return content_file.read()
        
def saveFile(content, fullPath):
    pos = fullPath.rfind('/')
    if(pos > 0):
        pathName = fullPath[:pos]
        makeIfNone(pathName)
    with open(fullPath,'w') as f:
        f.write(content)
#the main process will handle the whole thing.
#I love this game.
def mainProcess(prefix, directory, destDir):
    files = findAllUnderDirectory(prefix, directory)
    for qualifiedFile in files:
        fullDestDir = destDir+"/"+qualifiedFile.get('subDir')+"/"
        print 'FullDestDir:%s' % fullDestDir
        makeIfNone(fullDestDir)
        if not qualifiedFile.get('isSource'):
            cpFile(qualifiedFile.get('fullPath'), fullDestDir + qualifiedFile.get('fileName'))
            continue
        strText = getContent(qualifiedFile.get('fullPath'))
        for item in files:
            if item['found']:
                strText = replaceAll(strText, item.get('replaced'), item.get('replacement'))
            else:
                print 'completed text'  
        saveFile(strText, fullDestDir+qualifiedFile.get('targetName'))

def mainProcessTest(prefix, directory, destDir):
    files = findAllUnderDirectory(prefix, directory)
    for curFile in files:
        print 'subDir:%s,fullPath:%s, isSource:%i, targetName:%s, replaced:%s, replacement:%s,subDir:%s' % (curFile.get('subDir'),curFile.get('fullPath'), curFile.get('isSource'),curFile.get('targetName'), curFile.get('replaced'), curFile.get('replacement'), curFile.get('subDir')) 
if __name__ == "__main__":
    path = sys.argv[1]
    destPath = sys.argv[2]
    print 'start processing %s to destPath %s' % (path, destPath)
    #mainProcess('EZ', path, destPath)
    mainProcess('EZ', path, destPath)
    