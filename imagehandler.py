import subprocess
import tempfile

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

def resizeImage(src, dest):
 cmd = 'convert %s -resize 2000x480 %s' % (src, dest)
 executeCmd(cmd)
 cmd2 = 'convert %s -gravity center -crop 320x480+0+0 %s' %(dest, dest)
 return executeCmd(cmd2)

def combineImage(src1,src2,dest):
 cmd = 'convert %s %s +append %s' % (src1, src2, dest)
 executeCmd(cmd)
 cmd = 'convert %s -bordercolor white -border 6x6 %s' % (dest, dest)
 executeCmd(cmd)
  

def handleImage(src1, src2):
 """This method will combine the 2 image into one"""
 tmp1 = getTmpFileName()
 tmp2 = getTmpFileName()
 dest = getTmpFileName()
 resizeImage(src1, tmp1)
 resizeImage(src2, tmp2)
 combineImage(tmp1, tmp2, dest)
 return dest

print 'processed filename:', handleImage('~/Downloads/IMG_0735.JPG','~/Downloads/IMG_0734.JPG')
#executeCmd('ls -ltr')
#combineStr = '%s %i' % ('haha',1)
#print 'combined str:', combineStr
