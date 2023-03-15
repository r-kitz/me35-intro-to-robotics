# pip install paho-mqtt

import paho.mqtt.client as mqtt # showing no paho...on wrong version of Python?
import time

bob = mqtt.Client('sample')

# Chris's IP: 10.245.148.227
#bob.connect('ip address')
bob.connect('10.247.25.221') # ip of broker (pc)
#bob.publish('topic name/subtest',"thing to publish")
# need same topic as Chris has running for my thing to show up in the console (will still return something in tracking but not publish thing)

# --- SUBSCRIBE ---
def what(who,user,message):
    print(message.payload.decode()) # .decode() to take away type of character (ASCII or binary)
    
# if get message from bob, callback
bob.on_message = what # no parentheses, just telling function to call upon callback
bob.loop_start() # buffers whatever comes in
bob.subscribe('angles') #class/#') # to get all messages from subtopics of larger 'class' topic
time.sleep(10000) # subscribes as long as sleeping
bob.loop_stop()
bob.disconnect()

# waiting for smeone to publish, as soon as someone says something, run callback -- until 10 seconds happened