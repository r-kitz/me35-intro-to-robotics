import time
import machine
from machine import Pin

from secrets import tufts_eecs as wifi
import mqtt_CBR
from thetas import thetas

mqtt_broker = '10.247.25.221' # my pc ip address
#topic_sub = 'ESP/tell'
topic_pub = 'angles'
client_id = 'roserp2040'

led = machine.Pin(6, machine.Pin.OUT)

led_red = Pin(25, mode=Pin.OUT) # mainly disconnected
led_green = Pin(13, mode=Pin.OUT) # mainly connected to mqtt
led_yellow = Pin(15, mode=Pin.OUT) # mainly something was published

# function to turn on red led to indicate that main.py is running
def turn_on_led(pin):
    pin.on()
    
# function to turn off the main led when main is done running (for now should only run through angles once instead of while True)
def turn_off_led(pin):
    pin.off()

def blink_led(pin,delay):
    pin.on()
    time.sleep(delay)
    pin.off()

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
    
def get_rel_angles(angles_list):
    tot_hip = 0
    tot_knee = 0
    
    rel_angles_list = [[0,0]]
    
    for i in range(len(angles_list)):
        this_hip = angles_list[i][0]
        this_knee = angles_list[i][1]
        last_hip, last_knee = 0, 0 # initialize
        if i > 0: # don't access previous index for start b/c can't
            last_hip = angles_list[i-1][0]
            last_knee = angles_list[i-1][1]
        
        rel_hip = this_hip - last_hip
        rel_knee = this_knee - last_knee
        # add relative angles to turn to list to later convert to tuples
        rel_angles_list.append([rel_hip, rel_knee])
        
        tot_hip += rel_hip
        tot_knee += rel_knee
        
        
    return rel_angles_list
    
def stoplight_to_start():
    turn_on_led(led_red)
    time.sleep(.5)
    turn_off_led(led_red)
    turn_on_led(led_yellow)
    time.sleep(.5)
    turn_off_led(led_yellow)
    turn_on_led(led_green)
    time.sleep(.5)
    turn_off_led(led_green)
    time.sleep(0.01)
    turn_on_led(led_red)
    turn_on_led(led_yellow)
    turn_on_led(led_green)
    time.sleep(0.5)
    turn_off_led(led_red)
    turn_off_led(led_yellow)
    turn_off_led(led_green)
    
mqtt_CBR.connect_wifi(wifi)
blink_led(led_green,0.5)
        
def main():
    stoplight_to_start()
    
    angles = thetas.thetas
    list_rel_angles = get_rel_angles(angles) # need to convert absolute angles to relative so the motor only changes position by what is necessary to reach the overall desired angle
    
    angles_str_tuples = make_thetas_tuple_as_strings(list_rel_angles)
    #print(angles_str_tuples)
    
    fred = mqtt_CBR.mqtt_client(client_id, mqtt_broker, whenCalled)
    turn_on_led(led_green)
    #fred.subscribe(topic_sub)
    
    tot_hip_angle = 0
    tot_knee_angle = 0
    
    time_btwn_sends = 0.25 # seconds

    while True:
        try:
            fred.check()
            
            for i in range(len(angles_str_tuples)):
                #tot_hip_angle += list_rel_angles[i][0]
                #tot_knee_angle += list_rel_angles[i][1]
                #print("tot hip:", tot_hip_angle)
                #print("tot knee:", tot_knee_angle)
                
                msg = angles_str_tuples[i]
                fred.publish(topic_pub, msg)
                turn_on_led(led_yellow)
                time.sleep(time_btwn_sends/2)
                turn_off_led(led_yellow)
                time.sleep(time_btwn_sends/2)
                #blink()
        except OSError as e:
            print(e)
            fred.connect()
        except KeyboardInterrupt as e:
            fred.disconnect()
            turn_off_led(led_green)
            blink_led(led_red,0.5)
            print('done')
            break

        time.sleep(1)
    
main()
turn_off_led(led_red)
turn_off_led(led_yellow)
turn_off_led(led_green) # turn off all leds upon stop