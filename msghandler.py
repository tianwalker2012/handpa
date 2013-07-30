#!/usr/bin/python
# -*- coding: utf-8 -*- 
#All the text message will get handled here
import web
import time
from user import user
from imagehandler import handleImageURL
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
defaultUser.name = '羽毛'

defaultImage = {'url':'http://127.0.0.1:8080/static/IMG_0493.JPG','user':defaultUser}

def getCurrentMillis():
 return int(round(time.time() * 1000))


def getMatchedImage(user):
 """Get an image can match this user, keep it simple and stupid"""
 if len(uploadedImages) > 0:
  return uploadedImages[-1]
 return defaultImage

def storeUploadImage(url, user):
    uploadedImages.append({'url':url, 'user':user})
 
def handle(msg, user):
 """All the msg will be handled by me. all the logic will changed here"""
 appOpenID = msg.get('ToUserName', None)
 user.updated_at = datetime.now()
 if user.status == 1:
  if msg['MsgType'] == 'text':
    user.status = 2;
    print 'recived user name:',user.openid,", name:",msg.get('Content', None)
    user.name = msg.get('Content', None)
    appOpenID = msg.get('ToUserName', None )
    return textResponse % (user.openid,appOpenID,getCurrentMillis(),"""还有最后一步，点击下方的加号然后点击位置按钮发送给羽毛，就可以和附近的朋友合照片了!""")
  else:
    print 'revieved none text message'
    return textResponse % (user.openid, appOpenID,getCurrentMillis(), """请输入您的微信号完成注册：（不是中文昵称哦～请务必正确输入）""")
 elif user.status == 2:
  if msg['MsgType'] == 'location':
    user.status = 3
    print 'recieved all info:',user.openid ,",name:",user.name
    user.latitude = msg['Location_X']
    user.longitude = msg['Location_Y']
    print 'recieved all info:',user.openid ,",name:",user.name,',latitude,longitude:',user.latitude,",",user.longitude
    return textResponse % (user.openid, appOpenID,getCurrentMillis(),"""感谢注册，发送你的第一张照片看看有什么惊喜吧""")
  else:
    print 'Recieved type:%s at status 3' % (msg['MsgType'])
    return textResponse % (user.openid, appOpenID,getCurrentMillis(), """点击下方的加号然后点击位置按钮发送给羽毛，就可以和附近的朋友合照片了!""")
 elif user.status == 3:
  if msg['MsgType'] == 'image':
   print 'Recieved image from user:', user.name,",url:",msg['PicUrl']
   #myimage = downloadImage(msg['PicUrl'])
   #matchedImage = getMatchedImage(user)
   matchedResult = getMatchedImage(user)
   matchedUser = matchedResult['user']
   matchedURL = matchedResult['url']
   combinedURL = handleImageURL(msg['PicUrl'], matchedURL)
   storeUploadImage(msg['PicUrl'], user)
   #1. toID, 2.fromID, createTime,title,content,smallImage,imageURl
   return combineImageResponse % (user.openid,appOpenID,getCurrentMillis(),"羽毛飘来","你和"+matchedUser.name+"的合图",combinedURL, combinedURL)
  else:
   return textResponse % (user.openid, appOpenID,getCurrentMillis(), """给羽毛发张照片，然后....""")

if __name__ == "__main__":
 userGirl = user("coolid");
 #user.name = "tiange";
 userGirl.name = "coolguy"
 userGirl.status = 3
 msg = {"MsgType":"image","PicUrl":"http://127.0.0.1:8080/static/IMG_1782.JPG", "ToUserName":"feather", "FromUserName":"hotgirl","Content":"hotgirl", "Location_X":79.00283,"Location_Y":81.00833}
 response = handle(msg, userGirl);
 print "user name:",userGirl.name,":",response,"%f,%f" % (userGirl.longitude,userGirl.latitude)


