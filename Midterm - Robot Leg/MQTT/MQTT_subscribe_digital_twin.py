# pip install paho-mqtt
# program to read the broker and continually update drawing of current leg position
# "digital twin" of my robot leg

import paho.mqtt.client as mqtt # showing no paho...on wrong version of Python?
import time
import numpy as np
from matplotlib import pyplot as plt
import math

bob = mqtt.Client('sample')

# Chris's IP: 10.245.148.227
#bob.connect('ip address')
bob.connect('10.247.25.221') # ip of broker (pc)
#bob.publish('topic name/subtest',"thing to publish")
# need same topic as Chris has running for my thing to show up in the console (will still return something in tracking but not publish thing)

def msg_to_floats_list(received_msg):
    # ways to parse strings
    # str_name[index] = element_at_this_index_of_str
    # str_name.split(separator,maxsplit) returns a list of strings split around the separator, split max number of times if specified -- default is as many times as separator occurs
    
    # start by taking off first and last index (to take away () from the string)
    msg_no_parens = received_msg[1:(len(received_msg) - 1)]
    msg_list = msg_no_parens.split(',')
    hip_theta = float(msg_list[0])
    knee_theta = float(msg_list[1])
    #thetas_list_floats = [hip_theta, knee_theta]
    
    return hip_theta, knee_theta

def thetas_to_xy_coords(hip_theta, knee_theta):
    
    # thigh is hip to knee, shin is knee to foot
    length_thigh = 7 # cm
    length_shin = 13 # cm
    
    num_decimals = 2
    
    # write not as loop for now just need to get the values I want b/c harder to think about w terms in lists of length 2 and IK is a bit diff for knee, foot
    knee_x = round(length_thigh * math.sin(math.radians(hip_theta + 90)), num_decimals)
    knee_y = round(length_thigh * math.cos(math.radians(hip_theta + 90)), num_decimals)
    
    x2 = length_shin * math.cos(math.radians(hip_theta + knee_theta))
    y2 = length_shin * math.sin(math.radians(hip_theta + knee_theta))
    
    foot_x = round(knee_x + x2, num_decimals)
    foot_y = round(knee_y - y2, num_decimals)
    
    coords = np.array([foot_x, foot_y, knee_x, knee_y]) # order foot first to match convention of code I wrote to create the animations so don't get coords flipped on accident
    
    # coords should have [[knee_x,knee_y], [foot_x,foot_y]]
    return coords

# function to set the plot characteristics for all arm position plots
def set_arm_subplot_params(ax): # set num_pos as -1 if not using within loop
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim((-20,20))
    ax.set_ylim((-17.4,1))
    ax.set_xlabel('X-Position (cm)')
    ax.set_ylabel('Y-Position (cm)')
    
def make_plot_leg_pos(coords):
    fig, axis = plt.subplots(1,1)
    # data = [foot_pos, knee_pos, shoulder_pos]
    # all shoulder positions are the same (x,y) = (0,0), I set as datum and shoulder is stationary
    x = np.array([coords[0],coords[2],0])
    y = np.array([coords[1],coords[3],0])
    
    axis.plot(x,y)
    set_arm_subplot_params(axis)
    
start = True
start_time = 0

# --- SUBSCRIBE ---
def what(who,user,message):
    msg = message.payload.decode()
    # could program to detect time btwn messages but also can just hardcode the same in here as in the publisher
    #print("message is", msg, "as type", type(msg)) # .decode() to take away type of character (ASCII or binary)
    # msg = '(theta_hip,theta_knee)'
    # assuming message comes as a string, and I sent it from subscriber as a string to SPIKE and the SPIKE can parse the string
    theta_hip, theta_knee = msg_to_floats_list(msg)
    coordinates = thetas_to_xy_coords(theta_hip, theta_knee)
    make_plot_leg_pos(coordinates)
    
    plt.show(block=False)
    plt.pause(.25)
    plt.close()
    #plt.pause(1)
    
    
    
# if get message from bob, callback
bob.on_message = what # no parentheses, just telling function to call upon callback
bob.loop_start() # buffers whatever comes in
bob.subscribe('angles')
print("[foot_x, foot_y, knee_x, knee_y]")
time.sleep(3000)
# can put the stuff I want to happen in this time in the what() function!

bob.loop_stop()
bob.disconnect()

# waiting for smeone to publish, as soon as someone says something, run callback -- until 10 seconds happened
# returned from Antonio: "b'Antonio'" (b stands for binary)


# NEXT
# modify msg in what() function to break down into angles and then post to animation or new figure of digital twin