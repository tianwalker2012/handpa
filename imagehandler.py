import subprocess
import tempfile
import urllib2
import hashlib
import os

imageURLPrefix = "http://www.enjoyxue.com/static/%s"

imageDirectory = "/home/ec2-user/handpa/static"

def executeCmd(cmd):
 print 'will execute:', cmd
 p = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)
 for line in p.stdout.readlines():
  print line,
 retval = p.wait()
 print 'final result:', retval
 return retval

def getTmpFileName():
 pf = 'handpa_tmp'
 tf1 = tempfile.NamedTemporaryFile(prefix=pf)
 res = '%s.JPG' % tf1.name
 tf1.close()
 return res

#TODO in this method, the path may coincide with the existing one. 
#how to avoid this this?
#Use a tempoary file name to achieve this.
def downloadImage(url):
 """Will download files to the specified directory"""
 #I made an assumption that the url will have a file name.
 dirs = "./downloaded"
 #the the post fix
 file_pix = url.split('.')[-1];
 hashstr = hashlib.md5(url).hexdigest()
 fullpath = dirs + "/" + hashstr + ".jpg"
 print "full path:", fullpath
 #imageFile = urllib2.urlopen(url)
 if os.path.exists(fullpath):
  return fullpath
 imageFile = urllib2.urlopen(url)
 output = open(fullpath, 'wb')
 output.write(imageFile.read())
 output.close()
 return fullpath


def resizeImage(src, dest, isIcon):
    cmd = 'convert %s -resize 2000x480 %s' % (src, dest)
    if isIcon:
        cmd = 'convert %s -resize 2000x150 %s' % (src, dest)
    executeCmd(cmd)
    
    cmd2 = 'convert %s -gravity center -crop 320x480+0+0 %s' %(dest, dest)
    if isIcon:
        cmd2 = 'convert %s -gravity center -crop 270x150+0+0 %s' %(dest, dest)
    return executeCmd(cmd2)

def combineImage(src1,src2,dest):
 cmd = 'convert %s %s +append %s' % (src1, src2, dest)
 executeCmd(cmd)
 cmd = 'convert %s -bordercolor white -border 12x12 %s' % (dest, dest)
 executeCmd(cmd)


def handleImageURL(src1, src2, isIcon):
 """All the input are URL, this is right """
 dsrc1 = downloadImage(src1)
 dsrc2 = downloadImage(src2) 
 dest = handleImage(dsrc1, dsrc2, isIcon)
 fileName = dest.split('/')[-1]
 cpCmd = 'mv %s %s/%s' % (dest, imageDirectory, fileName)
 executeCmd(cpCmd)
 finalURL = imageURLPrefix % (fileName)
 return finalURL

def handleImage(src1, src2, isIcon):
 """This method will combine the 2 image into one"""
 tmp1 = getTmpFileName()
 tmp2 = getTmpFileName()
 dest = getTmpFileName()
 resizeImage(src1, tmp1, isIcon)
 resizeImage(src2, tmp2, isIcon)
 combineImage(tmp1, tmp2, dest)
 return dest

if __name__ == "__main__":
    print "I am alright"
 #import sys
 #print "downloaded:", handleImageURL("http://127.0.0.1:8080/static/IMG_0012.JPG", "http://127.0.0.1:8080/static/IMG_0493.JPG", true)
 #print 'processed filename:', handleImage('~/Downloads/IMG_0735.JPG','~/Downloads/IMG_0734.JPG')
 #executeCmd('ls -ltr')
 #combineStr = '%s %i' % ('haha',1)
 #print 'combined str:', combineStr
