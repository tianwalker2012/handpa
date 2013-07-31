# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 22:52:53 2013

@author: apple
"""
from datetime import datetime 

class Image:
    def __init__(self):
        self.author = None
        self.created_at = datetime.now()
        self.url = ''
        self.longitude = 0.0
        self.latitude = 0.0
        self.locLabel = None

class CombinedImage:
    def __init__(self, imageOne, imageTwo):
        self.imageOne = imageOne
        self.imageTwo = imageTwo
