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
from time import sleep

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
<ArticleCount>1</ArticleCount>
<Articles>
<item>
<Title><![CDATA[%s]]></Title> <Description><![CDATA[%s]]></Description>
<PicUrl><![CDATA[%s]]></PicUrl>
<Url><![CDATA[%s]]></Url>
</item>
</Articles>
<FuncFlag>1</FuncFlag>
</xml>"""


#All the uploaded image will be stored here
#It will have 2 messages, image URL and the user information. 
uploadedImages = []

defaultUser = user('openid')
defaultUser.name = '羽毛粉丝'

#defaultImage = {'url':'http://www.enjoyxue.com/static/IMG_0493.JPG','user':defaultUser}

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
    (combinedURL,iconURL) = handleImageURL(img.url, matchedResult.url)
    combo = CombinedImage(img, matchedResult,combinedURL, iconURL)
    inUser.combinedImage = combo

#The message is the message passed by user.
#may contain the location message. 
def createResponseByCombinedImage(inUser,combo, msg, appOpenID):
    combinedName = "%s和%s的合影" % (combo.imageOne.author.name, combo.imageTwo.author.name)
    #combineImageText(img, matchedResult)
    combinedDescription = ""
    return combineImageResponse % (inUser.openid,appOpenID,getCurrentMillis(),combinedName,combinedDescription,combo.iconURL, combo.imageURL)

#Now this method only used as a reference.
#I will use the async functionality to achieve this.
def generateCombineImage(img, msg, appOpenID):
    inUser = img.author    
    print 'Recieved image from user:', inUser.name,",url:",msg['PicUrl']
    #myimage = downloadImage(msg['PicUrl'])
    #matchedImage = getMatchedImage(user)
    setupImageLocation(img, msg)
    matchedResult = getMatchedImage(inUser)
    matchedUser = matchedResult.author
    matchedURL = matchedResult.url
    combinedURL = handleImageURL(img.url, matchedURL, 0)
    iconURL = handleImageURL(img.url, matchedURL, 1)
    combinedName = "%s和%s的合影" % (inUser.name,matchedUser.name)
    #
    #1. toID, 2.fromID, createTime,title,content,smallImage,imageURl
    return combineImageResponse % (inUser.openid,appOpenID,getCurrentMillis(),combinedName,combineImageText(img, matchedResult),iconURL, combinedURL)

def getMatchedImage(inUser):
    """Get an image can match this user, keep it simple and stupid"""
    if len(uploadedImages) > 0:
        for img in reversed(uploadedImages):
            if inUser.openid != img.author.openid:
                return img
    dfImage = Image()
    dfImage.author = user('openid')
    dfImage.author.name = '羽毛粉丝'
    dfImage.url = 'http://www.enjoyxue.com/static/IMG_0493.JPG'
    return dfImage

def storeUploadImage(url, inUser, msg):
    """Will store a image into memory"""
    img = Image()
    img.author = inUser
    #img.created_at = datetime.now()
    #img.locLabel = user.locLabel
    img.url = url
    setupImageLocation(img, msg)        
    uploadedImages.append(img)
    return img
 
def handle(msg, inUser):
    """All the msg will be handled by me. all the logic will changed here"""
    appOpenID = msg.get('ToUserName', None)
    print "current status:",inUser.status,",msg type:",msg['MsgType']
    inUser.updated_at = datetime.now()
    #inUser.status = 3
    if inUser.status == 1:
        if msg['MsgType'] == 'event':
            #I assume only subscribtion will have event.    
            inUser.status = 1
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
    elif inUser.status == 3:
        print 'I am in status:', inUser.status,",my type:",msg['MsgType']
        if msg['MsgType'] == 'image':
            img = storeUploadImage(msg['PicUrl'],inUser,msg)
            def processImage():
                createCombinedImage(img, msg, inUser)
            #execute the image generation in background thread
            executeAsync(processImage)
            
            if inUser.combinedImage == None:
                #inUser.pendingImage = img
                return textResponse % (inUser.openid, appOpenID,getCurrentMillis(), """拍摄成功！请发送你的地点，或发送任何文字忽略地点。""")
        if inUser.combinedImage:
            #pendingImage = inUser.pendingImage
            combinedImage = inUser.combinedImage
            inUser.combinedImage = None
            resText = createResponseByCombinedImage(inUser,combinedImage, msg, appOpenID)
            print 'Response:', resText
            return resText
        else:
            return textResponse % (inUser.openid, appOpenID,getCurrentMillis(), """试拍一张羽毛照片。""")
      
if __name__ == "__main__":
 userGirl = user("coolid");
 #user.name = "tiange";
 userGirl.name = "coolguy"
 userGirl.status = 3
 msg = {"MsgType":"image","PicUrl":"http://127.0.0.1:8080/static/IMG_1782.JPG", "ToUserName":"feather", "FromUserName":"hotgirl","Content":"hotgirl", "Location_X":79.00283,"Location_Y":81.00833}
 response = handle(msg, userGirl);
 print "user name:",userGirl.name,":",response,"%f,%f" % (userGirl.longitude,userGirl.latitude)


