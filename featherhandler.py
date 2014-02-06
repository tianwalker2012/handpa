# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 17:19:11 2014

@author: xie tian
"""
import web
import simplejson
import hashlib
from datetime import datetime

class FeatherHandler:
    def GET(self):
        return "Get ready"
                
        
    def POST(self):
        return "Post ready"

class UploadHandler:
    def GET(self):
        return "Upload get ready"
                
        
    def POST(self):
        x = web.input(myfile={})
        personid = x["personid"]
        storedDir = '/Users/apple/Documents/handpa/static/'
        baseURL = '/static/'
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
        return dict(url= baseURL+hashedName)