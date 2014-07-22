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
from mongoUtil import MongoUtil

def saveNoteAndPush(ps, note, message):
    token = ps.get('pushToken')
    MongoUtil.save('notes', note)
    if token:
        sendPush(token, message, {'noteID':str(note['_id'])}, ps.get('prodFlag'))


def sendPush(token, textInfo, dictInfo,sandBox, soundName='shot_new.caf'):
    print 'sandBox is:%s' % sandBox
    
    #'prod_push_cer.pem', 'prod_push_private_plain.pem'
    #'featheraz_cer.pem', 'featheraz_p12.pem'
    apns = None
    if sandBox == '0':
        apns = APNs(use_sandbox=True, cert_file='feather_cer.pem', key_file='feather_key_plain.pem')
    elif sandBox == '1':
        apns = APNs(use_sandbox=True, cert_file='featheraz_cer.pem', key_file='featheraz_p12.pem')
    else:
        apns = APNs(use_sandbox=False, cert_file='prod_push_cer.pem', key_file='prod_push_private_plain.pem')
    
    payload = Payload(alert=textInfo, sound=soundName, badge=1, custom = dictInfo)
    print 'before send push'
    
    def sendAsync(arg1, arg2):
        try:    
            apns.gateway_server.send_notification(token, payload)
        except:
            print 'error sending push'
        for (token_hex, fail_time) in apns.feedback_server.items():
            print '%r, %r' % (token_hex, fail_time)

        print "send a single success %r" % dictInfo
    #sendAsync(None, None)
    thread.start_new_thread(sendAsync, (None, None))
if __name__ == "__main__":
    #token_hex = '840cfa497609701e81c61249ca5d873c7f0180b7a03747ecfebead0309bed35e'
    #token_hex = '9dcd5e76457082acf22f51b96ba5baa7f9bd137602218f6bdbc0eb84ae369bca'    
    token_hex = 'f15a1aad893e08a10e4a965c120aca8e1b3264f21edadff79a0ccd64d0941683'    
    sendPush(token_hex, 'Hello baby', {'cool':'guy'}, '1')
    #MongoUtil.save('timeTest', {'createdTime':});
"""    
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