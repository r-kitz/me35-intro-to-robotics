import time
import machine

from secrets import tufts_eecs as wifi
import mqtt_CBR
from thetas import thetas

mqtt_broker = '10.247.25.221' # my pc ip address
#topic_sub = 'ESP/tell'
topic_pub = 'angles'
client_id = 'roserp2040'

mqtt_CBR.connect_wifi(wifi)
led = machine.Pin(6, machine.Pin.OUT)  

def blink(delay = 0.1):
    led.on()
    time.sleep(delay)
    led.off()
    
def whenCalled(topic, msg):
    print((topic.decode(), msg.decode()))
    blink()
    time.sleep(0.5)
    blink()
    
    
# function to convert imported list of theta_hip, theta_knee to proper format to send to SPIKE
# (originally wrote for midterm_PC_to_spike.py for 7/10 version)
# SPIKE takes desired angle as FLOAT, then does a proportional controller and takes the integer of the result
def make_thetas_tuple_as_strings(list_thetas):
    # thetas in degrees
    # message list format: angles = ('(hip1,knee1)', '(hip2,knee2)', ...)
    thetas_strs = [] # initialize as list...need to convert to tuple to send to Chris so np array doesn't make sense...
    
    # CONFIRM SENDING FORMAT (TUPLE, STRS INSIDE) w Chris
    
    # loop through each overall position (each pt in time) to convert each set of angles as (hip_angle, knee_angle) to str
    # ('hardcode in' from CSV based on found angles from IK calculations)
    for position in list_thetas:
        this_hip_theta = position[0]
        this_knee_theta = position[1]
        
        this_position_as_str = '(' + str(this_hip_theta) + ',' + str(this_knee_theta) + ')'
        thetas_strs.append(this_position_as_str)
    
    # convert list of thetas as strs to an outer tuple (format Chris wants, so can't change these values in this container once sent!)
    tuple_thetas_strs = tuple(thetas_strs)
    
    return tuple_thetas_strs
        
def main():
    angles = thetas.thetas
    angles_str_tuples = make_thetas_tuple_as_strings(angles)
    
    
    fred = mqtt_CBR.mqtt_client(client_id, mqtt_broker, whenCalled)
    #fred.subscribe(topic_sub)

    old = 0
    i = 0
    while True:
        try:
            fred.check()
            time_btwn_sends = 0.25 # seconds
            for i in range(len(angles_str_tuples)):
                msg = angles_str_tuples[i]
                fred.publish(topic_pub, msg)
                time.sleep(time_btwn_sends)
                blink()
        except OSError as e:
            print(e)
            fred.connect()
        except KeyboardInterrupt as e:
            fred.disconnect()
            print('done')
            break
            
    
main()