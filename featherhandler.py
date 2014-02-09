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
    def saveRegister(self, infos):
        personId = MongoUtil.create('persons', infos)
        web.debug("id in info:"+str(infos['_id']))
        infos['personID'] = str(personId)
        infos['createdTime'] = str(datetime.now())
        if '_id' in infos: del infos['_id']
        if 'password' in infos: del infos['password']
        return infos
        
    @classmethod
    def findLogin(self, infos):
        person = MongoUtil.fetch('persons', {'mobile':infos['mobile'], 'password':infos['password']})
        if(person):
            pid = str(person['_id'])
            if '_id' in person: 
                del person['_id']
            person['personID'] = pid
            return person        
        return None        
        #profileID = MongoUtil.create('person_profile', {'password':infos['password'],'email':infos['email'],'mobile':infos['mobile']})
class PhotoHandler:
    def POST(self):
        return self.process()

    def GET(self):
        return self.process()
        
    def process(self):
        params = web.data()
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        web.debug("data:"+ str(params)+","+str(userSession))
        jsons = simplejson.loads(params)
        web.debug("data:"+ str(params)+"json count:"+str(len(jsons)))
        res = []
        for js in jsons:
            #web.debug("inside json")
            storedId = DataUtil.savePhoto(js)
            web.debug("stored id:"+ str(storedId))
            res.append(dict(photoID=str(storedId)))
        #finalRes = simplejson.dumps(res)
        #web.debug("final result:"+ finalRes)
        return simplejson.dumps(res)

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
        return "empty"
        
    def POST(self):
        #params = web.input()
        #web.debug("all the inputs:"+ str(params))
        params = web.data()
        web.debug("post inputs:"+ str(params))
        uploaded = simplejson.loads(params)
        person = DataUtil.findLogin(uploaded)
        return simplejson.dumps(person)

class FeatherRegister:
    def GET(self):
        return "empty"
    def POST(self):
        params = web.data()
        web.debug("post inputs:"+ str(params))
        uploaded = simplejson.loads(params)
        #dups = DataUtil.findDuplicated(uploaded)
        DataUtil.saveRegister(uploaded)
        #uploaded['personID'] = str(personid)
        return simplejson.dumps(uploaded)

class UploadHandler:
    def GET(self):
        web.debug("upload get called"+ str(web.data()))
        return simplejson.dumps(dict(info='what up'))
        
    def POST(self):
        #web.debug("upload post get called:"+ str(web.input()))
        x = web.input(myfile={})
        photoID = x["photoID"]
        storedDir = '/Users/apple/Documents/handpa/static/'
        baseURL = 'http://192.168.1.103:8080/static/'
        filePath = x['myfile'].filename.replace('\\','/').split('/')[-1]
        postFix = filePath.split('.')[-1]
        hashedName = hashlib.md5(filePath + str(datetime.now())).hexdigest() + '.' + postFix
        fout = open(storedDir+hashedName, 'w')
        fout.write(x.myfile.file.read())
        fout.close()
        web.debug(x['myfile'].filename) # This is the filename
        web.debug("personid:"+photoID)
        storedPhoto = DataUtil.getPhotoByID(photoID)
        storedPhoto['screenURL'] = baseURL+hashedName
        DataUtil.updatePhoto(storedPhoto)
        #web.debug(x['myfile'].value) # This is the file contents
        #web.debug(x['myfile'].file.read())  Or use a file(-like) object
        #raise web.seeother('/static/'+hashedName)
        return simplejson.dumps(dict(url= baseURL+hashedName))