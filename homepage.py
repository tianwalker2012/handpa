# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 08:34:59 2013

@author: apple
"""
import web
from user import user, fetchUser,storeUser
from context import WebContext
class homepage:
    def GET(self, openid):
        print "Passed openid:", openid
        params = web.input()
        isUpdate = params.get('update', None)
        updateInfo = "更新个人信息成功！" if isUpdate else ""
        inUser = fetchUser(openid)
        return WebContext.render.homepage(updateInfo, inUser.name, inUser.nickName, openid)

    def POST(self, openid):
         params = web.input()
         openid = params['openid']
         print "input:",params
         inUser = fetchUser(openid)
         oldName = inUser.name
         oldNickname = inUser.nickName
         inUser.name = params.get('name',"")
         inUser.nickName = params.get('nickname',"羽毛游客")
         storeUser(inUser)
         print "oldName:%s, old nickName:%s, updated name:%s, nickName:%s" % (oldName, oldNickname, inUser.name, inUser.nickName)
         revisit = '/homepage/%s?update=true' % (openid)
         #web.debug(x['myfile'].filename) # This is the filename
         #web.debug(x['myfile'].value) # This is the file contents
         #web.debug(x['myfile'].file.read()) # Or use a file(-like) object
         raise web.seeother(revisit)