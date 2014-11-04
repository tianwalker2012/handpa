# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 13:58:00 2014

@author: apple
"""

try:
    import PIL
    from PIL import Image
except ImportError:
    import Image

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
    def resizeAndCrop(self, img_path, size, affix, crop_type='middle'):
        # If height is higher we resize vertically, if not we resize horizontally
        img = Image.open(img_path)
        # Get current and desired ratio for the images
        img_ratio = img.size[0] / float(img.size[1])
        ratio = size[0] / float(size[1])
        #The image is scaled/cropped vertically or horizontally depending on the ratio
        if ratio > img_ratio:
            img = img.resize((size[0], size[0] * img.size[1] / img.size[0]),Image.ANTIALIAS)
                # Crop in the top, middle or bottom
            if crop_type == 'top':
                box = (0, 0, img.size[0], size[1])
            elif crop_type == 'middle':
                box = (0, (img.size[1] - size[1]) / 2, img.size[0], (img.size[1] + size[1]) / 2)
            elif crop_type == 'bottom':
                box = (0, img.size[1] - size[1], img.size[0], img.size[1])
            else :
                raise ValueError('ERROR: invalid value for crop_type')
            img = img.crop(box)
        elif ratio < img_ratio:
            img = img.resize((size[1] * img.size[0] / img.size[1], size[1]),Image.ANTIALIAS)
            # Crop in the top, middle or bottom
            if crop_type == 'top':
                box = (0, 0, size[0], img.size[1])
            elif crop_type == 'middle':
                box = ((img.size[0] - size[0]) / 2, 0, (img.size[0] + size[0]) / 2, img.size[1])
            elif crop_type == 'bottom':
                box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
            else :
                raise ValueError('ERROR: invalid value for crop_type')
            img = img.crop(box)
        else :
            img = img.resize((size[0], size[1]),Image.ANTIALIAS)
        # If the scale is the same, we do not need to crop
        filePaths = img_path.replace('\\','/').split('/')
        filePath = filePaths[-1]
        fileParts = filePath.split('.')
        middle = fileParts[-2]
        postFix = fileParts[-1]
        fullPath = '%s/%s%s.%s' % ('/'.join(filePaths[:-1]),middle,affix,postFix) 
        web.debug('fileParts %s, fileName %s, fullPath:%s' % (fileParts,img_path, fullPath))
        img.save(fullPath)
        #img.save(modified_path)

    @classmethod
    def resize(self, filename, basewidth, affix, isSquare=False):
            img = Image.open(filename)
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            web.debug('image size:%i, org:%i, %s' % (hsize, img.size[1], filename))
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


