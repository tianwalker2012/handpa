#I assume this data base is alway exist.
#status 1 mean not register, 2 mean login, 3 mean accept location
from datetime import datetime
datastore = {}


def fetchUser(openid):
 """This method will try to fetch first, if not exist will create a new user"""
 stored = datastore.get(openid, None)
 if stored is None:
   stored = user(openid)
   datastore[openid] = stored 
 return stored

class user:
 def __init__(self, openid):
  self.openid = openid
  self.created_at = datetime.now()
  self.updated_at = datetime.now()
  self.status = 1
  self.name = ""
  self.longitude = 0.0
  self.latitude = 0.0
  #will store the latest local label. 
  self.locLabel = None
  #what's the purpose of the combined?
  #make sure the 
  self.pendingImage = None

if __name__ == "__main__":
 user1 = fetchUser("cool")
 user1.name = "tiange"
 print "assigned name:", user1.name
 userfetched = fetchUser("cool")
 print "current name:", userfetched.name

