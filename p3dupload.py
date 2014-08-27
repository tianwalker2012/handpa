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
        
    #executeCmd("ls -l")
    #executeCmd("ls")