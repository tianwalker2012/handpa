# -*- coding: utf-8 -*-
"""
Created on Sat Jun  7 21:56:57 2014

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

chinaTime = timezone('Asia/Shanghai')

def distance_on_unit_sphere(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    arc = math.pi/2.0
    try:
        degrees_to_radians = math.pi/180.0
        
        # phi = 90 - latitude
        phi1 = (90.0 - lat1)*degrees_to_radians
        phi2 = (90.0 - lat2)*degrees_to_radians
        # theta = longitude
        theta1 = long1*degrees_to_radians
        theta2 = long2*degrees_to_radians
        
        # Compute spherical distance from spherical coordinates.
        
        # For two locations in spherical coordinates 
        # (1, theta, phi) and (1, theta, phi)
        # cosine( arc length ) = 
        #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
        # distance = rho * arc length
    
        cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
        math.cos(phi1)*math.cos(phi2))
        if cos < 0.001:
            arc = 0
        else:
            arc = math.acos( cos )
    except:
        web.debug('encounter exception %r %r %r %r' % (lat1, long1, lat2, long2))
        # Remember to multiply arc by the radius of the earth 
        # in your favorite set of units to get length.
    return arc * 6378.1

def cleanPhoto4Wall(photo):
    res = {}
    person = MongoUtil.fetch('persons',{'_id':photo.get('personID')})    
    res['name'] = person.get('name')
    res['avatar'] = person.get('avatar')
    res['screenURL'] = photo.get('screenURL')
    #res['comments'] = photo.get('convers')
    if len(photo.get('conversations')) > 0:
        res['comments'] = photo.get('conversations')[0]['text']
    web.debug('fill res:%s' % person.get('name'))
    return res;

def cleanChat(photoChat):
    if photoChat.get('_id'):
        photoChat['chatID'] = str(photoChat['_id'])
        photoChat.pop('_id', None)
    if photoChat.get('createdTime'):
        photoChat['createdTime'] = str(photoChat['createdTime'])
    return photoChat

class PhotoWallDisplay:
    def GET(self):
        return self.POST()
    def POST(self):
        params = web.input()
        randNum = random.randint(1, 200)
        if not params:
            params = {
            "latitude":31.2,
            "longitude":121.6,
            "flashFlag":"client%i" % randNum,
            "disLimit":12
            }
        params['rand'] = randNum
        render = web.template.render('templates')
        return render.photowall(params)

class PhotoWall:
    def POST(self):
        return self.GET()

    def GET(self):
        params = web.data()
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        #web.debug("photo operation data:"+ str(params)+","+str(userSession))
        web.debug('raw data:%r' % params)        
        jsons = simplejson.loads(params)
        web.debug('chat detail:%r' % jsons)
        cmd = jsons['cmd']
        if cmd == 'add':
            return self.addComments(userSession, jsons)
        elif cmd == 'query':
            return self.queryPhotos(userSession, jsons)
    
    def queryPhotos(self, userSession, jsons):
        flashFlag = jsons.get('flashFlag')
        longitude = jsons.get('longitude')
        latitude = jsons.get('latitude')
        disLimit = jsons.get('disLimit')
        flag = None
        startDate = None
        if flashFlag:
            flag = MongoUtil.fetch('PhotoFlash', {'flashflag':flashFlag})
            if not flag:
                #flag = {'flashflag':flashFlag, 'fetchedTime':datetime.now(chinaTime)+timedelta(hours = 8)}
                MongoUtil.save('PhotoFlash', flag)
            else:
                startDate = flag.get('fetchedTime')
        #,  "createdTime":{'$gt':startDate}
        conds = {'$nor':[{'deleted':True}], "uploaded":True, 'longtitude':{'$gt':0.0}}
        if startDate:
            conds['createdTime'] = {'$gt':startDate}
        photos = MongoUtil.fetchPage('photos',conds ,0,20,[('createdTime',-1)])
        res = []        
        for pt in photos:
            lat1 = pt.get('latitude')
            lg1 = pt.get('longtitude')
            dis = distance_on_unit_sphere(latitude, longitude, lat1, lg1)
            if not disLimit or dis < disLimit:            
                res.append(cleanPhoto4Wall(pt))
            web.debug('photo %s, plat %r, plong %r, qlat %r, qlong %r, max dis:%r, actual dis:%r' % (str(pt.get('_id')), lat1, lg1, latitude, longitude, disLimit, dis))
        
        if flag and photos.count():
            flag['fetchedTime'] = datetime.now(chinaTime)+timedelta(hours = 8)
            MongoUtil.update('PhotoFlash', flag)
        elif not flag:
            flag = {'flashflag':flashFlag, 'fetchedTime':datetime.now(chinaTime)+timedelta(hours = 8)}
            MongoUtil.save(flag)
        web.debug('res %i,photoSize:%i' % (len(res), photos.count()))
        return simplejson.dumps(res)
        
    def queryComments(self, userSession, jsons):
        
        return simplejson.dumps(res)
        #web.debug('full result:%s' % fullRes)
        #return '{}'#fullRes
            
        #ph['createdTime'] = datetime.strptime(ph['createdTime'], '%Y-%m-%d %H:%M:%S.%f')
    def addComments(self, userSession, jsons):
        return '{}'
