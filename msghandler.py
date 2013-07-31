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

defaultImage = {'url':'http://www.enjoyxue.com/static/IMG_0493.JPG','user':defaultUser}

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
    return img1.author.name+"&"+img2+"\n"+formatDate(img1.created_at)+"&"+formatDate(img2.created_at)+"\n"+img1.locLabel+"&"+img2.locLabel

def generateCombineImage(img, msg, appOpenID):
    user = img.author    
    print 'Recieved image from user:', user.name,",url:",msg['PicUrl']
    #myimage = downloadImage(msg['PicUrl'])
    #matchedImage = getMatchedImage(user)
    setupImageLocation(img, msg)
    matchedResult = getMatchedImage(user)
    matchedUser = matchedResult.author
    matchedURL = matchedResult.url
    combinedURL = handleImageURL(img.url, matchedURL, 0)
    iconURL = handleImageURL(img.url, matchedURL, 1)
    #
    #1. toID, 2.fromID, createTime,title,content,smallImage,imageURl
    return combineImageResponse % (user.openid,appOpenID,getCurrentMillis(),user.name+"和"+matchedUser.name+"的合影",combineImageText(img, matchedResult),iconURL, combinedURL)

def getMatchedImage(user):
    """Get an image can match this user, keep it simple and stupid"""
    if len(uploadedImages) > 0:
        for img in reversed(uploadedImages):
            if user.openid != img.author.openid:
                return img
    return defaultImage

def storeUploadImage(url, user, msg):
    """Will store a image into memory"""
    img = Image()
    img.author = user
    #img.created_at = datetime.now()
    #img.locLabel = user.locLabel
    img.url = url
    setupImageLocation(img, msg)        
    uploadedImages.append(img)
    return img
 
def handle(msg, user):
    """All the msg will be handled by me. all the logic will changed here"""
    appOpenID = msg.get('ToUserName', None)
    user.updated_at = datetime.now()
    if user.status == 1:
        if msg['MsgType'] == 'event':
            #I assume only subscribtion will have event.    
            user.status = 1
            print 'new user subscribe us, id:', user.openid
            return textResponse % (user.openid,appOpenID,getCurrentMillis(),"""感谢使用羽毛相机。发送照片到羽毛相机，瞬间抓到一起拍照的小伙伴，体验照片空中合体。请先输入微信号码（不是中文昵称）完成注册：""")
        elif msg['MsgType'] == 'text':
            user.status = 2
            print 'recived user name:',user.openid,", name:",msg.get('Content', None)
            user.name = msg.get('Content', None)
            return textResponse % (user.openid,appOpenID,getCurrentMillis(),"""为保证微信号码准确，请再输入一次：""")
        else:
            print 'revieved none text message'
            return textResponse % (user.openid, appOpenID,getCurrentMillis(), """请先输入微信号码（不是中文昵称）完成注册：""")
    elif user.status == 2:
        if msg['MsgType'] == 'text':
            user.status == 3
            return textResponse % (user.openid, appOpenID,getCurrentMillis(), """注册成功。请试拍你的第一张羽毛照片。""")
        else:
            return textResponse % (user.openid,appOpenID,getCurrentMillis(),"""为保证微信号码准确，请再输入一次：""")
    elif user.status == 3:
        if msg['MsgType'] == 'image':
            img = storeUploadImage(msg['PicUrl'],user,msg)
            if user.pendingImage == None:
                user.pendingImage = img
                return textResponse % (user.openid, appOpenID,getCurrentMillis(), """拍摄成功！请发送你的地点，或发送任何文字忽略地点。""")
        if user.pendingImage:
            pendingImage = user.pendingImage
            user.pendingImage = None
            return generateCombineImage(pendingImage, msg, appOpenID)
        else:
            return textResponse % (user.openid, appOpenID,getCurrentMillis(), """试拍一张羽毛照片。""")
      
if __name__ == "__main__":
 userGirl = user("coolid");
 #user.name = "tiange";
 userGirl.name = "coolguy"
 userGirl.status = 3
 msg = {"MsgType":"image","PicUrl":"http://127.0.0.1:8080/static/IMG_1782.JPG", "ToUserName":"feather", "FromUserName":"hotgirl","Content":"hotgirl", "Location_X":79.00283,"Location_Y":81.00833}
 response = handle(msg, userGirl);
 print "user name:",userGirl.name,":",response,"%f,%f" % (userGirl.longitude,userGirl.latitude)


