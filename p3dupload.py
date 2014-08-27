# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 19:15:18 2014

@author: apple
"""
import web
import simplejson
import hashlib
from datetime import datetime, timedelta
from mongoUtil import MongoUtil
from bson.objectid import ObjectId
from imageutil import ImageUtil
from pushSender import sendPush
from i18nStrings import localInfo
from notify import cleanNote
import re
import os
import math
import string
import random
from random import randint
from pytz import timezone
from imagehandler import executeCmd
import pytz
import sys
if __name__ == "__main__":
    print 'i am all right'
    searchDir = sys.argv[1]
    #if len(sys.argv):
    print searchDir
    tasks = ["53fdc9a321ae7a478025476c","53fdc9b221ae7a478025476d","53fdc9bf21ae7a478025476e"]
    pos = 0
    curTask = None
    sequence = 0    
    for subdir, dirs, files in os.walk(searchDir):
        for curDir in dirs:
            if curDir == 'zoomimages':
                curTask = tasks[pos]
                sequence = 0
                pos += 1
                print 'break:%s, sequence:%i' % (curTask, sequence)
            else:
                print 'curDir:%s' % curDir
                #break;
            for file in files:
                if len(file) < 3 or not (file[-3:]=='png' or file[-3:]=='jpg'):
                    print 'break:%s' % file                    
                    break;                    
                filePath = os.path.join(subdir, file)  
                cmd = 'curl -i "www.enjoyxue.com:8080/p3d/upload" -XPOST   -F "myfile=@/%s" -F "taskID=%s" -F "sequence=%i" --http1.0' % (filePath, curTask, sequence)
                print cmd
                sequence += 1
                executeCmd(cmd)
    #executeCmd("ls -l")
    #executeCmd("ls")