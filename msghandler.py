#!/usr/bin/python
# -*- coding: utf-8 -*- 
#All the text message will get handled here
import web
import time
from user import user
from imagehandler import handleImageURL
from datetime import datetime
from image import Image
from image import CombinedImage
from datetime import datetime
from threading import Thread
from image import LoadedImage
from user import fetchUserByID
from user import storeUser
from time import sleep
from config import Config
from context import WebContext


textResponse = """<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%d</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
<FuncFlag>0</FuncFlag>
</xml>
"""

combineImageResponse = """<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%i</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>2</ArticleCount>
<Articles>
<item>
<Title><![CDATA[%s]]></Title> <Description><![CDATA[%s]]></Description>
<PicUrl><![CDATA[%s]]></PicUrl>
<Url><![CDATA[%s]]></Url>
</item>
<item>
<Title><![CDATA[我的羽毛（0条信息）]]></Title> <Description><![CDATA[修改你的羽毛信息]]></Description>
<PicUrl><![CDATA[%s]]></PicUrl>
<Url><![CDATA[http://www.enjoyxue.com/homepage/%s]]></Url>
</item>
</Articles>
<FuncFlag>1</FuncFlag>
</xml>"""


#All the uploaded image will be stored here
#It will have 2 messages, image URL and the user information. 
#uploadedImages = []

defaultUser = user('openid')
defaultUser.name = '羽毛粉丝'

#defaultImage = {'url':'http://www.enjoyxue.com/static/IMG_0493.JPG','user':defaultUser}
comboImages = {}

def getCurrentMillis():
 return int(round(time.time() * 1000))

def getLocationInfo(msg):
    locLabel = msg.get('Label','');
    if locLabel == '':
        if msg['MsgType'] == 'location':
            return "经度：%f,纬度:%f" % (msg['Location_X'], msg['Location_Y'])
    return locLabel

def setupImageLocation(img, msg):
    if(msg['MsgType'] == 'location'):
        img.longitude = msg['Location_X']
        img.latitude = msg['Location_Y']
        img.locLabel = getLocationInfo(msg)

def formatDate(dt):
    return dt.strftime("%d/%m/%y")

def combineImageText(img1, img2):
    result = "%s&%s\n%s&%s\n%s&%s" % (img1.author.name,img2.author.name,formatDate(img1.created_at),formatDate(img2.created_at),img1.locLabel,img2.locLabel)
    return result

def executeAsync(md):
    thread = Thread(target = md)
    thread.start()

#This method will be executed in the background thread. 
#And will generate a combinedImage object and assign it to user. 
def createCombinedImage(img, msg, inUser):
    matchedResult = getMatchedImage(inUser)
    storeUser(inUser)
    #sleep(30)
    (combinedURL,iconURL) = handleImageURL(img.url, matchedResult.url)
    combo = CombinedImage(img, matchedResult,combinedURL, iconURL)
    #inUser.combinedImage = combo
    #Make sure our change can be saw by other thread
    
    comboImages[inUser.openid] = combo
    WebContext.combinedImages.append(combo)
    combo.position = len(WebContext.combinedImages) - 1
    

def getComboImage(inUser):
    return comboImages.get(inUser.openid, None)
    
def removeComboImage(inUser):
    comboImages.pop(inUser.openid, None)

def space4None(content):
    return content if content else ''
#The message is the message passed by user.
#may contain the location message.
#Todo I need to store the image description update 
def createResponseByCombinedImage(inUser,combo, msg, appOpenID):
    author = fetchUserByID(combo.imageTwo.authorID)
    combinedName = "我和%s的合影" % (author.nickName)
    #combineImageText(img, matchedResult)
    if msg['MsgType'] == 'text':
        combo.imageOne.description = msg['Content']
    elif msg['MsgType'] == 'location':
        combo.imageOne.description = msg['Label']
    combo.imageOne.save()
    
    combinedDescription = "我说:%s\n%s说:%s" % (space4None(combo.imageOne.description), author.nickName,space4None(combo.imageTwo.description)) 
    detailURL = Config.comboDetailURL % (combo.position)
    return combineImageResponse % (inUser.openid,appOpenID,getCurrentMillis(),combinedName,combinedDescription,combo.iconURL, detailURL,inUser.avatar if inUser.avatar else Config.iconImage, inUser.openid)

def getMatchedImage(inUser):
    """Get an image can match this user, keep it simple and stupid"""
    if len(LoadedImage.loadedImages) > 0:
        for img in reversed(LoadedImage.loadedImages):
            imgUser = fetchUserByID(img.authorID)
            if (inUser.openid != imgUser.openid) and not(inUser.combinedHistory.get(str(img._id), None)):
                inUser.combinedHistory[str(img._id)] = 'used'
                return img
    dfImage = Image()
    dfImage.author = user('openid')
    dfImage.author.nickName = '羽毛粉丝'
    dfImage.url = 'http://www.enjoyxue.com/static/IMG_0493.JPG'
    return dfImage

def storeUploadImage(url, inUser, msg):
    """Will store a image into memory"""
    img = Image()
    #img.author = inUser
    img.authorID = inUser._id
    #img.created_at = datetime.now()
    #img.locLabel = user.locLabel
    img.url = url
    setupImageLocation(img, msg)        
    LoadedImage.loadedImages.append(img)
    img.save()
    return img

#Following is status transation logic, 1 mean first time get our service
#Then jump to 3, mean first trial, after the trial is done, 
#the status is 4, we will need you to give use the nick name. 
#Then status is 5, mean pending avarter. 
#Then status is 6, pending weixin number
#then status is 7, mean register success. 
#cool. 
def handle(msg, inUser):
    """All the msg will be handled by me. all the logic will changed here"""
    appOpenID = msg.get('ToUserName', None)
    print "current status:",inUser.status,",msg type:",msg['MsgType']
    inUser.updated_at = datetime.now()
    #inUser.status = 3
    if msg['MsgType'] == 'event':
        #I assume only subscribtion will have event.    
        #inUser.status = 3
        print 'new user subscribe us, id:', inUser.openid
        return textResponse % (inUser.openid,appOpenID,getCurrentMillis(),"""感谢使用羽毛相机。发送照片到羽毛相机，瞬间抓到一起拍照的小伙伴，体验照片空中合体。""")    
    if inUser.status == 1:
        #inUser.status = 3
        if msg['MsgType'] == 'event':
            #I assume only subscribtion will have event.    
            inUser.status = 3
            print 'new user subscribe us, id:', inUser.openid
            return textResponse % (inUser.openid,appOpenID,getCurrentMillis(),"""感谢使用羽毛相机。发送照片到羽毛相机，瞬间抓到一起拍照的小伙伴，体验照片空中合体。请先输入微信号码（不是中文昵称）完成注册：""")
        elif msg['MsgType'] == 'text':
            inUser.status = 2
            print 'recived user name:',inUser.openid,", name:",msg.get('Content', None)
            inUser.name = msg.get('Content', None)
            return textResponse % (inUser.openid,appOpenID,getCurrentMillis(),"""为保证微信号码准确，请再输入一次：""")
        else:
            print 'revieved none text message'
            return textResponse % (inUser.openid, appOpenID,getCurrentMillis(), """请先输入微信号码（不是中文昵称）完成注册：""")
    elif inUser.status == 2:
        if msg['MsgType'] == 'text':
            inUser.status = 3
            print 'I will change status to 3, actual status:', inUser.status
            return textResponse % (inUser.openid, appOpenID,getCurrentMillis(), """注册成功。请试拍你的第一张羽毛照片。""")
        else:
            return textResponse % (inUser.openid,appOpenID,getCurrentMillis(),"""为保证微信号码准确，请再输入一次：""")
    
    elif inUser.status == 4:
        if msg['MsgType'] == 'image':
            img = storeUploadImage(msg['PicUrl'], inUser, msg)
        inUser.status = 5
        return textResponse % (inUser.openid,appOpenID,getCurrentMillis(),"""给自己取个昵称让羽毛里的小伙伴们多一个喜欢你理由。""")
    elif inUser.status == 5:
        if msg['MsgType'] == 'image':
            img = storeUploadImage(msg['PicUrl'], inUser, msg)
        elif msg['MsgType'] == 'text':
            inUser.nickName = msg['Content']
            inUser.status = 6
            return textResponse % (inUser.openid,appOpenID,getCurrentMillis(),"""请上传你的头像。酷一点的是必须的""")
        return textResponse % (inUser.openid,appOpenID,getCurrentMillis(),"""给自己取个昵称让羽毛里的小伙伴们多一个喜欢你理由。""")
    elif inUser.status == 6:
        if msg['MsgType'] == 'image':
            #img = storeUploadImage(msg['PicUrl'], inUser, msg)
            inUser.avatar = msg['PicUrl']
            inUser.status = 7
            return textResponse % (inUser.openid,appOpenID,getCurrentMillis(),"""最后一步了，输入微信号码（不是中文昵称），让羽毛上的小伙伴们能跟你分享更多好照片：""")
        return textResponse % (inUser.openid,appOpenID,getCurrentMillis(),"""请上传你的头像。酷一点是的必须的""")
    elif inUser.status == 7:
        if msg['MsgType'] == 'image':
            img = storeUploadImage(msg['PicUrl'], inUser, msg)
        elif msg['MsgType'] == 'text':
            inUser.name = msg['Content']
            inUser.status = 8
            return textResponse % (inUser.openid,appOpenID,getCurrentMillis(),"""谢谢你注册羽毛，尽情体验照片空中合体乐趣吧！""")
        return textResponse % (inUser.openid,appOpenID,getCurrentMillis(),"""最后一步了，输入微信号码（不是中文昵称），让羽毛上的小伙伴们能跟你分享更多好照片：""")

    elif inUser.status == 3 or inUser.status == 8:
        print 'I am in status:', inUser.status,",my type:",msg['MsgType']
        #indicate current request is 
        if msg['MsgType'] == 'image':
            img = storeUploadImage(msg['PicUrl'],inUser,msg)
            inUser.pendingCombine = 1
            def processImage():
                createCombinedImage(img, msg, inUser)
            #execute the image generation in background thread
            executeAsync(processImage)
            
            if getComboImage(inUser) == None:
                #inUser.pendingImage = img
                return textResponse % (inUser.openid, appOpenID,getCurrentMillis(), """拍摄成功！记下你的真实想法或者发送地理位置""")
        comboImage = getComboImage(inUser)
        if comboImage:
            #pendingImage = inUser.pendingImage
            #combinedImage = inUser.combinedImage
            #inUser.combinedImage = None
            removeComboImage(inUser)
            inUser.pendingCombine = 0
            displayMsg = inUser.lastMessage if inUser.lastMessage else msg
            resText = createResponseByCombinedImage(inUser,comboImage, displayMsg, appOpenID)
            inUser.lastMessage = None            
            print 'Response:', resText
            if inUser.status == 3:
                print "change status:", 4
                inUser.status = 4
            return resText
        else:
            if(inUser.pendingCombine):
                #Mean we are working on the image.
                if not inUser.lastMessage:
                    inUser.lastMessage = msg
                return textResponse % (inUser.openid, appOpenID,getCurrentMillis(), """亲，羽毛在很努力很努力得帮你合照片，稍候几秒发任意信息取回。""")
            return textResponse % (inUser.openid, appOpenID,getCurrentMillis(), """试拍一张羽毛照片。""")
      
if __name__ == "__main__":
 userGirl = user("coolid");
 #user.name = "tiange";
 userGirl.name = "coolguy"
 userGirl.status = 3
 msg = {"MsgType":"image","PicUrl":"http://127.0.0.1:8080/static/IMG_1782.JPG", "ToUserName":"feather", "FromUserName":"hotgirl","Content":"hotgirl", "Location_X":79.00283,"Location_Y":81.00833}
 response = handle(msg, userGirl);
 print "user name:",userGirl.name,":",response,"%f,%f" % (userGirl.longitude,userGirl.latitude)


