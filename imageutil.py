# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 13:58:00 2014

@author: apple
"""
import PIL
from PIL import Image
import os
import sys
import web
class ImageUtil:
    
    @classmethod
    def changeName(self, filename, affix):
        fileParts = filename.split('.')
        middle = fileParts[:-1]
        postFix = fileParts[-1]
        fullPath = '%s%s.%s' % (middle,affix,postFix)
        return fullPath

    @classmethod
    def resize(self, filename, basewidth, affix):
            img = Image.open(filename)
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
            filePaths = filename.replace('\\','/').split('/')
            filePath = filePaths[-1]
            fileParts = filePath.split('.')
            
            middle = fileParts[-2]
            postFix = fileParts[-1]
            fullPath = '%s/%s%s.%s' % ('/'.join(filePaths[:-1]),middle,affix,postFix) 
            web.debug('fileParts %s, fileName %s, fullPath:%s' % (fileParts,filename, fullPath))
            img.save(fullPath)
            return fullPath


if __name__ == "__main__":
    paths = sys.argv[1:]
    for fileName in paths:
    #current_file = os.path.join(path, file)
        print 'processed %s', ImageUtil.resize(fileName, 60, 'tb')
#print ImageUtil.resize('/Users/apple/image_py.jpg', 60, 'cool')


