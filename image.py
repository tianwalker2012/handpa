# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 22:52:53 2013

@author: apple
"""
from datetime import datetime 

class Image:
    counter = 1
    def __init__(self):
        Image.counter += 1
        self.id = Image.counter
        self.author = None
        self.created_at = datetime.now()
        self.url = ''
        self.longitude = 0.0
        self.latitude = 0.0
        self.locLabel = None
class CombinedImage:
    def __init__(self, imageOne, imageTwo, url, iconURL):
        self.imageOne = imageOne
        self.imageTwo = imageTwo
        self.imageURL = url
        self.iconURL = iconURL
