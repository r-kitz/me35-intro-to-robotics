# pip install paho-mqtt
# program to read the broker and continually update drawing of current leg position
# "digital twin" of my robot leg

import paho.mqtt.client as mqtt # showing no paho...on wrong version of Python?
import time

bob = mqtt.Client('sample')

# Chris's IP: 10.245.148.227
#bob.connect('ip address')
bob.connect('10.247.25.221') # ip of broker (pc)
#bob.publish('topic name/subtest',"thing to publish")
# need same topic as Chris has running for my thing to show up in the console (will still return something in tracking but not publish thing)

def msg_to_floats(received_msg):
    # ways to parse strings
    # str_name[index] = element_at_this_index_of_str
    # str_name.split(separator,maxsplit) returns a list of strings split around the separator, split max number of times if specified -- default is as many times as separator occurs
    
    # start by taking off first and last index (to take away () from the string)
    msg_no_parens = received_msg[1:(len(received_msg) - 1)]
    msg_list = msg_no_parens.split(',')
    hip_theta = float(msg_list[0])
    knee_theta = float(msg_list[1])
    
    return hip_theta, knee_theta

# --- SUBSCRIBE ---
def what(who,user,message):
    msg = message.payload.decode()
    print("message is", msg, "as type", type(msg)) # .decode() to take away type of character (ASCII or binary)
    # msg = '(theta_hip,theta_knee)'
    # assuming message comes as a string, and I sent it from subscriber as a string to SPIKE and the SPIKE can parse the string
    theta_hip, theta_knee = msg_to_floats(msg)
    print("hip theta is", theta_hip, "as type", type(theta_hip))
    print("knee theta is", theta_knee, "as type", type(theta_knee))
    
    
# if get message from bob, callback
bob.on_message = what # no parentheses, just telling function to call upon callback
bob.loop_start() # buffers whatever comes in
bob.subscribe('angles')
# rather than just have a sleep statement to receive the messages from the broker, I need a loop that still sleeps for enough time, but can also do stuff while I'm waiting until I need to disconnect from the client
time.sleep(3000)
# can put the stuff I want to happen in this time in the what() function!

bob.loop_stop()
bob.disconnect()

# waiting for smeone to publish, as soon as someone says something, run callback -- until 10 seconds happened
# returned from Antonio: "b'Antonio'" (b stands for binary)


# NEXT
# modify msg in what() function to break down into angles and then post to animation or new figure of digital twin