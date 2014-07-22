# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 15:41:17 2014

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
import pytz


class MobileCapture:
    def GET(self):
        return self.POST()
    def POST(self):
        params = web.input()
        randNum = random.randint(1, 200)
        if not params:
            params = {
            #"latitude":31.2,
            #"longitude":121.6,
            #"flashFlag":"client%i" % randNum,
            #"disLimit":12
            }
        params['rand'] = randNum
        render = web.template.render('templates')
        return render.phototake(params)