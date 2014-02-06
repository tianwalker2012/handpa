# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 07:30:01 2013

@author: apple
"""

from pymongo import Connection #导入模块
from datetime import datetime
from baseobject import BaseObject

con = Connection()
db = con.handpa #连接test数据库
posts = db.testData

class objects:
  def __init__(self, nm):
    self.name = nm

class SimpleObj(BaseObject):
    def __init__(self, nm):
        self.name = nm

class ComplexObj(BaseObject):
    def __init__(self):
        self.simples = [SimpleObj('tiange'), SimpleObj('TengLuo')]
        self.maps = {"daughters":SimpleObj('XieChengyue'),"lists":[1,2,3],"maps":{"pureMap":"verypure"}}
        self.lists = [SimpleObj('Purpose'),"Responsible",{"any":"like"}]
        self.name = "VeryComplex"

if __name__ == "__main__":
    #obj = objects('tiange')
    #posts.insert({'name':'Coolguys mongo experiment','created_at':datetime.now(), 'person':obj})
    complexObj = ComplexObj();    
    print 'Success, serialized:', complexObj.serialize()
