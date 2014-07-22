#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import web
from xml.dom.minidom import parseString
import hashlib
from user import user, fetchUser,storeUser
from msghandler import handle
from image import getAllImages
from image import LoadedImage
from homepage import homepage
from showdetail import showdetail
from context import WebContext
from baseobject import BaseObject
from baseobject import isSerializable
#import gluon.contrib.simplejson
import simplejson
from featherhandler import FeatherHandler
from featherhandler import UploadHandler
from featherhandler import FeatherLogin
from featherhandler import FeatherRegister
from featherhandler import FeatherContacts
from featherhandler import PhotoHandler
from featherhandler import PersonHandler
from featherhandler import ExchangeHandler
from featherhandler import FriendShip
from featherhandler import PhotoURL
from infocollector import InfoCollector
from chathandler import ChatHandler
from photochathandler import PhotoChatHandler
from notify import Notify
from photowall import PhotoWall
from photowall import PhotoWallDisplay
from touchhandler import TouchHandler
from mobilecapture import MobileCapture

render = web.template.render('templates/')
WebContext.render = render
#db = web.database(dbn='mysql', user='handpa', pw='handpa', db='handpa')
urls = (
 '/', 'index',
 '/homepage/(.+)', 'homepage',
 '/photourl/(.+)', 'PhotoURL',
 '/uploader', 'uploader',
 '/showdetail/(.+)', 'showdetail',
 '/todo', 'todo',
 '/resttest/(.+)/(.+)', 'RestTest',
 '/haha', 'hahaclass',
 '/outputtest','outputtest',
 '/feather', 'FeatherHandler',
 '/upload', 'UploadHandler',
 '/login', 'FeatherLogin',
 '/broken/(.+)', 'BrokenTest',
 '/register', 'FeatherRegister',
 '/query/contacts','FeatherContacts',
 '/photo/info',"PhotoHandler",
 '/person/info',"PersonHandler",
 '/photo/exchange', 'ExchangeHandler',
 '/friend', 'FriendShip',
 '/notify', 'Notify',
 '/info','InfoCollector',
 '/chat', 'ChatHandler',
 '/store', 'AppStore',
 '/pchat','PhotoChatHandler',
 '/photowall', 'PhotoWall',
 '/photodisplay', 'PhotoWallDisplay',
 '/touch', 'TouchHandler',
 '/mobilecapture', 'MobileCapture',
 '/nativeupload','uploader'
)

class AppStore:
    def GET(self):
        return self.POST()
    
    def POST(self):
        web.ctx.status = '302 Moved Temporarily'
        #web.debug('headers:%s, tuple is:%r'% (web.ctx.headers, ('Location', pt['screenURL'].encode("ASCII", 'ignore') if pt['screenURL'] else '')) )
        web.ctx.headers.append(('Location','https://itunes.apple.com/cn/app/yu-mao/id873928141?mt=8'))
        return ''
        
class BrokenTest:
    def GET(self, brokenPoint):
        bi = int(brokenPoint)
        web.debug('broken point %i' % int(brokenPoint))
        web.header('Content-type','images/jpeg')
        #web.header('Transfer-Encoding','chunked') 
        f = open("/Users/apple/Documents/handpa/static/0ac59a6b21390f7e06243eb14b343a76.jpg", 'rb')
        contents = f.read()
        web.debug('content length:%i' % len(contents))  
        if(len(contents) < bi):
            bi = len(contents)
        return contents[:bi]

class RestTest:
    def GET(self, fst, sec):
        return 'first value:%s, second value:%s' % (fst, sec)

class JsonObject(BaseObject):
 def __init__(self, name, gender):
  self.name = name
  self.gender = gender 


def getText(nodelist):
 rc = []
 for node in nodelist:
  if node.nodeType == node.TEXT_NODE:
   rc.append(node.data)
 return ''.join(rc)

def getTagValue(rootNode, tagName):
 tagNodes = rootNode.getElementsByTagName(tagName)
 if len(tagNodes) > 0:
  return tagNodes[0].firstChild.nodeValue.strip()
 return None
 
def getTagData(rootNode, tagName):
 tagNodes = rootNode.getElementsByTagName(tagName)
 if len(tagNodes) > 0:
  return tagNodes[0].firstChild.data.strip()
 return None

def printObjectDetail(obj):
 """vars(Foo()) #==> {'a': 1, 'b': 2}
vars(Foo()).keys() #==> ['a', 'b']"""
 print 'I will print the object detail'
 varmap = vars(obj)
 varkeys = varmap.keys()
 for key in varkeys:
  print key,":",varmap[key]
  
def printAttribute(obj):
 for md in dir(web.input):
  print 'attribute:',md 

def handleMessage(msgs):
 """Will do the message processing here, now only handle text and image message"""
 msgType = msgs['MsgType']
 if msgType == 'text':
  print 'Received text message'
  return """Thanks for register"""
 elif msgType == 'image':
  print 'Received image message'
  return """Thanks for your image"""
 else:
  print 'message type:',msgType
  return """Thanks for your love"""

def parseMessage(dom1):
  """Store data in dom to a Map"""
  res = {}
  #shared field
  res['MsgType'] = getTagData(dom1,'MsgType')
  res['CreateTime'] = getTagValue(dom1,'CreateTime')
  res['FromUserName'] = getTagData(dom1, 'FromUserName')
  res['ToUserName'] = getTagData(dom1, 'ToUserName')
  res['MsgId'] = getTagValue(dom1, 'MsgId') 
  
  #event 
  res['Event'] = getTagValue(dom1, None)
  
  #text message only
  res['Content'] = getTagData(dom1, 'Content');
  
  #image message only
  res['PicUrl'] = getTagData(dom1, 'PicUrl');
  
  #location message only
  res['Location_X'] = getTagValue(dom1, 'Location_X');
  res['Location_Y'] = getTagValue(dom1, 'Location_Y');
  res['Scale'] = getTagValue(dom1, 'Scale');
  res['Label'] = getTagData(dom1, 'Label');
  
  #link message only
  res['Title'] = getTagData(dom1, 'Title')
  res['Description'] = getTagData(dom1, 'Description')
  res['Url'] = getTagData(dom1, 'Url')
  return res

class outputtest:
 def GET(self):
     out1 = "coolguy"
     out2 = "hotgirl"
     jobj = JsonObject("tian", 37)
     return jobj.serialize()
 def POST(self):
     webData = web.data()
     print "body is:", webData
     parsedJson = simplejson.loads(webData)
     return parsedJson["name"]
class index:
 def GET(self):
  #what's the meaning of this?
  echoVal = web.input(echostr=None)
  print "recieved weixin access:", echoVal
  return echoVal.echostr

 def POST(self):
  """I assume only accept dom as parameter"""
  webData = web.data()
  print "body is:", webData
  dom1 = parseString(webData);
  msg = parseMessage(dom1)
  storedUser = fetchUser(msg['FromUserName'])
  result = handle(msg, storedUser)
  #Make sure the user will 
  storeUser(storedUser)
  #The purpose is to make sure the whole thing get flush out, so that 
  #I could check the result immediately.
  import sys
  sys.stdout.flush()
  return result
   
   
class todo:
 def GET(self):
  #todos = db.select('todo')
  return render.index('todo list')

class uploader:
 def GET(self):
  return """<html><head></head><body>
         <form method="POST" enctype="multipart/form-data" action="/upload">
         <input type="file" name="myfile" />
         <br/>
         <input type="submit" />
         </form>
         </body></html>"""

 def POST(self):
  x = web.input(myfile={})
  storedDir = '/Users/apple/Documents/handpa/static/'
  #filePath = x['myfile'].filename.replace('\\','/').split('/')[-1]
    
  
  #postFix = filePath.split('.')[-1]
  hashedName = 'uploadimage.jpg' #hashlib.md5(filePath).hexdigest() + '.' + postFix
  fout = open(storedDir+hashedName, 'w')
  fout.write(x.myfile.file.read())
  fout.close()
  #web.debug(x['myfile'].filename) # This is the filename
  #web.debug(x['myfile'].value) # This is the file contents
  #web.debug(x['myfile'].file.read())  Or use a file(-like) object
  raise web.seeother('/static/'+hashedName)

#web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
if __name__ == "__main__":
 import sys
 reload(sys)
 sys.setdefaultencoding('utf-8')
 app = web.application(urls, globals())
 #Will load all previous images
 #Since only some string,I guess I can load them all to memory
 getAllImages()
 print "Previous stored image is:", len(LoadedImage.loadedImages)
 #logFile = open("/tmp/confirm.log","wt")
 #print >> logFile, "YES"
 app.run()

