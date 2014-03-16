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
import re
import os
import math
webURL = None
#why this style, because I can use the chain style which is a powerful tools
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
            subPhoto.pop('photoRelations', None)
            res.append(cleanPhoto(subPhoto))
        photo['photoRelations'] = res

        
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
        person = MongoUtil.fetch('persons', {'mobile':infos['mobile'], 'password':infos['password']})
        if(person):
            #pid = str(person['_id'])
            #if '_id' in person: 
            #    del person['_id']
            #person['personID'] = pid
            #cleanPerson(person)
            return person        
        return None        
        #profileID = MongoUtil.create('person_profile', {'password':infos['password'],'email':infos['email'],'mobile':infos['mobile']})

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
        
        elif 'personID' in jsons:
            personID = ObjectId(jsons['personID']) 
        else :
            web.debug('Just ask for match')
            #not uploaded yet, will try to fetch matched image now
            #web.ctx.status = '402 invalid parameters'
            #return 'Need photoID'
            #photoID = DataUtil.savePhoto({'createdTime':datetime.now(), 'personID':ownerID, 'uploaded':'0'})
            #created = True
        
        photos = None
        if(personID):
            photos = MongoUtil.fetchPage('photos', {'personID':{'$ne':ownerID},'personID':personID, '_id':{'$ne':photoID}, 'uploaded':'1', '$nor':[{'matchedUsers':userSession}]},0, 1, [('createdTime', -1)]) 
        else:
            photos = MongoUtil.fetchPage('photos', {'personID':{'$ne':ownerID},'_id':{'$ne':photoID}, 'uploaded':'1', '$nor':[{'matchedUsers':userSession}]},0, 1, [('createdTime', -1)])        
        
        matchPhoto = None     
        web.debug('cursor:'+ str(photos))
        if photos.count() > 0 : matchPhoto = photos[0]
        web.debug("matched photo:"+ str(matchPhoto))        
        srcPhoto = MongoUtil.fetchByID('photos', photoID)
        if matchPhoto:
            if not 'matchedUsers' in matchPhoto:
                matchPhoto['matchedUsers'] = []
            web.debug("before insert:"+ str(matchPhoto['matchedUsers']))
            
            matchPhoto['matchedUsers'].append(userSession)
            #matchPhoto['matchedUsers'].append('Random')
            web.debug("after insert:"+ str(matchPhoto['matchedUsers']))
            MongoUtil.update('photos', matchPhoto)
            if srcPhoto:
                if not 'photoRelations' in srcPhoto:
                    srcPhoto['photoRelations'] = []
                srcPhoto['photoRelations'].append(matchPhoto['_id'])
                MongoUtil.update('photos', srcPhoto)
            cleanPhoto(matchPhoto)
            matchPhoto.pop('photoRelations', None)
            #matchPhoto['srcPhotoID'] = str(photoID)
            #cleanPhoto(srcPhoto)
            web.debug('returned photo:'+ str(matchPhoto))
            return  simplejson.dumps(matchPhoto)
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
        
    def process(self):
        params = web.data()
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        if not userSession:
            web.debug("No valid user")
            web.ctx.status = '406 No User'
            return 'No user'
        
        web.debug("data:"+ str(params)+","+str(userSession))
        jsons = simplejson.loads(params)
        
        cmd = jsons['cmd']
        if cmd == 'mobile':
            return self.mobileQuery(jsons['mobiles'], userSession)
        elif cmd == 'personID':
            return self.queryByID(jsons['personIDs'])
        elif cmd == 'upload':
            return self.uploadPerson(jsons['persons'], userSession)
            
class PhotoHandler:
    def POST(self):
        return self.process()

    def GET(self):
        return self.process()
        
        
    def queryPhotos(self, jsons, userSession):
        startPage = jsons['startPage']
        pageSize = jsons['pageSize']
        otherID = None
        if 'otherID' in jsons:
            otherID = jsons['otherID']
        web.debug('startPage:%d, pageSize:%d, otherID %s'%(startPage, pageSize, otherID))
        res = [] 
        photos = None
        if not otherID:
            photos = MongoUtil.fetchPage('photos', {'personID':ObjectId(userSession)}, startPage, pageSize, [('createdTime', -1)])
        else:
            photos = MongoUtil.fetchPage('photos', {'personID':ObjectId(userSession), 'relationUsers':otherID}, startPage, pageSize, [('createdTime', -1)])
        
        for photo in photos:
            fillPhotoRelation(photo)
            res.append(cleanPhoto(photo))
        web.debug("Got "+ str(len(res)) + " for "+ str(res));
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
        matchedUsers = photo['matchedUsers']
        newList = []
        for user in matchedUsers:
            if not user == userSession:
                newList.append(user)
        photo['matchedUsers'] = newList
        MongoUtil.update('photos', photo)
        return simplejson.dumps({'result':'success'})

    def deletePhoto(self, photoID, userSession):
        web.debug("will remove photo:%s" % photoID)
        MongoUtil.remove('photos', {'_id': ObjectId(photoID)})
        return simplejson.dumps({'result':'success'})
    
    def updatePhotos(self, photos, userSession):
        res = []
        web.debug("Will update photo for:%r"%(photos))
        for ph in photos:
            existPhoto = None
            if 'photoID' in ph and ph['photoID'] != '':
                web.debug("have photoID:%r url:%r" % (ph['photoID'], ph['assetURL']))
                existPhoto = MongoUtil.fetchByID('photos', ObjectId(ph['photoID']))
                ph['_id'] = existPhoto['_id']
                ph['personID'] = ObjectId(ph['personID'])
                ph.pop('photoID', None)
                DataUtil.updatePhoto(ph)
            else:
                #web.ctx.status = "404 can't find ID"
                #return "Can not find %s" % (ph['photoID'])
                #ph['personID'] = ObjectId(ph['personID'])
                #ph.pop('photoID', None)
                ph['personID'] = ObjectId(ph['personID'])
                storedID = MongoUtil.save('photos', ph)
                ph['photoID'] = str(storedID)
            res.append(cleanPhoto(ph))
        return simplejson.dumps(res)
    def likePhoto(photoID, personID, like):
        photo = MongoUtil.fetchByID(ObjectId(photoID));
        
                    
        
        
    def process(self):
        params = web.data()
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        web.debug("photo operation data:"+ str(params)+","+str(userSession))
        jsons = simplejson.loads(params)
        
        cmd = jsons['cmd']
        if cmd == 'upload':
            #web.debug("data:"+ str(params)+"json count:"+str(len(jsons)))
            return self.uploadInfo(jsons['photos'], userSession)
        elif cmd == 'update':
            return self.updatePhotos(jsons['photos'], userSession)
        elif cmd == 'query':
            return self.queryPhotos(jsons, userSession)
        elif cmd == 'removeMatch':
            return self.removeMatch(jsons['photoID'],userSession)
        elif cmd == 'delete':
            return self.deletePhoto(jsons['photoID'], userSession)
        elif cmd == "like":
            return self.likePhoto(jsons['photoID'], userSession, True)
        elif cmd == "dislike":
            return self.likePhoto(jsons['photoID'], userSession, False)

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
        return simplejson.dumps(cleanPerson(person))

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
            web.debug("mock:%r, personID:%r" % (mock, personID))
            uploaded['avatar'] = avatarURL
        
        if personID:
            person = MongoUtil.fetchByID('persons', ObjectId(personID))
            web.debug("mock user register:%r" % (person))
            uploaded.pop('personID', None)
            uploaded['_id'] = ObjectId(personID)
            uploaded['mock'] = '0'
            MongoUtil.update('persons', uploaded)
            return simplejson.dumps(cleanPerson(uploaded))
        else:
            person = DataUtil.saveRegister(uploaded)
            #uploaded['personID'] = str(personid)
            return simplejson.dumps(cleanPerson(person))

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

        storedDir = os.getcwd()+'/static/'+userSession+'/'
        makeIfNone(storedDir)
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
        storedPhoto['uploaded'] = '1'
        DataUtil.updatePhoto(storedPhoto)
        #web.debug(x['myfile'].value) # This is the file contents
        #web.debug(x['myfile'].file.read())  Or use a file(-like) object
        #raise web.seeother('/static/'+hashedName)
        return simplejson.dumps(dict(screenURL = baseURL+hashedName))
    def uploadAvatar(self, x, userSession):
        #photoID = x["photoID"]
        tmpDir = userSession if userSession else 'tmp'
        storedDir = os.getcwd()+'/static/avatar/'+tmpDir+'/'
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