# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 15:56:57 2013

@author: apple
"""

from pymongo import Connection #导入模块
from datetime import datetime
#from user import user
con = Connection()
db = con.handpa #连接test数据库

#fetch user from the database
def fetch(colName, cond):
    cols = db[colName]
    return cols.find_one(cond)

def fetchByID(colName, oid):
    cols = db[colName]
    return cols.find_one({'_id':oid})

#sort staff
#every time server started I will load the image. 
#I love this game so much.    
#db.collection.find().sort( { age: -1 } )
def fetchAll(colName, sorts):
    cols = db[colName]
    return cols.find().sort(sorts)
    
def fetchSome(colName, conds, sorts):
    cols = db[colName]
    return cols.find(conds).sort(sorts)


def removeAll(colName):
    cols = db[colName]
    cols.remove()

#This is a distructive method.
#some type of smell, I will get it done.
def create(colName, values):
    cols = db[colName]
    objID = cols.insert(values)
    print "insert result:", objID
    #values['_id'] = objID
    return objID

#I assume the objectID exist will turn a insert to update. 
#Let's test and verify it
#Update normally mean bulk change for many record at once.
#in my case, I'd better use save
def update(colName, values):
    cols = db[colName]
    #The condition of the update    
    conds = {'_id':values['_id']}
    #remove the id from the dictionary
    values.pop('_id',None)
    cols.update(conds,{"$set":values})

def save(colName, values):
    cols = db[colName]
    return cols.save(values)