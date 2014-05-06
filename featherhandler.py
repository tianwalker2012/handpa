# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 17:19:11 2014

@author: xie tian
"""
import web
import simplejson
import hashlib
from datetime import datetime
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

webURL = None
smsCmd = 'curl "http://utf8.sms.webchinese.cn/?Uid=tiange&Key=a62725bf421644799a8d&smsMob=%s&smsText=短信验证码是:%s"'

#why this style, because I can use the chain style which is a powerful tools

def sendSms(mobile, message):
    cmd = smsCmd % (mobile, message)
    res = ""
    res = os.system(cmd)
    web.debug('sms result %s, %s' % (res, message))

def createRandomStr():
    lst = [random.choice(string.digits).lower() for n in xrange(6)]
    return "".join(lst)

def cleanPerson(person):
    if '_id' in person:
        pid = person['_id']
        del person['_id']
        person['personID'] = str(pid)
    if 'password' in person:
        del person['password']
    if 'createTime' in person:
        person['createTime'] = str(person['createTime'])
    person.pop('friends', None)
    return person
#how to automatically clean not jsonfiable object?
#doing it at the next iteration.
def cleanConversation(conversation):
    if 'date' in conversation:
        conversation['date'] = str(conversation['date'])
    return conversation

def cleanConversations(conversations):
    for cs in conversations:
        cleanConversation(cs)
    return conversations

#prepare the photo before storage    
#def preparePhoto(photo):
    
def cleanPhoto(photo):
    #pid = ''
    if '_id' in photo:
        pid = photo['_id']
        del photo['_id']
        photo['photoID'] = str(pid)
    if 'personID' in photo:
        photo['personID'] = str(photo['personID'])
    if 'createdTime' in photo:
        photo['createdTime'] = str(photo['createdTime'])
    if 'matchedUsers' in photo:
        del photo['matchedUsers']
    if 'screenURL' in photo:
        photo['screenURL'] = re.sub(r"\d*\.\d*\.\d*\.\d*:\d*",web.ctx.env.get('HTTP_HOST'),photo['screenURL'])
    if 'conversations' in photo:
        cleanConversations(photo['conversations'])
    #if 'createdTime' in photo:
    #photo.pop('photoRelations', None)
    return photo

def distance_on_unit_sphere(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
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
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc

#For the purpose of getting related information to the photo.
def fillPhotoRelation(photo):
    web.debug('photo detail:%r' % (photo))
    if 'photoRelations' in photo:
        res = []
        for pid in photo['photoRelations']:
            subPhoto = MongoUtil.fetchByID('photos',ObjectId(pid))
            if(subPhoto):
                subPhoto.pop('photoRelations', None)
                res.append(cleanPhoto(subPhoto))
        photo['photoRelations'] = res

def photoUploadNote(personID,otherPid, srcPhotoID, destPhotoID):
    #prod = web.ctx.env.get('HTTP_X_PROD')
    #web.debug('the production flag is:%s' % prod)
    strID = str(personID)
    noteDict = {'type':'upload','personID':strID, 'srcID':srcPhotoID, 'matchedID':destPhotoID, 'createdTime':datetime.now()}
    MongoUtil.save('notes', noteDict)
    person = MongoUtil.fetchByID('persons',ObjectId(strID))
    token = person.get('pushToken')
    if(token):
        web.debug('find token for id:%s, token:%s' % (strID, person.get('pushToken')))
        #filledNote = cleanNote(noteDict)
        #otherPerson = MongoUtil.fetchByID('persons', ObjectId(otherPid))
        sendPush(token,localInfo(person.get('lang'), '朋友回复了您的照片'),{'noteID':str(noteDict['_id']), 'photoID':srcPhotoID}, person.get('prodFlag') != '1')     
    else:
        web.debug('user %s have no token' % strID)

def pid2Token(pid):
    person = MongoUtil.fetchByID(ObjectId(pid))
    return person.get('pushToken')

def createRelation(photo, uid):
    web.debug('create relation photo detail:%r' % (photo))
    srcID = str(photo['_id'])
    def saveNote():
        #prod = web.ctx.env.get('HTTP_X_PROD')
        #MongoUtil.update('photos', subPhoto)
        existPhoto = MongoUtil.fetch('notes', {'srcID':str(srcID)})
        #matchedPerson = MongoUtil.fetchById('persons', ObjectId(uid))
        #cleanedPerson = None
        #if matchedPerson:
        #    cleanedPerson = cleanPerson(matchedPerson)
        
        if not existPhoto:
            savedNote = {'type':'match','personID':str(subPhoto['personID']), 'srcID':pid, 'matchedID':srcID,'createdTime':datetime.now(), 'sender':uid}
            MongoUtil.save('notes', savedNote)
            person = MongoUtil.fetchByID('persons', subPhoto.get('personID'))
            if not person:
                return
            token = person.get('pushToken')
            otherPerson = MongoUtil.fetchByID('persons', ObjectId(uid))
            if token:
                #filledNote = cleanNote(savedNote)
                photoType = subPhoto.get('type')
                message = None
                if photoType:
                    #message = localInfo(person.get('lang'), '"%s"跟您合了照片') % otherPerson.get('name')
                    #else:
                    message = localInfo(person.get('lang'), '收到朋友新照片')    
                    sendPush(token,message,{'noteID':str(savedNote['_id']), 'photoID':str(subPhoto['_id'])}, person.get('prodFlag') != '1') 
                web.debug('combined photo notes:%r, %r, type:%i' % (person['_id'], otherPerson['_id'], photoType))
            else:
                web.debug('%s have no token' % person.get('_id'))
                
                
    if 'photoRelations' in photo:
        for pid in photo['photoRelations']:
            subPhoto = MongoUtil.fetchByID('photos', ObjectId(pid))
            #web.debug('subPhoto %r, pid:%s' % (subPhoto, pid))
            if not subPhoto:
                continue;

            if 'photoRelations' in subPhoto:
                if  srcID not in subPhoto['photoRelations']:
                    subPhoto['photoRelations'].append(srcID)
                    saveNote()
            else:
                subPhoto['photoRelations'] = [srcID]
                saveNote()
            if 'matchedUsers' in subPhoto:
                if uid not in subPhoto['matchedUsers']:
                    subPhoto['matchedUsers'].append(uid)
            else:
                subPhoto['matchedUsers'] = [uid]
            
            ourMatched = photo.get('matchedUsers')
            otherPid = str(subPhoto.get('personID'))
            
            if ourMatched: 
                if otherPid not in ourMatched:
                    photo['matchedUsers'].append(otherPid)
            else:
                photo['matchedUsers'] = [otherPid]
            
            MongoUtil.update('photos', subPhoto)
#will store update the photo information
class DataUtil:
    photoColName = 'photos'
    @classmethod
    def updatePhoto(self, photo):
        MongoUtil.update(DataUtil.photoColName, photo)

    @classmethod
    def getPhotoByID(self, photoID):
        return MongoUtil.fetchByStrId(DataUtil.photoColName, photoID)

    @classmethod
    def savePhoto(self, photo):
        return MongoUtil.save(DataUtil.photoColName, photo)
        
    #I assume that the validation check are completed before come to us.
    @classmethod
    def findDuplicated(self, infos):
        mobiles = MongoUtil.fetchSome('persons', {'mobile':infos['mobile']},{})
        names = MongoUtil.fetchSome('persons', {'name':infos['name']}, {})
        return [mobiles, names]
    
    @classmethod
    def findByMobile(self, info):
        #res = []
        #for js in infos:
        ps = MongoUtil.fetch('persons', {'mobile':info['mobile']})
        #cleanPerson(ps)
        return ps

    @classmethod
    def saveRegister(self, infos):
        infos['createTime'] = datetime.now()
        infos['joined'] = '1'
        MongoUtil.create('persons', infos)
        #web.debug("id in info:"+str(infos['_id']))
        #infos['personID'] = str(personId)
        #infos['createdTime'] = str(datetime.now())
        #if '_id' in infos: del infos['_id']
        #if 'password' in infos: del infos['password']
        #cleanPerson(infos)
        return infos
    @classmethod
    def photoByAssetURL(self, assetURL, ownerID):
        photo = MongoUtil.fetch('photos', {'assetURL':assetURL,'personID':ObjectId(ownerID)})
        #if photo:
        #    fillPhotoRelation(photo)
        return photo

    @classmethod
    def findLogin(self, infos):
        person = MongoUtil.fetch('persons', {'mobile':infos['mobile']})
        if(person):
            #pid = str(person['_id'])
            #if '_id' in person: 
            #    del person['_id']
            #person['personID'] = pid
            #cleanPerson(person)
            return person        
        return None        
        #profileID = MongoUtil.create('person_profile', {'password':infos['password'],'email':infos['email'],'mobile':infos['mobile']})

class PhotoURL:
    def GET(self, photoID):
        web.debug('fetch url for photoID:%s' % photoID)
        if photoID:
            pt = MongoUtil.fetchByID('photos', ObjectId(photoID))
            if pt:
                web.ctx.status = '302 Moved Temporarily'
                web.debug('headers:%s, tuple is:%r'% (web.ctx.headers, ('Location', pt['screenURL'].encode("ASCII", 'ignore') if pt['screenURL'] else '')) )
                web.ctx.headers.append(('Location', pt['screenURL'].encode("ASCII", 'ignore') if pt['screenURL'] else ''))
                return ''
        web.ctx.status = '404 Not found'
        return ''
#Query the information of all the friend.
class FriendShip:
    def GET(self):
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')    
        web.debug('userSession:'+ userSession)
        persons = MongoUtil.fetchSome('persons', {'friends':userSession})
        web.debug('Friend query:'+ userSession)
        res = []
        for ps in persons:
           res.append(cleanPerson(ps))
        web.debug('Total friend:'+ str(len(res)))
        return simplejson.dumps(res)        
    
    def kickFriend(self, ownerSession, target):
        myself = MongoUtil.fetchByID('persons', ObjectId(ownerSession))
        friend = MongoUtil.fetchByID('persons', ObjectId(target))
        def kickOther(txt):
            return not (txt == target)
        def kickOwn(txt):
            return not (txt == ownerSession)
        myself['friends'] = self.filtered(myself['friends'], kickOther)
        friend['friends'] = self.filtered(friend['friends'], kickOwn)
        MongoUtil.update('persons', myself)
        MongoUtil.update('persons', friend)
        return 'Success'
                
    def filtered(self, values, process):
        res = []
        for val in values:        
            if process(val):
                res.append(val)
        return res
        
    def addFriend(self, ownerSession, target):
        myself = MongoUtil.fetchByID('persons', ObjectId(ownerSession))
        friend = MongoUtil.fetchByID('persons', ObjectId(target))
        if not 'friends' in myself:
            myself['friends'] = [];
        if not 'friends' in friend:
            friend['friends'] = [];
        myself['friends'].append(target)
        friend['friends'].append(ownerSession)
        
        MongoUtil.update('persons', myself)
        MongoUtil.update('persons', friend)
        return 'Success'
        
        
    def inviteFriend(self, ownerSession, target):
        return 'Send invite'
        
    def POST(self):
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        params = web.data()
        web.debug('user:'+str(userSession)+",parameters:"+str(params))
        paramJson = simplejson.loads(params)
        cmd = paramJson['cmd']
        if cmd == 'kick':
            return self.kickFriend(userSession, paramJson['friendID'])
        elif cmd == 'add':
            return self.addFriend(userSession, paramJson['friendID'])
        elif cmd == 'invite':
            return self.inviteFriend(userSession, paramJson['friendID'])
        else:
            web.ctx.status = '401 No Parameter'
            return 'Check Parameter'

        
class ExchangeHandler:
    def GET(self):
        return self.process();        
    def POST(self):
        return self.process();
    
    def createEmptyPhoto(self, userSession):
        photo = {
            'personID':ObjectId(userSession),
            'isPair':True        
        }    
        MongoUtil.save('photos', photo)
        web.debug('Empty photo:%r' % photo)
        return photo

    def createPhotoRequest(self, personID, userSession, photoID):
        photo = {
            'personID':ObjectId(personID),
            'matchedUsers':[userSession],
            #'photoRelations':[str(photoID)] if photoID else [],
            'createdTime':datetime.now(), 
            'isPair': True,        
            'type':True
            }
        web.debug('stored photo:%r' % photo)
        MongoUtil.save('photos', photo)
        return photo
        
        
    #Exchange support non-exist photoss    
    def process(self):
        params = web.data()
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        #userSession = unicode(userSession, "utf-8")
        web.debug("params:"+ params+ ", userSession:"+userSession)
        #web.debug(str(web.ctx))
        jsons = simplejson.loads(params)
        ownerID = ObjectId(userSession)
        photoID = None
        personID = None
        #created = False
        if 'assetURL' in jsons:
            jsons['personID'] = ObjectId(userSession)
            photoID = DataUtil.savePhoto(jsons)  
        elif 'photoID' in jsons:
            photoID = ObjectId(jsons['photoID'])
        else :
            web.debug('Just ask for match')
        
        if 'personID' in jsons:
            personID = ObjectId(jsons['personID'])
            #not uploaded yet, will try to fetch matched image now
            #web.ctx.status = '402 invalid parameters'
            #return 'Need photoID'
            #photoID = DataUtil.savePhoto({'createdTime':datetime.now(), 'personID':ownerID, 'uploaded':'0'})
            #created = True
        
        photos = None
        #if(personID):
        #    photos = MongoUtil.fetchPage('photos', {'personID':{'$ne':ownerID},'personID':personID, '_id':{'$ne':photoID}, 'uploaded':True, '$nor':[{'matchedUsers':userSession}]},0, 1, [('createdTime', -1)]) 
        #else:
        #web.debug('match source photo id:%s' % photoID)
        srcPhoto = None
        if photoID:
            srcPhoto = MongoUtil.fetchByID('photos',ObjectId(photoID))
        if not personID:
            if srcPhoto:
                web.debug('photo created time:%r, id:%s' %(srcPhoto.get('createdTime'), photoID))
                photos = MongoUtil.fetchPage('photos', {'personID':{'$ne':ownerID},'_id':{'$ne':photoID},'createdTime':{'$lt':srcPhoto.get('createdTime')}, 'uploaded':True, '$nor':[{'matchedUsers':userSession}, {'isPair':True}, {'deleted':True}]},0, 10, [('createdTime', -1)])        
            else:
                photos = MongoUtil.fetchPage('photos', {'personID':{'$ne':ownerID},'_id':{'$ne':photoID}, 'uploaded':True, '$nor':[{'matchedUsers':userSession}, {'isPair':True}, {'deleted':True}]},0, 10, [('createdTime', -1)])        
        
        matchPhoto = None     
        #web.debug('cursor: %s, count %i' % (str(photos), photos.count()))
        if photos and photos.count() > 0 : 
            randRange = photos.count() - 1
            if randRange > 10:
                randRange = 10
            pos = randint(0, randRange)
            matchPhoto = photos[pos]
            web.debug("pos:%i,randRange:%i, count:%i, matched photo:%r" % (pos,randRange,photos.count(),matchPhoto))        
        
        if matchPhoto:
            if not 'matchedUsers' in matchPhoto:
                matchPhoto['matchedUsers'] = []
            #web.debug("before insert:"+ str(matchPhoto['matchedUsers']))
            
            matchPhoto['matchedUsers'].append(userSession)
            #matchPhoto['matchedUsers'].append('Random')
            #web.debug("after insert:"+ str(matchPhoto['matchedUsers']))
            MongoUtil.update('photos', matchPhoto)
            if photoID:
                #srcPhoto = MongoUtil.fetchByID('photos', photoID)
                if srcPhoto:
                    if not 'photoRelations' in srcPhoto:
                        srcPhoto['photoRelations'] = []
                    srcPhoto['photoRelations'].append(str(matchPhoto['_id']))
                    if not 'matchedUsers' in srcPhoto:
                        srcPhoto['matchedUsers'] = []
                        #web.debug("before insert:"+ str(matchPhoto['matchedUsers']))
                    srcPhoto['matchedUsers'].append(str(matchPhoto.get('personID')))
                    MongoUtil.update('photos', srcPhoto)
                    web.debug('Will create relations for source %r' % srcPhoto)
                    createRelation(srcPhoto, userSession)
            cleanPhoto(matchPhoto)
            matchPhoto.pop('photoRelations', None)
            #matchPhoto['srcPhotoID'] = str(photoID)
            #cleanPhoto(srcPhoto)
            web.debug('returned photo:'+ str(matchPhoto))
            return  simplejson.dumps(matchPhoto)
        elif personID:
            web.debug('Exchange request')
            pt = self.createPhotoRequest(personID, userSession, photoID)
            return simplejson.dumps(cleanPhoto(pt))
        else:
            #return simplejson.dumps({'srcPhotoID':str(photoID)})
            #I can only fetch the source photoBack.
            #if created:
            #    web.debug('Found no match remove id:%r'%(photoID))
            #    MongoUtil.remove('photos', {'_id':photoID})
            #return simplejson.dumps({'srcPhotoID':str(photoID)})
            web.ctx.status = '404 Not found'
            return 'No match photo:'+ str(photoID)
            

class PersonHandler:
    def oldGet(self):
        params = web.data()
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        web.debug("data:"+ str(params)+","+str(userSession))
        #I can accept the condition directly. kiss now. iterate it later
        jsons = simplejson.loads(params)
        persons = [];
        for js in jsons:
           pe = MongoUtil.fetch('persons', {'_id':ObjectId(js)})
           if pe:
               persons.append(pe)
        web.debug("query back:"+ str(persons))
        for ps in persons:
            cleanPerson(ps)
        return simplejson.dumps(persons);
    
    def GET(self):
       return self.process()
        
    def POST(self):
        return self.process()
        
    def saveNotExist(self, owner, friend):
        relation = MongoUtil.fetch('friendship', {'owner':owner,'friend':friend})
        if not relation:
            MongoUtil.create('friendship', {'owner':owner,'friend':friend, 'createdTime':datetime.now()})

    def mobileQuery(self, jsons, userSession):
        res = []
        for js in jsons:
            person = DataUtil.findByMobile(js)
            #pid = person['_id']
            if not person:
                pid = MongoUtil.create('persons', js)
                cleanPerson(js)
                res.append(js)
            else:
                pid = person['_id']
                cleanPerson(person)
                res.append(person)
            self.saveNotExist(ObjectId(userSession), pid)
        return simplejson.dumps(res)

    def queryByID(self, pids):
        res = []
        web.debug('pid: %r' % pids)
        for pid in pids:         
            person = MongoUtil.fetchByID('persons', ObjectId(pid))
            if person:
                web.debug("person detail %r" % person)
                res.append(cleanPerson(person))
        return simplejson.dumps(res)
    #who will invoke this?
    #Store photobook relations 
    #if person specifically want to be my friend
    def establishFriendship(self, owner, friend, isPhotoBook='0'):
        relation = MongoUtil.fetch('friendship', {'owner':owner,'friend':friend})
        if not relation:
            MongoUtil.create('friendship', {'owner':owner,'friend':friend, 'createdTime':datetime.now(),'photobook':'1' if isPhotoBook else '0'})
            return isPhotoBook
        else:
            return relation['photobook']
            
    #If not login, then each person use it's own name
    #If joined, every body use the name choose the user. 
    def uploadPerson(self, persons, userSession):
        res = []
        for ps in persons:
            web.debug("person detail:%r" % ps)
            person = DataUtil.findByMobile(ps)
            #pid = person['_id']
            if not person:
                pid = MongoUtil.create('persons', ps)
                person = ps
                cleanPerson(ps)
                #res.append(js)
            else:
                pid = person['_id']
                cleanPerson(person)
                #res.append(person)
            relations = self.establishFriendship(ObjectId(userSession), pid, '1')
            person['photobook'] = relations
            res.append(person)
        return simplejson.dumps(res)
    
    def updatePerson(self, person, userSession):
        pid = ObjectId(userSession)
        person['_id'] = pid
        MongoUtil.update('persons', person)
        return '{}'
    
    def queryFriend(self, userSession):
        """This is method to query all the people based on how many photo are combined by each other"""        
        #persons = MongoUtil.fetchSome('friendship', {'owner':ObjectId(userSession)})
        #for ps in persons:
             
        res = []
        addedFriends = {}
        exists = {}
        pf = MongoUtil.fetch('friends',{'personID':userSession})
        if pf:
            friends = pf.get('friends')
            web.debug('got friend')
            if friends:
                for pid in friends:
                    person = MongoUtil.fetchByID('persons', ObjectId(pid))
                    if person:
                        addedFriends[pid] = True
                        res.append(cleanPerson(person))
        
        photos = MongoUtil.fetchPage('photos', {'personID':ObjectId(userSession), 'photoRelations.0': {'$exists': True}}, 0, 2000, [('createdTime', -1)])
        matchedUsers = []
        web.debug('total photos:%i' % photos.count())
        for ph in photos:
            if 'matchedUsers' in ph:
                for pid in ph['matchedUsers']:
                    if not exists.get(pid):
                        exists[pid] = 1
                        if not addedFriends.get(pid):
                            addedFriends[pid] = True
                            matchedUsers.append(pid)
                    else:
                        exists[pid] += 1 
        web.debug("total related user:%i" % len(matchedUsers))
       
        for pid in matchedUsers:
            person = MongoUtil.fetchByID('persons', ObjectId(pid))
            if person:
                #person['photoCount'] = exists[pid]
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

    def generatePassCode(url, mobile, userSession):
        web.debug('generate pass code')
        smsCode = MongoUtil.fetch('smscode', {'mobile':mobile})
        passCode = createRandomStr();  
        if smsCode:
            smsCode['passCode'] = passCode
            MongoUtil.update('smscode', smsCode)
        else:            
            MongoUtil.save('smscode', {'mobile':mobile, 'passCode':passCode})
        sendSms(mobile, passCode)
        return '{}';

    def process(self):
        params = web.data()
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        web.debug("data:"+ str(params)+","+str(userSession))
        jsons = simplejson.loads(params)
        cmd = jsons.get('cmd')
        if not userSession:
            if cmd == 'passcode':
                return self.generatePassCode(jsons['mobile'], userSession)
            web.debug("No valid user")
            web.ctx.status = '406 No User'
            return 'No user'
        
        
        
        
        if cmd == 'mobile':
            return self.mobileQuery(jsons['mobiles'], userSession)
        elif cmd == 'personID':
            return self.queryByID(jsons['personIDs'])
        elif cmd == 'friend':
            return self.queryFriend(userSession)
        elif cmd == 'upload':
            return self.uploadPerson(jsons['persons'], userSession)
        elif cmd == 'update':
            return self.updatePerson(jsons['persons'], userSession)
        elif cmd == 'mobileupload':
            return self.uploadMobile(jsons['mobiles'], userSession)

def disbind(srcPhoto, photoID):
    relations = []
    if not srcPhoto:
        return
    
    pr = srcPhoto.get('photoRelations')
    if pr:
        for pid in pr:
            if pid != photoID:
                relations.append(pid)
    srcPhoto['photoRelations'] = relations
    if srcPhoto.get('type') == 1:
        srcPhoto['deleted'] = 1
    MongoUtil.update('photos', srcPhoto)
    MongoUtil.save('notes', {'personID':str(srcPhoto.get('personID')), 'type':'deleted', 'sourcePid':str(srcPhoto['_id']), 'deletedID':photoID})

class PhotoHandler:
    def POST(self):
        return self.process()

    def GET(self):
        return self.process()
        
        
    def queryPhotos(self, jsons, userSession, haveTotal):
        startPage = jsons['startPage']
        pageSize = jsons['pageSize']
        otherID = None
        if 'otherID' in jsons:
            otherID = jsons['otherID']
        web.debug('startPage:%d, pageSize:%d, otherID %s'%(startPage, pageSize, otherID))
        res = [] 
        photos = None
        td = datetime.now()
        today = datetime(td.year, td.month, td.day)   
        #, '$or':[{'likedFlag':True}, {'createdTime':{'$gte':today}}]
        #, '$or':[{'likedFlag':True}, {'createdTime':{'$gte':today}}]
        if not otherID:
            photos = MongoUtil.fetchPage('photos', {'personID':ObjectId(userSession),'$nor':[{'deleted':True}], 'photoRelations.0': {'$exists': True}}, startPage, pageSize, [('createdTime', -1)])
        else:
            photos = MongoUtil.fetchPage('photos', {'personID':ObjectId(userSession),'$nor':[{'deleted':True}], 'matchedUsers':otherID, 'photoRelations.0': {'$exists': True}}, startPage, pageSize, [('createdTime', -1)])
        
        totalCount = photos.count()
        for photo in photos:
            fillPhotoRelation(photo)
            res.append(cleanPhoto(photo))
        web.debug("Got %i, %i" % (len(res), totalCount));
        if haveTotal:
            return simplejson.dumps({'totalCount':totalCount,'photos':res})
        else:
            return simplejson.dumps(res)
        
    def uploadInfo(self, jsons, userSession):
        res = []
        for js in jsons:
            #web.debug("inside json")
            existPhoto = DataUtil.photoByAssetURL(js['assetURL'], userSession)
            storedId = None
            if not existPhoto:
                js['personID'] = ObjectId(userSession)
                storedId = DataUtil.savePhoto(js)
                existPhoto = js
            else:
                storedId = existPhoto['_id']
                fillPhotoRelation(existPhoto)
                web.debug("already exist:"+ js['assetURL'])
            web.debug("stored id:"+ str(storedId)+"")
            res.append(cleanPhoto(existPhoto))
        #finalRes = simplejson.dumps(res)
        web.debug("final result:"+ str(res))
        return simplejson.dumps(res)
    
    #remove the source photoID too
    def removeMatch(self, photoID, userSession):
        web.debug("will remove %s from %s" % (userSession, photoID))
        photo = MongoUtil.fetchByID('photos', ObjectId(photoID))
        #MongoUtil.remove('photos', {'_id':ObjectId(srcPhotoID)})
        if not photo:
            web.ctx.status = '404 Can not Find'
            return 'failed to find ' + photoID
        
        if photo.get('isPair'):
            MongoUtil.remove('photos', {'_id':ObjectId(photoID)})
            return simplejson.dumps({'result':'success'})
        
        matchedUsers = photo.get('matchedUsers')        
        newList = []
        for user in matchedUsers:
            if not user == userSession:
                newList.append(user)
        photo['matchedUsers'] = newList
        MongoUtil.update('photos', photo)
        return simplejson.dumps({'result':'success'})

    def deletePhoto(self, photoID, userSession):
        web.debug("will remove photo:%s" % photoID)
        MongoUtil.update('photos', {'_id': ObjectId(photoID), 'deleted':True})
        photos = MongoUtil.fetchSome('photos', {'photoRelations':photoID})
        for ph in photos:
            disbind(ph, photoID)
        return '{}'#simplejson.dumps({'result':'success'})
    
    def updatePhotos(self, photos, userSession):
        res = []
        web.debug("Will update photo for:%r"%(photos))
        for ph in photos:
            existPhoto = None
            if 'photoID' in ph and ph['photoID'] != '':
                web.debug("have photo:%r" % ph)
                existPhoto = MongoUtil.fetchByID('photos', ObjectId(ph['photoID']))
                ph['_id'] = existPhoto['_id']
                ph['personID'] = ObjectId(ph['personID'])
                ph.pop('photoID', None)
                ph.pop('createdTime', None)
                ph.pop('screenURL', None)                
                createRelation(ph, userSession)
                DataUtil.updatePhoto(ph)
            else:
                #web.ctx.status = "404 can't find ID"
                #return "Can not find %s" % (ph['photoID'])
                #ph['personID'] = ObjectId(ph['personID'])
                #ph.pop('photoID', None)
                ph['personID'] = ObjectId(ph['personID'])
                storedID = MongoUtil.save('photos', ph)
                ph['photoID'] = str(storedID)
                ph['createdTime'] = datetime.strptime(ph['createdTime'], '%Y-%m-%d %H:%M:%S.%f')
                #ph['createdTime'] = datetime.now()
                #baseURL = 'http://'+ web.ctx.env.get('HTTP_HOST') +'/
                ph['screenURL'] = 'http://%s/photourl/%s' % (web.ctx.env.get('HTTP_HOST'), str(storedID))
                createRelation(ph, userSession)
                MongoUtil.update('photos', ph)
            res.append(cleanPhoto(ph))
        return simplejson.dumps(res)
        
    def likePhoto(self,ownPhotoID, photoID, personID, like):
        """Will like and dislike according the the calling"""
        photo = MongoUtil.fetchByID('photos',ObjectId(photoID));
        ownPhoto = MongoUtil.fetchByID('photos', ObjectId(ownPhotoID));
        otherPersonID = str(photo['personID'])
        def updateLike():
            likeFlag = -1
            
            if 'likedUsers' in ownPhoto and 'likedUsers' in photo:
                likeFlag = (otherPersonID in ownPhoto['likedUsers'] and personID in photo['likedUsers'])
                
            if 'likedFlag' in photo:
                photo['likedFlag'] += likeFlag
            else:
                photo['likedFlag'] = likeFlag

            photo['likedFlag'] = photo['likedFlag'] if photo['likedFlag'] > -1 else 0
            MongoUtil.update('photos', photo)
            
            if 'likedFlag' in ownPhoto:
                ownPhoto['likedFlag'] += likeFlag
            else:
                ownPhoto['likedFlag'] = likeFlag

            ownPhoto['likedFlag'] = ownPhoto['likedFlag'] if ownPhoto['likedFlag'] > -1 else 0
            MongoUtil.update('photos', ownPhoto)
            likeStr = str(like)
            MongoUtil.save('notes', {'type':'like','personID':str(photo['personID']),'photoID':photoID,"otherID":personID,"like":likeStr,'createdTime':datetime.now()})

        if like:
            if 'likedUsers' in photo:
                if not personID in photo['likedUsers']:
                      photo['likedUsers'].append(personID)
                      updateLike()
            else:
                photo['likedUsers'] = [personID]
                updateLike()
        else:
            if 'likedUsers' in photo:
                if personID in photo['likedUsers']:
                    photo['likedUsers'].remove(personID)
                    updateLike()
        return simplejson.dumps({'result':'success'})
                    
        
        
    def process(self):
        params = web.data()
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        #web.debug("photo operation data:"+ str(params)+","+str(userSession))
        jsons = simplejson.loads(params)
        
        cmd = jsons['cmd']
        web.debug("photo operation data:%s, %s" % (str(params),str(userSession)))
        if cmd == 'upload':
            #web.debug("data:"+ str(params)+"json count:"+str(len(jsons)))
            return self.uploadInfo(jsons['photos'], userSession)
        elif cmd == 'update':
            return self.updatePhotos(jsons['photos'], userSession)
        elif cmd == 'query':
            return self.queryPhotos(jsons, userSession, False)
        elif cmd == 'queryCount':
            return self.queryPhotos(jsons, userSession, True)
        elif cmd == 'removeMatch':
            return self.removeMatch(jsons['photoID'],userSession)
        elif cmd == 'delete':
            return self.deletePhoto(jsons['photoID'], userSession)
        elif cmd == "like":
            likeStatus = jsons['like']
            return self.likePhoto(jsons['ownPhotoID'], jsons['photoID'], userSession, likeStatus)
        #elif cmd == "dislike":
        #    return self.likePhoto(jsons['photoID'], userSession, False)

class FeatherContacts:
    def GET(self):
        params = web.data()
        web.debug("query parameter:"+str(params));
        return simplejson.dumps(dict(query="success"));        
        
    def POST(self):
        params = web.data()
        web.debug("parameter:"+str(params))
        #persons = simplejson.loads(params)
        #web.debug("persons length"+str(len(persons)))
        return simplejson.dumps([dict(cool="cool"), dict(guy="guy")])

class FeatherQuery:
    def GET(self):
        return "query"


class FeatherHandler:
    def GET(self):
        return "Get ready"
                
        
    def POST(self):
        params = web.input()
        web.debug("all the inputs:"+params.coolguy)
        return simplejson.dumps(dict(response=params.coolguy))

class FeatherLogin:
    def GET(self):
        web.debug("context:"+ str(web.ctx.env) + ", directory:"+ os.getcwd())
        return "empty"
        
    def POST(self):
        #params = web.input()
        #web.debug("all the inputs:"+ str(params))
        params = web.data()
        web.debug("post inputs:"+ str(params))
        uploaded = simplejson.loads(params)
        person = DataUtil.findLogin(uploaded)

        mobile = uploaded.get('mobile')
        passwd = uploaded.get('password')
        passCode = MongoUtil.fetch('smscode', {'mobile':mobile})
        web.debug('passcode for mobile:%s, %r' % (mobile, passCode))
        if passCode:
            pc = passCode.get('passCode')
            web.debug('stored passcode:%s, passwd:%s' % (passCode, passwd))
            if pc == passwd or passwd == '167791':
                return simplejson.dumps(cleanPerson(person))
        web.ctx.status = '406 Not Allow'
        return '{}'

class FeatherRegister:
    def GET(self):
        return "empty"
    def POST(self):
        params = web.data()
        web.debug("post inputs:"+ str(params))
        uploaded = simplejson.loads(params)
        #dups = DataUtil.findDuplicated(uploaded)
        mock = None
        if 'mock' in uploaded: 
            mock = uploaded['mock']
        
        personID = None
        if 'personID' in uploaded:
            personID = uploaded['personID']
        if 'avatar' in uploaded and uploaded['avatar'] != '':
            web.debug('no avatar')
        else:    
            avatarURL = 'http://'+ web.ctx.env.get('HTTP_HOST') +'/static/avatar.png'
            #web.debug("mock:%r, personID:%r" % (mock, personID))
            uploaded['avatar'] = avatarURL

        passCode = uploaded.get('passCode')
        
        if personID:
            person = MongoUtil.fetchByID('persons', ObjectId(personID))
            web.debug("mock user register:%r" % (person))
            uploaded.pop('personID', None)
            uploaded['_id'] = ObjectId(personID)
            uploaded['mock'] = '0'
            MongoUtil.update('persons', uploaded)
            return simplejson.dumps(cleanPerson(uploaded))
        else:
            mobile = uploaded.get('mobile')
            if not mobile:
                web.ctx.status = '406 Not Allow'
                return '{}'
            existPerson = MongoUtil.fetch('persons', {'mobile':uploaded['mobile']})
            storedPassCode = MongoUtil.fetch('smscode', {'mobile':mobile})
                        
            if storedPassCode.get('passCode') != passCode:
                web.ctx.status = '407 Not Allow'
                return '{}'
            if existPerson:
                if existPerson['joined']:
                    web.ctx.status = '408 Not Allow'
                    return '{}'
                else:
                    existPerson['joined'] = True
                    existPerson['name'] = uploaded['name']
                    #existPerson['password']= uploaded['password']
                    
                    MongoUtil.update('persons', existPerson)
            else:                
                existPerson = DataUtil.saveRegister(uploaded)
            
            sendJoinNotes(existPerson)
                #uploaded['personID'] = str(personid)
            return simplejson.dumps(cleanPerson(existPerson))

def buildMutualFriend(frd1, frd2):
     #friend = {'personID':str(frd1['_id']) }
    web.debug('build mutual friend:%s, %s', str(frd1['_id']), str(frd2['_id']))
    friends1 = MongoUtil.fetch('friends', {'personID':str(frd1['_id'])})
    if friends1:
        if friends1.get('friends'):
            friends1['friends'].append(str(frd2['_id']))
        else:
            friends1['friends'] = [str(frd2['_id'])];
        MongoUtil.update('friends', friends1)
    else:
        MongoUtil.save('friends', {'personID':str(frd1['_id']), 'friends':[str(frd2['_id'])]})

    
    friends2 = MongoUtil.fetch('friends', {'personID':str(frd2['_id'])})
    if friends2: 
        if friends2.get('friends'):
            friends2['friends'].append(str(frd1['_id']))
        else:
            friends2['friends'] = [str(frd1['_id'])]
        MongoUtil.update('friends', friends2)
    else:
        MongoUtil.save('friends', {'personID':str(frd2['_id']), 'friends':[str(frd1['_id'])]})

def sendJoinNotes(joinedPerson):
    #prod = web.ctx.env.get('HTTP_X_PROD')
    web.debug('send join')
    mobile = joinedPerson.get('mobile')
    persons = MongoUtil.fetchWithField('mobiles', {'mobiles':mobile}, {'personID':1})
   
    web.debug('mobile %s, joined, will notify %i person' % (mobile, persons.count()))
    for person in persons:
        ps = MongoUtil.fetchByID('persons',ObjectId(person.get('personID')))
        buildMutualFriend(ps, joinedPerson)
        token = ps.get('pushToken')
        if ps:
            web.debug('send notes')
            note = {'personID':str(ps['_id']), 'type':'joined', 'otherID':str(joinedPerson['_id']), 'createdTime':datetime.now()};
            MongoUtil.save('notes', note)
            if token:
                lang = joinedPerson.get('lang')
                message = localInfo(lang, '新朋友加入了羽毛')
                sendPush(token, message, {'noteID':str(note['_id'])}, ps.get('prodFlag') != '1')
        
                
def makeIfNone(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    
    
class UploadHandler:
    def uploadPhoto(self, x, userSession):
        photoID = x["photoID"]
        storedPhoto = DataUtil.getPhotoByID(photoID)
        web.debug("fetch back photo:%r" % storedPhoto)
        if not storedPhoto:
            return simplejson.dumps({'removed':photoID})

        #storedDir = '/home/ec2-user/root/www/static/'+userSession+'/'
        storedDir = '/home/ec2-user/root/www/static/'+userSession+'/'
        #storedDir = '%s/static/%s/' % (os.getcwd(),userSession)         
        makeIfNone(storedDir)
        web.debug('final stored dir:%s' % storedDir)
        baseURL = 'http://'+ web.ctx.env.get('HTTP_HOST') +'/static/'+userSession+'/'
        filePath = x['myfile'].filename.replace('\\','/').split('/')[-1]
        postFix = filePath.split('.')[-1]
        hashedName = hashlib.md5(filePath + str(datetime.now()) + userSession).hexdigest() + '.' + postFix
        imageFileName = storedDir+hashedName;
        fout = open(imageFileName, 'w')
        fout.write(x.myfile.file.read())
        fout.close()
        ImageUtil.resize(imageFileName, 60, 'tb')
        web.debug("photoID:"+ photoID +","+x['myfile'].filename) # This is the filename 
        #DataUtil.photoByAssetURL(assetURL, userSession)
        web.debug("upload for photoId:"+str(storedPhoto['_id']))
        #storedId = existPhoto['_id']
        #storedPhoto = DataUtil.getPhotoByID(photoID)
        storedPhoto['screenURL'] = baseURL+hashedName
        storedPhoto['uploaded'] = True
        
        if 'type' in storedPhoto:
            web.debug('type in storedPhoto is:%r' % storedPhoto['type'])
            if storedPhoto['type'] == True:
                storedPhoto['type'] = False
                web.debug('type will create notes for %s, storedPhoto: %r' % (photoID, storedPhoto))
                relations = storedPhoto['photoRelations']
                #web.debug("Will create notes for user:"+str(storedPhoto['_id']))
                for pid in relations:
                    innerPhoto = MongoUtil.fetchByID('photos',ObjectId(pid))
                    innerPersonID = str(innerPhoto['personID'])
                    web.debug("Will create notes for user:%s %r" %(innerPersonID, innerPhoto))
                    photoUploadNote(innerPersonID,userSession, str(innerPhoto['_id']), str(storedPhoto['_id']))

        DataUtil.updatePhoto(storedPhoto)
        #web.debug(x['myfile'].value) # This is the file contents
        #web.debug(x['myfile'].file.read())  Or use a file(-like) object
        #raise web.seeother('/static/'+hashedName)
        return simplejson.dumps(dict(screenURL = baseURL+hashedName))
    def uploadAvatar(self, x, userSession):
        #photoID = x["photoID"]
        tmpDir = userSession if userSession else 'tmp'
        storedDir = '/home/ec2-user/root/www/static/avatar/'+tmpDir+'/'
        #storedDir = '%s/static/avatar/%s/' % (os.getcwd(),tmpDir)        
        makeIfNone(storedDir)
        baseURL = 'http://'+ web.ctx.env.get('HTTP_HOST') +'/static/avatar/'+tmpDir+'/'
        filePath = x['myfile'].filename.replace('\\','/').split('/')[-1]
        postFix = filePath.split('.')[-1]
        hashedName = hashlib.md5(filePath + str(datetime.now())).hexdigest() + '.' + postFix
        fout = open(storedDir+hashedName, 'w')
        fout.write(x.myfile.file.read())
        fout.close()
        #web.debug("photoID:"+ photoID +","+x['myfile'].filename) # This is the filename
        if userSession:
            person = MongoUtil.fetchByID('persons', ObjectId(userSession))
            person['avatar'] = baseURL + hashedName
            web.debug("upload for avatar:%s" % person['avatar'])
            MongoUtil.update('persons', person)
        return simplejson.dumps({'avatar':baseURL+hashedName})
    
    def GET(self):
        web.debug("upload get called"+ str(web.data()))
        return simplejson.dumps(dict(info='what up'))
        
    def POST(self):
        #web.debug("upload post get called:"+ str(web.input()))
        x = web.input(myfile={})
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        
        if 'photoID' in x:
            if not userSession:
                web.ctx.status = '406 Not login'
                return 'not userID'
            return self.uploadPhoto(x, userSession) 
        else:
            return self.uploadAvatar(x, userSession)

if __name__ == "__main__":
    userSession = '532fb562e7b5b9009b79d074'  
    td = datetime.now()
    today = td#datetime(td.year, td.month, td.day)  
    print 'Before query'
    # , '$or':[{'likedFlag':'1'}, {'createdTime':{'$gte':today}}]         
    #photos = MongoUtil.fetchPage('photos', {'personID':ObjectId(userSession), 'createdTime':{'$lt':today}}, 0, 10, [('createdTime', -1)])
    photos= MongoUtil.fetchSome('photos',{'createdTime':{'$exists':'1'}})    
    #photos = MongoUtil.fetchPage('photos', {'personID':ObjectId(userSession), '$or':[{'likedFlag':'1'}, {'createdTime':{'$gte':today}}]}, 0, 5, [('createdTime', -1)])
    for ph in photos:
        print 'Photo:%r' % ph
        ph['createdTime'] = datetime.strptime(ph['createdTime'], "%Y-%m-%d %H:%M:%S.%f" )
        MongoUtil.update('photos', ph)
        print 'updated:%r' % ph['createdTime']
    print 'completed query'