#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 16:22:01 2014

@auther: Xie Tian
"""

import time
from apns import APNs, Payload
import simplejson
import sys
import thread

def sendPush(token, textInfo, dictInfo,sandBox = True):
    print 'sandBox is:%i' % sandBox
    
    apns = APNs(use_sandbox=sandBox, cert_file='feather_cer.pem' if sandBox else 'feather_cer_prod.pem' , key_file='feather_key_plain.pem' if sandBox else 'feather_key_plain_prod.pem')
    payload = Payload(alert=textInfo, sound="default", badge=1, custom = dictInfo)
    print 'before send push'
    
    def sendAsync(arg1, arg2):
        try:    
            apns.gateway_server.send_notification(token, payload)
        except:
            print 'error sending push: %r' % sys.exc_info()
        for (token_hex, fail_time) in apns.feedback_server.items():
            print '%r, %r' % (token_hex, fail_time)

        print "send a single success %r" % dictInfo

    thread.start_new_thread(sendAsync, (None, None))
if __name__ == "__main__":
    apns = APNs(use_sandbox=True, cert_file='feather_cer.pem', key_file='feather_key_plain.pem')
    print "will send request"
    # Send a notification
    token_hex = '840cfa497609701e81c61249ca5d873c7f0180b7a03747ecfebead0309bed35e'
    realInfo = simplejson.dumps({"haha":"cool"})
    #print 'payload file:%s' % apns.__file__ 
    payload = Payload(alert="Hello World!", sound="default", badge=1, custom = {"haha":"cool"})
    apns.gateway_server.send_notification(token_hex, payload)

    for (token_hex, fail_time) in apns.feedback_server.items():
        print '%r, %r' % (token_hex, fail_time)

    print "send a single success"
    # Send multiple notifications in a single transmission
"""  
    frame = Frame()
    identifier = 1
    expiry = time.time()+3600
    priority = 10
    frame.add_item(token_hex, payload, identifier, expiry, priority)
    apns.gateway_server.send_notification_multiple(frame)

# Get feedback messages
    for (token_hex, fail_time) in apns.feedback_server.items():
        print '%r, %r' % (token_hex, fail_time)
"""