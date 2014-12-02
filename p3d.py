# -*- coding: utf-8 -*-
"""
Created on Fri Aug 15 10:54:59 2014

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
import urlparse
from replace import insertPadding
import ziphandler

chinaTime = timezone('Asia/Shanghai')
smsCmd = 'curl "http://utf8.sms.webchinese.cn/?Uid=tiange&Key=a62725bf421644799a8d&smsMob=%s&smsText=短信验证码是:%s"'

def sendSms(mobile, message):
    cmd = smsCmd % (mobile, message)
    res = ""
    res = os.system(cmd)
    web.debug('sms result %s, %s' % (res, message))

def makeIfNone(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)

def cleanUser(user):
    strID = str(user['_id'])
    strDate = str(user['createTime'])
    user.pop('_id', None)
    user['personID'] = strID
    user['createTime'] = strDate
    return user

def cleanInfoPoint(infoPoint):
    infoPoint['infoID'] = str(infoPoint.get('_id'))
    infoPoint.pop('_id', None)
    return infoPoint

def fillTask(photoTask, personID):
    tk = photoTask
    likedList = tk.get('likedList') if tk.get('likedList') else [] 
    favorList = tk.get('favorite') if tk.get('favorite') else []
    tk['liked'] = personID in likedList
    tk['isFavor'] = personID in favorList
    tk.pop('likedList', None)
    tk.pop('favorite', None)
    tk['likedCount'] = len(likedList)
    tk['favorCount'] = len(favorList)
    photos = MongoUtil.fetchSome('StoredPhoto', {'taskID':str(photoTask['_id'])},[('sequence', 1)])
    phs = []
    for ph in photos:
        infoPts = MongoUtil.fetchSome('InfoPoint', {'photoID':str(ph['_id'])})
        if infoPts:        
            ph['infos'] = [cleanInfoPoint(infoPt) for infoPt in infoPts]
        phs.append(cleanStoredPhoto(ph))
    taskID = str(photoTask['_id'])
    photoTask.pop('_id', None)
    photoTask['createdTime'] = str(photoTask['createdTime'])
    photoTask['photos'] = phs;
    photoTask['taskID'] = taskID
    return photoTask

def cleanTask(photoTask):
    tk = photoTask
    likedList = tk.get('likedList') if tk.get('likedList') else [] 
    favorList = tk.get('favorite') if tk.get('favorite') else []
    tk['likedCount'] = len(likedList)
    tk['favorCount'] = len(favorList)
    taskID = str(photoTask.get('_id'))
    photoTask.pop('_id', None)
    photoTask['createdTime'] = str(photoTask.get('createdTime'))
    #sphotoTask['photos'] = phs;
    photoTask['taskID'] = taskID
    return photoTask

def fetchPhotoInfo(photoID):
    infoPts = MongoUtil.fetchSome('InfoPoint', {'photoID':photoID})
    web.debug('info for:%s=%i' % (photoID, infoPts.count()))
    return [info for info in infoPts]
    
def cleanPerson(person):
    if '_id' in person:
        pid = person['_id']
        #del person['_id']
        person.pop('_id', None)
        person['personID'] = str(pid)
    if 'password' in person:
        del person['password']
    if 'createTime' in person:
        person['createTime'] = str(person['createTime'])
    person.pop('friends', None)
    return person

def createRandomStr():
    lst = [random.choice(string.digits).lower() for n in xrange(6)]
    return "".join(lst)


class PhotoOperation:
    def GET(self, optType):
        return self.POST(optType)
    def POST(self, optType):
        params = web.input()
        isDelete = params.get("isDelete")
        taskID = params.get("taskID")
        personID = params.get("personID")
        #isFavor = param.get('isFavor')
       
        task = MongoUtil.fetchByID('PhotoTask', ObjectId(taskID))
        web.debug("isDelete:%r, taskID:%r, personID:%r, likedList:%r, favorList:%r, optType:%s" % (isDelete, taskID, personID,task.get('likedList'), task.get('favorite'), optType))
        returnedList = []    
        if optType == "like":            
            taskList = [] if not task.get('likedList') else task.get('likedList')
            if isDelete=="1":
                taskList = [x for x in taskList if x != personID]
            else:
                taskList.append(personID)
            web.debug("before stored like taskList %r" % taskList)
            task['likedList'] = taskList
            MongoUtil.update('PhotoTask', task)
            returnedList = taskList
        elif optType == 'favorite':
            favorList = [] if not task.get('favorite') else task.get('favorite')
            if isDelete=="1":
                favorList = [x for x in favorList if x != personID]
            else:
                favorList.append(personID)
            web.debug("before stored favor taskList %r" % favorList)
            task['favorite'] = favorList
            MongoUtil.update('PhotoTask', task)
            returnedList = favorList
        return simplejson.dumps(returnedList)
                
class P3DRegister:
    def GET(self):
        return self.POST()
    def POST(self):
        params = web.input()
        #web.debug("post inputs:"+ str(params))
        #uploaded = simplejson.loads(params)
        #dups = DataUtil.findDuplicated(uploaded)
        #mock = None
        #if 'mock' in uploaded: 
        #    mock = uploaded['mock']
        
        personID = params.get('personID')
        passCode = params.get('passCode')
        mobile = params.get('mobile')
        storedPassCode = None
        if mobile:
            storedPassCode = MongoUtil.fetch('p3dpasscode', {'mobile':mobile})
        if passCode != '167791' and (not storedPassCode or storedPassCode.get('passCode') !=  passCode):
            web.ctx.status = '406 Not Allow'
            return 'passcode error'
        person = None
        if personID:
            person = MongoUtil.fetchByID('P3DUser', ObjectId(personID))
        
        if not person:
            person =  {"createTime":datetime.now(chinaTime)+timedelta(hours=8)}
            MongoUtil.save('P3DUser', person)
        
        params['_id'] = person['_id']
        params['joined'] = True
        MongoUtil.update('P3DUser', params)
        
        return simplejson.dumps(cleanPerson(params))


class P3DPerson:

    def GET(self, cmd):
       return self.process(cmd)
        
    def POST(self, cmd):
        return self.process(cmd)
        
    def saveNotExist(self, owner, friend):
        relation = MongoUtil.fetch('friendship', {'owner':owner,'friend':friend})
        if not relation:
            MongoUtil.create('friendship', {'owner':owner,'friend':friend, 'createdTime':datetime.now(chinaTime)+timedelta(hours = 8)})


    def queryByID(self, pid):
        #res = []
        #web.debug('pid: %r' % pids)
        #for pid in pids:         
        person = MongoUtil.fetchByID('P3DUser', ObjectId(pid))
        if person:
            web.debug("get person detail %r" % person.get('name'))
            return simplejson.dumps([cleanPerson(person)])
        return '[]'
    #who will invoke this?
    #Store photobook relations 
    #if person specifically want to be my friend
    def establishFriendship(self, owner, friend, isPhotoBook='0'):
        relation = MongoUtil.fetch('friendship', {'owner':owner,'friend':friend})
        if not relation:
            MongoUtil.create('friendship', {'owner':owner,'friend':friend, 'createdTime':datetime.now(chinaTime)+timedelta(hours=8),'photobook':'1' if isPhotoBook else '0'})
            return isPhotoBook
        else:
            return relation['photobook']
            
    #If not login, then each person use it's own name
    #If joined, every body use the name choose the user. 
    
    def updatePerson(self, person, userSession):
        pid = ObjectId(userSession)
        person['_id'] = pid
        person.pop('personID', None)
        MongoUtil.update('P3dUser', person)
        return '{}'
    
    def queryFriend(self, userSession, queryPid):
        """This is method to query all the people based on how many photo are combined by each other"""        
        #persons = MongoUtil.fetchSome('friendship', {'owner':ObjectId(userSession)})
        #for ps in persons:
        res = []
        #addedFriends = {}
        #exists = {}
        
        conds = {'personID':queryPid, 'deleted':False}
        if userSession != queryPid:
            conds = {'personID':queryPid,'deleted':False, 'hidden':False}
        friends = MongoUtil.fetchSome('friends', conds)
        if friends:
            #friends = pf.get('friends')
            #web.debug('got friend')
            for fid in friends:
                    person = MongoUtil.fetchByID('persons', ObjectId(fid.get('friendID')))
                    if person:
                        #addedFriends[pid] = True
                        res.append(cleanPerson(person))
        return simplejson.dumps(res)
                        
    def uploadMobile(self, mobiles, userSession):
        web.debug('will upload all the mobile')
        storeMobiles = MongoUtil.fetch('mobiles', {'personID':userSession})
        if storeMobiles:
            storeMobiles['mobiles'] = mobiles
            MongoUtil.update('mobiles', storeMobiles)
        else:
            MongoUtil.save('mobiles', {'personID':userSession, 'mobiles':mobiles})
        return '{}'

    def generatePassCode(self, mobile, userSession):
        web.debug('generate pass code')
        smsCode = MongoUtil.fetch('p3dpasscode', {'mobile':mobile})
        passCode = createRandomStr();  
        if smsCode:
            smsCode['passCode'] = passCode
            MongoUtil.update('p3dpasscode', smsCode)
        else:            
            MongoUtil.save('p3dpasscode', {'mobile':mobile, 'passCode':passCode})
        sendSms(mobile, passCode)
        return '{}';

    def process(self, cmd):
        params = web.input()
        #userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        userSession = params.get('personID')
        web.debug("data:"+ str(params)+","+str(userSession))
        #jsons = simplejson.loads(params)
        #cmd = params.get('cmd')
        #if not userSession:
        if cmd == 'passcode':
            return self.generatePassCode(params.get('mobile'), userSession)

       

        if cmd == 'login':
            mobile = params.get('mobile')
            password = params.get('password')
            person = MongoUtil.fetch('P3DUser', {'mobile':mobile, 'password':password})
            if person:
                return simplejson.dumps(cleanPerson(person))
            else:
                web.ctx.status = '406 Not Allow'
                return 'passcode error'
        if not userSession:            
            web.debug("No valid user")
            web.ctx.status = '406 No User'
            return 'No user'
        if cmd == 'mobile':
            return self.mobileQuery(params['mobiles'], userSession)
        elif cmd == 'personID':
            return self.queryByID(params.get('personID'))
        elif cmd == 'friend':
            fid = params.get('queryID')
            return self.queryFriend(userSession, fid)
        elif cmd == 'addFriend':
            fid = params.get('personID')
            return self.addFriend(userSession, fid)
        elif cmd == 'blockFriend':
            fid = params.get('personID')
            return self.blockFriend(userSession, fid)
        elif cmd == 'acceptFriend':
            fid = params.get('personID')
            return self.acceptFriend(userSession, fid)
        elif cmd == 'upload':
            return self.uploadPerson(params['persons'], userSession)
        elif cmd == 'update':
            return self.updatePerson(params, userSession)
        elif cmd == 'mobileupload':
            return self.uploadMobile(params['mobiles'], userSession)


    
class WebUploader:
    def GET(self):
        return self.POST()
    def POST(self):
        render = web.template.render('templates')
        #cookie = web.cookies(visitCount=0)
        personID = web.cookies(personID=None).personID
        web.debug('exist personID:%s' % personID)
        if not personID:
            user = {"createdTime":datetime.now(chinaTime)+timedelta(hours=8)}
            MongoUtil.save('P3dUser', user)
            web.setcookie('personID',str(user.get('_id')), 360000,path='/')
            personID = str(user.get('_id'))
        
        #imageURL = web.input().get('url')
        #iconURL = None
        #if imageURL:
        #    pos = imageURL.rfind('.jpg')
        #    if pos > 0:
        #        iconURL = imageURL[:pos] + "tb" + imageURL[pos:]
        web.debug("will render web uploader")
        return render.photoupload({"visitCount":0, "icon":None,"personID":personID})

class InfoPoint:
    def GET(self, cmd):
        return self.POST(cmd);
    def POST(self, cmd):
        params = web.input()
        for key in params:
            web.debug('param %s,%s' % (key, params[key]))
        if cmd == 'create':
            data = {'x':params.x, 
                    'y':params.y,
                    'photoID':params.photoID,
                    'title':params.title,
                    'type':params.type,
                    'comment':params.comment}
            
            MongoUtil.create('InfoPoint', data)
            return simplejson.dumps({'infoID':str(data.get('_id'))})
        elif cmd == 'update':
            data = {'x':params.x, 
                    'y':params.y,
                    'photoID':params.photoID,
                    'title':params.title,
                    'type':params.type,
                    'comment':params.comment}
            data['_id'] = ObjectId(params.infoID)
            MongoUtil.update('InfoPoint', data)
            return '{}'
        elif cmd == 'remove':
            MongoUtil.remove('InfoPoint', {'_id':ObjectId(params.infoID)})
            return '{}'

class Account:
    def GET(self, cmd):
        return self.POST(cmd)
    def POST(self, cmd):
        params = web.input()
        web.debug('params:%r' % params.get('personID'))
        if cmd == 'create':
            user = {"createTime":datetime.now(chinaTime)+timedelta(hours=8)}
            MongoUtil.save('P3dUser', user)
            return simplejson.dumps(cleanPerson(user))
        elif cmd == 'query':
            #tasks = None
            queryCond = {'$nor':[{'isPrivate':True}],'$or':[{'completed':True}, {'completed':'1'}]}
            start = int(params.start) if params.get('start') else 0
            limit = int(params.limit) if params.get('limit') else 18
            personID = params.get('personID')
            personal = params.get('personal')
            if personal:
                queryCond = {'personID':personID, '$or':[{'completed':True}, {'completed':'1'}]}
                #start = 0
                #limit = 200
            web.debug('cond:%r,start:%i,limit:%i' % (queryCond, start, limit)) 
            tasks = MongoUtil.fetchWithLimit('PhotoTask', queryCond, start, limit, [('createdTime', -1)])
            res = []            
            for tk in tasks:
                res.append(fillTask(tk, personID))
            return simplejson.dumps(res)
        elif cmd == 'clean':
            tasks = MongoUtil.fetchAll('PhotoTask')
            count = 0
            for tk in tasks:
                photos = MongoUtil.fetchSome('StoredPhoto', {'taskID':str(tk['_id'])})
                web.debug('photo count:%i, id:%s' % (photos.count(), str(tk['_id'])))
                if photos.count() == 0:
                    MongoUtil.remove('PhotoTask', {'_id':tk['_id']})
                    count += 1
            return '{"count":%i}' % count
                
class P3DShowQuery:
    def GET(self):
        return self.POST()
    def POST(self):
        params = web.input()
        photos = []
        if params.get('taskID'):
            photos = MongoUtil.fetchSome('StoredPhoto', {'taskID':params.taskID},[('sequence', 1)])
        pts = []
        def process(pht):
            pts.append(pht)
            return pht.get('remoteURL')
        imgUrls = [process(pt) for pt in photos];        
        #for pt in photos:
        infos = []
        i = 0
        for pt in pts:
            pinfos = fetchPhotoInfo(str(pt.get('_id')))
            for info in pinfos:
                web.debug('get info out')
                info['pos'] = i
                infos.append(info)
            i += 1
        #render = web.template.render('templates', globals={'simplejson':simplejson})
        #return render.show3d({"imagelist":imgUrls, "zoomlist":imgUrls,'infos':infos})
        return simplejson.dumps({"imagelist":imgUrls, "infos":infos})
def paddingList(urls, padding):
    return [insertPadding(url, padding) for url in urls]

class P3DShow:
    def GET(self):
        return self.POST()
        
    def POST(self):
        params = web.input()
        photos = [] 
        taskID = ""
        taskName = "未命名作品" 
        web.debug('query taskID:%s' % params.get('taskID'))
        task = {}
        owner = {}
        if params.get('taskID'):
            taskID = params.get('taskID')
            photos = MongoUtil.fetchSome('StoredPhoto', {'taskID':params.taskID},[('sequence', 1)])
            task = MongoUtil.fetchByID('PhotoTask',ObjectId(taskID))
            if task.get('name'):
                taskName = task.get('name')
        pts = []
        def process(pht):
            pts.append(pht)
            imagePath = urlparse.urlparse(pht.get('remoteURL')).path
            return imagePath
        imgUrls = [process(pt) for pt in photos];        
        #for pt in photos:
        infos = []
        pinList = []
        render = web.template.render('templates', globals={'simplejson':simplejson})
        return render.show3d({
            "thumbnail":simplejson.dumps(paddingList(imgUrls, "tb")), 
            "imageList":simplejson.dumps(paddingList(imgUrls, "nm")), 
            "zoomList":simplejson.dumps(imgUrls),
            "pinList":simplejson.dumps(pinList),
            "taskID":simplejson.dumps(taskID),
            "task":simplejson.dumps(cleanTask(task)),
            "owner":simplejson.dumps(owner), 
            "name":simplejson.dumps(taskName)})

class IDCreator:
    def GET(self, cmd):
        return self.POST(cmd)
    def POST(self, cmd):
        if cmd == 'create':
            params = web.input()
            store = {"personID":params.personID,"completed":False,"isPrivate":params.get("isPrivate"),     "createdTime":datetime.now(chinaTime)+timedelta(hours=8)}
            name = params.get('name')
            #count = params.get('count')
            if name:
                store['name'] = name
            MongoUtil.save('PhotoTask', store)
            res = {"id":str(store.get('_id'))}
            return simplejson.dumps(res)
        elif cmd == 'query':
            params = web.input()
            web.debug("query data:%r" % params)
            if params.get('taskID'):
                photoTask = MongoUtil.fetchByID('PhotoTask', ObjectId(params.taskID))
                if photoTask:
                    return simplejson.dumps(fillTask(photoTask, params.get("personID")))
            return '{}'
        elif cmd == 'update':
            params = web.input()
            completed = params.get('completed')
            if not completed:
                completed = False
            elif completed == '1':
                completed = True
            if params.get('taskID'):
                web.debug('params:%r' % params)
                storedParams = {'_id':ObjectId(params.get('taskID')),"completed":completed, "name":params['name'], "isPrivate":params['isPrivate']}
                MongoUtil.update('PhotoTask',storedParams)
            return '{}'
        elif cmd == 'delete':
            params = web.input()
            if params.get('taskID'):
                MongoUtil.remove('PhotoTask', {'_id':ObjectId(params.get('taskID'))})
            return '{}'
        return '{}'
def cleanStoredPhoto(storedPhoto):
    pid = str(storedPhoto.get('_id'))
    storedPhoto['photoID'] = pid
    storedPhoto.pop('_id', None)
    return storedPhoto

class RawPhotoUpload:
    def POST(self):
        x = web.input(file={})
        params = web.input()
        #storedDir = '/home/ec2-user/root/www/static/'+userSession+'/'
        #storedDir = '/home/ec2-user/root/www/static/'+taskID+'/'
        taskID = params.get('taskID')
        #sequenceID = params.get('seq')
        storedDir = '%s/static/%s/' % (os.getcwd(),taskID)         
        makeIfNone(storedDir)
        #web.debug('final stored dir:%s, %s' % (storedDir,isOriginal))
        baseURL = 'http://'+ web.ctx.env.get('HTTP_HOST') +'/static/'+taskID+'/'
        filePath = x['file'].filename.replace('\\','/').split('/')[-1]
        postFix = filePath.split('.')[-1]
        hashedName = hashlib.md5(filePath + str(datetime.now(chinaTime))).hexdigest() + '.' + postFix
        imageFileName = storedDir+hashedName;
        fout = open(imageFileName, 'w')
        fout.write(x.file.file.read())
        fout.close()
        remoteURL = baseURL + hashedName
        
        #task = MongoUtil.fetchByID('PhotoTask', ObjectId(taskID))
        result = {"url":remoteURL}
        return simplejson.dumps(result)


class BatchUploader:
    def GET(self, cmd):
        render = web.template.render('templates', globals={'simplejson':simplejson})
        person = MongoUtil.fetch('P3DUser', {'uploader':True})
        if not person:
            person =  {"uploader":True,"name":"上传客","joined":True, "mobile":"16888","password":"16888","createTime":datetime.now(chinaTime)+timedelta(hours=8)}
            MongoUtil.save("P3DUser", person)
        if cmd == "page":
            return render.batchupload({"personID":str(person.get('_id'))})
        else:
            return str(person.get('_id'))
    def POST(self, cmd):
        x = web.input(myfile={})
        personID = x.get('personID')
        web.debug('uploaded person:%s' % personID)
        if not personID:
            web.debug('quit for no personID')
            return '{}'
        storedDir = '/home/ec2-user/root/www/static/'
        if not os.path.exists(storedDir):
            storedDir = '%s/static/rawupload/' % os.getcwd()  
        else:
            storedDir = '/home/ec2-user/root/www/static/rawupload/'
        tmpFile = hashlib.md5(str(datetime.now(chinaTime))).hexdigest()
        storedFile = storedDir + tmpFile + ".zip"
        storedTmp = os.path.join(storedDir, tmpFile)
        makeIfNone(storedDir)
        fout = open(storedFile, 'w')
        fout.write(x.myfile.file.read())
        fout.close()
        web.debug('final stored File:%s' % storedFile)
        ziphandler.uploadAllZip(storedFile, storedTmp, personID)
        return storedFile

class WebUpload:
    def GET(self):
        return '{}'

    def POST(self):
        x = web.input()
        taskID = x["taskID"]
        photoID = x.get("photoID")
        sequence = x.get("sequence")
        isOriginal = x.get("isOriginal")
        #x = web.input(myfile={})
        #web.debug('data:%s', web.data()[:100]);
        pos = web.data()[:50].find('base64,');
        data = web.data()[pos+7:].decode('base64')
        storedDir = '/home/ec2-user/root/www/static/'
        if not os.path.exists(storedDir):
            storedDir = '%s/static/%s/' % (os.getcwd(),taskID)  
        else:
            storedDir = '/home/ec2-user/root/www/static/'+taskID+'/'   
        makeIfNone(storedDir)
        web.debug('final stored dir:%s' % storedDir)
        baseURL = 'http://%s/static/%s/' % (web.ctx.env.get('HTTP_HOST'), taskID)
        #filePath = x['myfile'].filename.replace('\\','/').split('/')[-1]
        
        postFix = 'jpg'#filePath.split('.')[-1]
        hashedName = hashlib.md5('raw' + str(datetime.now(chinaTime))).hexdigest() + '.' + postFix
        imageFileName = storedDir+hashedName;
        fout = open(imageFileName, 'w')
        fout.write(data)
        fout.close()
        #ImageUtil.resize(imageFileName, 60, 'tb')
        ImageUtil.resize(imageFileName, 60, 'tb')
        #storedPhoto['screenURL'] = baseURL+hashedName
        remoteURL = baseURL + hashedName
        storedPhoto = None
        if photoID:
            storedPhoto = MongoUtil.fetchByID('StoredPhoto', ObjectId(photoID))
            oldRemoteURL = storedPhoto['remoteURL']
            storedPhoto['remoteURL'] = remoteURL
            if isOriginal and int(isOriginal) == 1:
                storedPhoto['originalURL'] = remoteURL
            elif not storedPhoto.get('originalURL'):
                storedPhoto['originalURL'] = oldRemoteURL
            MongoUtil.update('StoredPhoto',storedPhoto)
        else:
            storedPhoto = {'taskID':taskID, 'sequence':int(sequence), 'remoteURL':remoteURL, 'originalURL':remoteURL}
            MongoUtil.save('StoredPhoto', storedPhoto)
        
        #task = MongoUtil.fetchByID('PhotoTask', ObjectId(taskID))
        
        return simplejson.dumps(cleanStoredPhoto(storedPhoto))        

class AvatarHandler:
    def GET(self, cmd):
        web.debug('avatar command:%s' % cmd)
        return '{}'

    def POST(self, cmd):
        x = web.input(myfile={})
        personID = x.get('personID')
        isOriginal = x.get("isOriginal")
        #storedDir = '/home/ec2-user/root/www/static/'+userSession+'/'
        #storedDir = '/home/ec2-user/root/www/static/'+taskID+'/'
        if not personID:
            web.debug('quit for no personID')
            return '{}'
        storedDir = '/home/ec2-user/root/www/static/avatar/'
        if not os.path.exists(storedDir):
            storedDir = '%s/static/avatar/' % os.getcwd()  
        else:
            storedDir = '/home/ec2-user/root/www/static/avatar/'

        makeIfNone(storedDir)
        web.debug('final stored dir:%s, %s' % (storedDir,isOriginal))
        #baseURL = 'http://'+ web.ctx.env.get('HTTP_HOST') +'/static/avatar/'
        #filePath = x['myfile'].filename.replace('\\','/').split('/')[-1]
        #postFix = filePath.split('.')[-1]
        #hashedName = hashlib.md5(filePath + str(datetime.now(chinaTime))).hexdigest() + '.' + postFix
        imageFileName = "%s%s.jpg" % (storedDir, personID)
        fout = open(imageFileName, 'w')
        fout.write(x.myfile.file.read())
        fout.close()
        
        #remoteURL = "%s%s.jpg" % (baseURL, personID)
        #storedPhoto = None
        storedPerson = MongoUtil.fetchByID('P3DUser', ObjectId(personID))
        fullPath = '/static/avatar/%s.jpg' % personID
        if storedPerson:
            #oldRemoteURL = storedPhoto['remoteURL']
            storedPerson['avatar'] = fullPath
            MongoUtil.update('P3DUser',storedPerson)

        #task = MongoUtil.fetchByID('PhotoTask', ObjectId(taskID))
        
        return simplejson.dumps({"fullURL":fullPath})

class PhotoUploader:
    def GET(self):
        params = web.input();
        cmd = params.get('cmd')
        if cmd == 'del':
            photoID = params.photoID
            MongoUtil.remove('StoredPhoto', {'_id':ObjectId(photoID)})
            #Need to delete the uploaded photo too
        elif cmd == 'update':
            photoIDs = params.photoID.split(',')
            #sequences = params.sequence.split(',')
            for i in range(0, len(photoIDs)):
                photoID = photoIDs[i]
                #sequence = sequences[i]
                web.debug('photoID:'+photoID)
                MongoUtil.updateByConds('StoredPhoto', {'_id':ObjectId(photoID)}, {'sequence':i})
        return '{}'

    def POST(self):
        x = web.input(myfile={})
        taskID = x["taskID"]
        photoID = x.get("photoID")
        sequence = x.get("sequence")
        isOriginal = x.get("isOriginal")
        #storedDir = '/home/ec2-user/root/www/static/'+userSession+'/'
        #storedDir = '/home/ec2-user/root/www/static/'+taskID+'/'
        storedDir = '/home/ec2-user/root/www/static/'
        if not os.path.exists(storedDir):
            storedDir = '%s/static/%s/' % (os.getcwd(),taskID)  
        else:
            storedDir = '/home/ec2-user/root/www/static/'+taskID+'/'

        makeIfNone(storedDir)
        web.debug('final stored dir:%s, %s' % (storedDir,isOriginal))
        baseURL = 'http://'+ web.ctx.env.get('HTTP_HOST') +'/static/'+taskID+'/'
        filePath = x['myfile'].filename.replace('\\','/').split('/')[-1]
        postFix = filePath.split('.')[-1]
        hashedName = hashlib.md5(filePath + str(datetime.now(chinaTime))).hexdigest() + '.' + postFix
        imageFileName = storedDir+hashedName;
        fout = open(imageFileName, 'w')
        fout.write(x.myfile.file.read())
        fout.close()
        ImageUtil.resize(imageFileName, 80, 'tb')
        ImageUtil.resize(imageFileName, 180, 'cv')
        ImageUtil.resize(imageFileName, 640, 'nm')
        #storedPhoto['screenURL'] = baseURL+hashedName
        remoteURL = baseURL + hashedName
        storedPhoto = None
        if photoID:
            storedPhoto = MongoUtil.fetchByID('StoredPhoto', ObjectId(photoID))
            oldRemoteURL = storedPhoto['remoteURL']
            storedPhoto['remoteURL'] = remoteURL
            if isOriginal and int(isOriginal) == 1:
                storedPhoto['originalURL'] = remoteURL
            elif not storedPhoto.get('originalURL'):
                storedPhoto['originalURL'] = oldRemoteURL
            MongoUtil.update('StoredPhoto',storedPhoto)
        else:
            storedPhoto = {'taskID':taskID, 'sequence':int(sequence), 'remoteURL':remoteURL, 'originalURL':remoteURL}
            MongoUtil.save('StoredPhoto', storedPhoto)
        
        #task = MongoUtil.fetchByID('PhotoTask', ObjectId(taskID))
        
        return simplejson.dumps(cleanStoredPhoto(storedPhoto))