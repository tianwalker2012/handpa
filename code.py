import web
from xml.dom.minidom import parseString

render = web.template.render('templates/')
#db = web.database(dbn='mysql', user='handpa', pw='handpa', db='handpa')
urls = (
 '/', 'index',
 '/uploader', 'uploader',
 '/todo', 'todo'
)

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


class index:
 def GET(self):
  #what's the meaning of this?
  echoVal = web.input(echostr=None)
  return echoVal.echostr

 def POST(self):
  """I assume only accept dom as parameter"""
  webData = web.data()
  print "body is:", webData
  dom1 = parseString(webData);
  msgs = parseMessage(dom1)
  return handleMessage(msgs)
   
   
class todo:
 def GET(self):
  #todos = db.select('todo')
  return render.index('todo list')

class uploader:
 def GET(self):
  return """<html><head></head><body>
         <form method="POST" enctype="multipart/form-data" action="">
         <input type="file" name="myfile" />
         <br/>
         <input type="submit" />
         </form>
         </body></html>"""

 def POST(self):
  x = web.input(myfile={})
  web.debug(x['myfile'].filename) # This is the filename
  web.debug(x['myfile'].value) # This is the file contents
  web.debug(x['myfile'].file.read()) # Or use a file(-like) object
  raise web.seeother('/upload')

if __name__ == "__main__":
 app = web.application(urls, globals())
 app.run()

