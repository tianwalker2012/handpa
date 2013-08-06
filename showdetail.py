# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 09:20:43 2013

@author: apple
"""

import web
from user import user, fetchUser,storeUser,fetchUserByID
from context import WebContext
from image import Image
class showdetail:
    def GET(self, pos):
        print "Passed combo position:", pos, ",comboSize:", len(WebContext.combinedImages)
        intPos = int(pos)        
        comboArr = WebContext.combinedImages
        if(intPos > len(comboArr)):
            return "Not exist combo"
        comboImage = comboArr[intPos]
        #params = web.input()
        #isUpdate = params.get('update', None)
        #updateInfo = "更新个人信息成功！" if isUpdate else ""
        #inUser = fetchUser(openid)
        #with(combo, combineTitle, myself, otherUser)
        otherSide = fetchUserByID(comboImage.imageTwo.authorID)
        me = fetchUserByID(comboImage.imageOne.authorID)
        comboTitle = "我和%s的合影" % (otherSide.nickName)
        return WebContext.render.showdetail(comboImage, comboTitle, me, otherSide)
