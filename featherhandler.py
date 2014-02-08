# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 17:19:11 2014

@author: xie tian
"""
import web
import simplejson
import hashlib
from datetime import datetime

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
        params = web.input()
        web.debug("all the inputs:"+ str(params))
        return simplejson.dumps(dict(personID=10, name="coolguy",email="xie.tian@gmail.com"))

class FeatherRegister:
    def GET(self):
        return "empty"
    def POST(self):
        params = web.input()
        web.debug("post inputs:"+ str(params))
        return simplejson.dumps(dict(personID=10, name="coolguy", email="xie.tian@gmail.com"))

class UploadHandler:
    def GET(self):
        web.debug("upload get called"+ str(web.data()))
        return simplejson.dumps(dict(info='what up'))
        
    def POST(self):
        #web.debug("upload post get called:"+ str(web.input()))
        x = web.input(myfile={})
        personid = x["personid"]
        storedDir = '/Users/apple/Documents/handpa/static/'
        baseURL = 'http://192.168.1.103:8080/static/'
        filePath = x['myfile'].filename.replace('\\','/').split('/')[-1]
        postFix = filePath.split('.')[-1]
        hashedName = hashlib.md5(filePath + str(datetime.now())).hexdigest() + '.' + postFix
        fout = open(storedDir+hashedName, 'w')
        fout.write(x.myfile.file.read())
        fout.close()
        web.debug(x['myfile'].filename) # This is the filename
        web.debug("personid:"+personid)
        #web.debug(x['myfile'].value) # This is the file contents
        #web.debug(x['myfile'].file.read())  Or use a file(-like) object
        #raise web.seeother('/static/'+hashedName)
        return simplejson.dumps(dict(url= baseURL+hashedName))