import subprocess
import tempfile
import urllib2
import hashlib
import os
from config import Config

#imageURLPrefix = "http://www.enjoyxue.com/static/%s"

#imageDirectory = "/home/ec2-user/handpa/static"

#Is this true
def executeCmd(cmd):
 print 'will execute:', cmd
 p = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)
 for line in p.stdout.readlines():
  print line,
 retval = p.wait()
 print 'final result:', retval
 return retval
 
def executeWithResult(cmd):
    print 'will execute:', cmd
    p = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)
    results = []    
    for line in p.stdout.readlines():
        results.append(line)
    retval = p.wait()
    resStr = ''.join(results)
    print 'final result:', retval, ",", resStr
    return (retval, resStr)

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

def parseSize(src):
    cmd = 'identify %s' % src
    (retval, res) = executeWithResult(cmd)
    if(retval == 0):
        items = res.split(' ')
        if(len(items) > 3):
            sizeStrs = items[2].split('x')
            #print 'size string:',items[2],",length:",len(sizeStrs),"x/y",int(sizeStrs[0]),int(sizeStrs[1])
            if(len(sizeStrs) == 2):
                return (1, int(sizeStrs[0]), int(sizeStrs[1]))
    return (0, 0, 0)

    
#I am actually a best crop.
#I want to resize the image just enough to crop the stem out. 
def resizeToSize(src, dest, destX, destY):
    (res, x, y) = parseSize(src)
    if res:
        ratioX = float(destX)/float(x)
        ratioY = float(destY)/float(y)
        finalRatio = max(ratioX, ratioY)
        finalX = max(finalRatio * x, destX)
        finalY = max(finalRatio * y, destY)
        print "ratioX:%f,y:%f, finalRatio:%f, x:%i, y:%i" % (ratioX, ratioY, finalRatio, x, y)
        cmd = 'convert %s -resize %ix%i %s' % (src, finalX, finalY, dest)
        executeCmd(cmd)
        cmd2 = 'convert %s -gravity center -crop %ix%i+0+0 %s' % (dest, destX, destY, dest)
        return executeCmd(cmd2)
    else:
        print 'Failed to collect image info from:', src
        return 0

def resizeImage(src, dest):
    cmd = 'convert %s -resize 2000x480 %s' % (src, dest)
    #if isIcon:
    #    cmd = 'convert %s -resize 2000x150 %s' % (src, dest)
    executeCmd(cmd)
    
    cmd2 = 'convert %s -gravity center -crop 320x480+0+0 %s' %(dest, dest)
    #if isIcon:
    #    cmd2 = 'convert %s -gravity center -crop 270x150+0+0 %s' %(dest, dest)
    return executeCmd(cmd2)

def combineImage(src1,src2,dest,iconFile):
 cmd = 'convert %s %s +append %s' % (src1, src2, dest)
 executeCmd(cmd)

 cmd1 = 'convert %s -gravity center -crop 540x300+0+0 %s' % (dest, iconFile)
 executeCmd(cmd1)

 #cmd2 = 'convert %s -bordercolor white -border 12x12 %s' % (iconFile, iconFile)
 #executeCmd(cmd2)
 
 #cmd3 = 'convert %s -bordercolor white -border 12x12 %s' % (dest, dest)
 #executeCmd(cmd3)     

def handleImageURL(src1, src2):
 """All the input are URL, this is right """
 dsrc1 = downloadImage(src1)
 dsrc2 = downloadImage(src2) 
 (dest,iconFile) = handleImage(dsrc1, dsrc2)
 fileName = dest.split('/')[-1]
 iconFileName = iconFile.split('/')[-1]
 cpCmd = 'mv %s %s/%s' % (dest, Config.imagePath, fileName)
 executeCmd(cpCmd)
 cpCmd = 'mv %s %s/%s' % (iconFile, Config.imagePath, iconFileName)
 executeCmd(cpCmd)
 finalURL = Config.imageURLPrefix % (fileName)
 iconURL = Config.imageURLPrefix % (iconFileName)
 return (finalURL, iconURL)

def handleImage(src1, src2):
 """This method will combine the 2 image into one"""
 tmp1 = getTmpFileName()
 tmp2 = getTmpFileName()
 dest = getTmpFileName()
 iconFile = getTmpFileName()
 resizeToSize(src1, tmp1, 320, 480)
 resizeToSize(src2, tmp2, 320, 480)
 combineImage(tmp1, tmp2, dest, iconFile)
 return (dest, iconFile)

if __name__ == "__main__":
    print "I am alright"
    print "downloaded image:%s, icon:%s" % handleImageURL("http://127.0.0.1:8080/static/IMG_0012.JPG", "http://127.0.0.1:8080/static/IMG_0493.JPG")
    #resizeToSize('static/IMG_0012.JPG', 'static/img800x200.jpg', 800, 200)     
    #print 'processed filename:', handleImage('~/Downloads/IMG_0735.JPG','~/Downloads/IMG_0734.JPG')
 #executeCmd('ls -ltr')
 #combineStr = '%s %i' % ('haha',1)
 #print 'combined str:', combineStr
