from threading import Thread
from time import sleep

def coolmethod():
   sleep(2)
   print "i am another thread"

def multiReturn():
  return ('haha','hehe')  

thread = Thread(target = coolmethod)
#thread.start()
print "completed"
#sleep(3)

(res1, res2) = multiReturn()
print "first:",res1,",second:",res2
