# pip install paho-mqtt

import paho.mqtt.client as mqtt
import time
import numpy as np # for loading CSV, make all data structures np arrays for uniformity??? or lists if convenient...

'''
from midterm_path_v3.py (code to plan path and create diagrams/animations)
import math
import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from collections import deque # for animation trace
'''

# path to CSV of theta_hip, theta_knee (assuming + = clockwise direction of motors) -- need the 'r' before the string of the path for unicode to decode the path, for some reason
# r"C:\Users\rckch\Downloads\me35_midterm_motorthetas.csv"

# function to read in txt (CSV) file of motor thetas and get numpy arrays with each column
def read_thetas(filename):
    #thetas = pd.read_csv(filename)
    thetas = np.loadtxt(filename, dtype=float, skiprows=1, delimiter=',') # skip header row w column names (theta_hip, theta_knee)
    # each row/outer index is an overall arm position/point in time,
    # inner values are [finger_x, finger_y, elbow_x, elbow_y]
    thetas_hip = thetas[:,0]
    thetas_knee = thetas[:,1]
    return thetas, thetas_hip, thetas_knee

# function to connect my client to the external broker at the given IP address
def start_connection_to_broker(client, ip):
    # connect my driver code to the computer running the MQTT broker I will send info to
    client.connect(ip)
    
# function to convert imported list of theta_hip, theta_knee to proper format (tuple of floats -- within string) to send to SPIKE
# SPIKE takes desired angle as FLOAT, then does a proportional controller and takes the integer of the result
def make_thetas_tuple_as_strings(thetas):
    # thetas in degrees
    # message list format: angles = ('(hip1,knee1)', '(hip2,knee2)', ...)
    thetas_strs = ['(0,0)'] # initialize as list...need to convert to tuple to send to Chris so np array doesn't make sense...
    
    # loop through each overall position (each pt in time) to convert each set of angles as (hip_angle, knee_angle) to str
    # ('hardcode in' from CSV based on found angles from IK calculations)
    for position in thetas:
        this_hip_theta = position[0] - 90
        this_knee_theta = position[1]
        
        # for Chris' set-up had to flip knee to first and upper(hip) to second
        this_position_as_str = '(' + str(this_hip_theta) + ',' + str(this_knee_theta)  + ')'
        thetas_strs.append(this_position_as_str)
    
    # convert list of thetas as strs to an outer tuple (format Chris wants, so can't change these values in this container once sent!)
    tuple_thetas_strs = tuple(thetas_strs)
    
    return tuple_thetas_strs
        
# function to publish list of messages to a given topic from my client at a set amount of time between messages
def send_thetas_to_broker(client, topic, thetas_tuple_to_send):
    
    # initialize as default string before putting in angles later
    message = '(0,0)' 

    wait_btwn_thetas = .5 # seconds
    # --- PUBLISH ---
    # send message to broker 3 times
    for pair in thetas_tuple_to_send: # ??? for-each ok? or do regular for loop if need index...
        #george.publish('topic name/subtest',"message to publish")
        message = pair
        #print("Sending: ", message, "as type", type(message), "to topic", topic)
        client.publish(topic, message)
        time.sleep(wait_btwn_thetas)
        
# function to stop my client's connection to the external broker (should do at end of code so not still running!)
def stop_connection(client):
    # disconnect the client
    client.disconnect()
    
def main():
    
    # QUESTION: is it ok to establish main variables here so can use 'globally' inside main? and if so should they all be at top of main() function or only right before needed?
    # or should I initialize them actually globally, or inside a function then pass them around?
    # i.e. just a function to initialize variables?
    george = mqtt.Client('dskfl;a')
    broker_ip = '10.245.155.186'
    # need same topic as Chris has running for my thing to show up in the console (will still return something in tracking but not publish thing)
    topic_publish_to = 'angles' # topic that broker is listening (subscribing) to; include subtopic (i.e. listen) if existent after topic (i.e. ESP)
    
    
    # QUESTION: should I set a variable equal to this then put inside the () or is this most efficient (seems quicker for code)?
    motor_thetas, motor_thetas_hip, motor_thetas_knee = read_thetas(r'C:\Users\rckch\Downloads\me35_midterm_motorthetas.csv') # need the r before the path string for unicode to decode
    
    start_connection_to_broker(george, broker_ip)
    
    thetas_to_send = make_thetas_tuple_as_strings(motor_thetas)
    
    # QUESTION: is it nicer to pass in theta_hip and theta_knee separately (so do the division stuff in read_thetas, or just do it here so only have to pass in thetas?
    send_thetas_to_broker(george, topic_publish_to, thetas_to_send)
    
    stop_connection(george)
    
    #print(thetas_to_send) -- to check that thetas I am publishing are proper format and in proper order
    
main()
               
               


