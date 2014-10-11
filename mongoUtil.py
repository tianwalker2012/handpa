# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 15:56:57 2013

@author: apple
"""

from pymongo import Connection #导入模块
from datetime import datetime
from bson.objectid import ObjectId
#from user import user
con = Connection()
db = con.handpa #连接test数据库

class MongoUtil:
#fetch user from the database
    @classmethod
    def fetch(self, colName, cond):
        cols = db[colName]
        return cols.find_one(cond)
    @classmethod
    def fetchByStrId(self, colName, oid):
        return  MongoUtil.fetchByID(colName, ObjectId(oid))
        
    @classmethod
    def fetchByID(self, colName, oid):
        cols = db[colName]
        return cols.find_one({'_id':oid})

#sort staff
#every time server started I will load the image. 
#I love this game so much.    
#db.collection.find().sort( { age: -1 } )
    @classmethod
    def fetchAll(self, colName, sorts = None):
        cols = db[colName]
        if sorts:
            return cols.find().sort(sorts)
        return cols.find()

    @classmethod
    def fetchSome(self, colName, conds, sorts = None):
        cols = db[colName]
        if sorts:
            return cols.find(conds).sort(sorts)
        else:
            return cols.find(conds)
    @classmethod
    def fetchWithField(self, colName, conds, fields):
        cols = db[colName]
        return cols.find(conds, fields)

    @classmethod 
    def fetchPage(self, colName, conds, startPage, pageSize, sorts = None):
        cols = db[colName]
        if sorts:        
            return cols.find(conds).skip(startPage * pageSize).limit(pageSize).sort(sorts)
        else:
            return cols.find(conds).skip(startPage * pageSize).limit(pageSize)
         
         
    @classmethod 
    def fetchWithLimit(self, colName, conds, startPos, limit, sorts = None):
        cols = db[colName]
        if sorts:        
            return cols.find(conds).skip(startPos).limit(limit).sort(sorts)
        else:
            return cols.find(conds).skip(startPos).limit(limit)

    @classmethod
    def removeAll(self, colName):
        cols = db[colName]
        cols.remove()
        
    @classmethod
    def remove(self, colName, conds):
        cols = db[colName]
        cols.remove(conds)

#This is a distructive method.
#some type of smell, I will get it done.
    @classmethod
    def create(self, colName, values):
        cols = db[colName]
        objID = cols.insert(values)
        print "insert result:", objID
        #values['_id'] = objID
        return objID

#I assume the objectID exist will turn a insert to update. 
#Let's test and verify it
#Update normally mean bulk change for many record at once.
#in my case, I'd better use save
    @classmethod
    def update(self, colName, values):
        cols = db[colName]
        #The condition of the update
        cid = values['_id']
        conds = {'_id':cid}
        #remove the id from the dictionary
        values.pop('_id',None)
        cols.update(conds,{"$set":values})
        values['_id'] = cid
   
    @classmethod
    def updateByConds(self,colName,conds,values):
        cols = db[colName]
        cols.update(conds,{"$set":values})

    @classmethod
    def save(self, colName, values):
        cols = db[colName]
        return cols.save(values)