#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import web
import imagehandler as util
from os import walk
import os
import os.path
import replace
import sys
from datetime import datetime, timedelta
from mongoUtil import MongoUtil
from bson.objectid import ObjectId
from imageutil import ImageUtil
import re
import math
import string
import random
from random import randint
from pytz import timezone
import hashlib
import threading

chinaTime = timezone('Asia/Shanghai')
def makeIfNone(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)


def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"

def zipTo(zipFile, directory):
	"""Will zip the file to the specified directoy"""
	cmd = "unzip %s -d %s" % (shellquote(zipFile), shellquote(directory))
	cmdResult = util.executeCmd(cmd)
	print "zip result %s" % cmdResult
	#fileName = os.path.basename(zipFile)
	#destFile = os.path.join(directory, fileName)
	#cmdResult = util.executeCmd("cd %s" % directory)
	#print "cd the directory:%s" % cmdResult
	#cmd = "unzip %s -d %s" % () 

def findAllFiles(directory, files):    
    for (dirpath, dirnames, filenames) in walk(directory):
    	if len(filenames):
    		workName = os.path.basename(dirpath)
    		print "works %s, %r, %r" % (dirpath, workName, filenames)
    		filenames.sort()
    		fullNames = []
    		sequence = 0
    		for fn in filenames:
    			subFix = replace.getSubfix(fn).lower()
    			if subFix == 'jpg' or subFix == 'jpeg' or subFix == 'png' or subFix == 'gif':  
    				fullNames.append({"fullPath":os.path.join(dirpath, fn), "sequence":sequence})
    				sequence += 1
    		if len(fullNames.count):
        		files.append({"workName":workName,"fullPath":dirpath, "files":fullNames})


def addTask(personID, taskName):
	store={"personID":personID,"completed":True,"isPrivate":False,"name":taskName,"createdTime":datetime.now(chinaTime)+timedelta(hours=8)}
	MongoUtil.save('PhotoTask', store)
	return str(store.get('_id'))

def addPhoto(taskID, sequence, imageFile):
		#taskID = x["taskID"]
    	isOriginal = True
    	storedDir = '/home/ec2-user/root/www/static/'
    	if not os.path.exists(storedDir):
            storedDir = '%s/static/%s/' % (os.getcwd(),taskID)  
        else:
            storedDir = '/home/ec2-user/root/www/static/'+taskID+'/'

        makeIfNone(storedDir)
        web.debug('final stored dir:%s, %s' % (storedDir,isOriginal))
        hostName = "www.pin3d.cn"
        baseURL = 'http://'+ hostName +'/static/'+taskID+'/'
        #filePath = x['myfile'].filename.replace('\\','/').split('/')[-1]

        postFix = replace.getSubfix(imageFile)
        hashedName = hashlib.md5(str(datetime.now(chinaTime))).hexdigest() + '.' + postFix
        destname = os.path.join(storedDir,hashedName)
        #cpCmd = "cp %s %s" % (shellquote(imageFile), shellquote(destname))
        #cmdResult = util.executeCmd(cpCmd)
        #print "cmd:%s, result:%s" % (cpCmd, cmdResult)
        ImageUtil.squareCrop(imageFile, destname)
        ImageUtil.resize(destname, 80, 'tb')
        ImageUtil.resize(destname, 180, 'cv')
        ImageUtil.resize(destname, 640, 'nm')
        #storedPhoto['screenURL'] = baseURL+hashedName
        remoteURL = baseURL + hashedName
       	storedPhoto = {
       	'taskID':taskID, 
       	'sequence':int(sequence), 
       	'remoteURL':remoteURL, 
       	'originalURL':remoteURL}
        MongoUtil.save('StoredPhoto', storedPhoto)
        return remoteURL

def uploadWorks(files, personID):
	"""Will  upload the works"""
	print "will upload:%s, %i" % (personID, len(files))
	for photo in files:
		print "%s, fullPath:%s, fileCount:%i" % (photo['workName'], photo['fullPath'], len(photo['files']))
		taskID = addTask(personID, photo['workName'])
		print "taskID:%s" % taskID
		for dp in photo['files']:
			remoteURL = addPhoto(taskID, dp['sequence'], dp['fullPath'])
			print 'remoteURL:%s' % remoteURL

def uploadAllZip(zipFile, zipDir, personID):
	def innerThread():
		print "will zip %s to %s" % (zipFile, zipDir)
		zipTo(zipFile, zipDir)
		fileNames = []
		findAllFiles(zipDir, fileNames)
		print "the file count:%i" % len(fileNames)
		uploadWorks(fileNames, personID)
		cmd = "rm -rf %s" % zipDir
		cmdRes = util.executeCmd(cmd)
		print "%s result:%s" % (cmd, cmdRes)
	thr = threading.Thread(target=innerThread, args=[])
	thr.start()
	print 'uploadAllZip completed'


if __name__ == "__main__":
	zipFile = sys.argv[1]
	zipDir = sys.argv[2]
	person = MongoUtil.fetch('P3DUser', {'uploader':True})
	if not person:
		person =  {"uploader":True,"name":"上传客","joined":True, "mobile":"16888","password":"16888","createTime":datetime.now(chinaTime)+timedelta(hours=8)}
	 	MongoUtil.save("P3DUser", person)
	uploadAllZip(zipFile, zipDir, str(person.get('_id')))
	 
