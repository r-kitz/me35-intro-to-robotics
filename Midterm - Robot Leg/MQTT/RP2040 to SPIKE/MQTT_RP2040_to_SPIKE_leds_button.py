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
button = machine.Pin(12, mode=Pin.IN, pull=Pin.PULL_UP)
# press button to start one instance of publishing (one time through leg swing of all angles)

led_red = Pin(25, mode=Pin.OUT) # mainly disconnected
led_green = Pin(13, mode=Pin.OUT) # mainly connected to mqtt
led_yellow = Pin(15, mode=Pin.OUT) # mainly something was published

mqtt_CBR.connect_wifi(wifi)
blink_led(led_green,0.5)

fred = mqtt_CBR.mqtt_client(client_id, mqtt_broker, whenCalled)
turn_on_led(led_green)
#fred.subscribe(topic_sub)

# function to turn on red led to indicate that main.py is running
def turn_on_led(pin):
    pin.on()
    
# function to turn off the main led when main is done running (for now should only run through angles once instead of while True)
def turn_off_led(pin):
    pin.off()

# function to blink LED on a pin on/off with inputted delay
def blink_led(pin,delay):
    pin.on()
    time.sleep(delay)
    pin.off()

# provided blink function to blink the built-in board LED
def blink(delay = 0.1):
    led.on()
    time.sleep(delay)
    led.off()

# function to return current state of button (pressed or not)
def get_button():
    return button.value()
    # 1 is not pressed
    # 0 is pressed
    
# function to publish (0,0) position to broker so subscribed SPIKE resets position to (0,0)
def send_reset_pos():
    fred.publish(topic_pub, '(0,0)')
    
# function to setup client to decode received messages and topics if subscribing, and blink on-board LED when this happens
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
    thetas_strs = ['(0,0)'] # initialize as list...need to convert to tuple to send to Chris so np array doesn't make sense...
    
    # CONFIRM SENDING FORMAT (TUPLE, STRS INSIDE) w Chris
    
    # loop through each overall position (each pt in time) to convert each set of angles as (hip_angle, knee_angle) to str
    # ('hardcode in' from CSV based on found angles from IK calculations)
    for position in list_thetas:
        this_hip_theta = position[0] - 90 # subtract from all b/c absolute angles, not relative to each other
        this_knee_theta = position[1]
        
        this_position_as_str = '(' + str(this_hip_theta) + ',' + str(this_knee_theta) + ')'
        thetas_strs.append(this_position_as_str)
    
    # convert list of thetas as strs to an outer tuple (format Chris wants, so can't change these values in this container once sent!)
    tuple_thetas_strs = tuple(thetas_strs)
    
    return tuple_thetas_strs
    
# function to light up red, yellow, and green LEDs separately in order then all at same time
# to emulate a "ready, set, go" sequence to show when the main.py code starts up automatically on the board as soon as it receives power
# so you can expect to be able to press the button to start the publishing and see the other LEDs react individually (using other functions outside of this one) based on what is happening in the code
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
    
def turn_off_all_leds():
    turn_off_led(led_red)
    turn_off_led(led_yellow)
    turn_off_led(led_green) # turn off all leds upon stop
        
def main():
    stoplight_to_start()
    
    angles = thetas.thetas
    
    angles_str_tuples = make_thetas_tuple_as_strings(angles)
    #print(angles_str_tuples)
    
    tot_hip_angle = 0
    tot_knee_angle = 0
    
    time_btwn_sends = 0.25 # seconds

    button_held = False
    while True:
        try:
            fred.check()
            # if button is pressed and wasn't held before
            if get_button() == 0 and not button_held:
                print('button')
                for i in range(len(angles_str_tuples)):
                    #tot_hip_angle += list_rel_angles[i][0]
                    #tot_knee_angle += list_rel_angles[i][1]
                    #print("tot hip:", tot_hip_angle)
                    #print("tot knee:", tot_knee_angle)
                    
                    msg = angles_str_tuples[i]
                    print(msg)
                    fred.publish(topic_pub, msg)
                    turn_on_led(led_yellow)
                    time.sleep(time_btwn_sends/2)
                    turn_off_led(led_yellow)
                    time.sleep(time_btwn_sends/2)
                    #blink()
                    
                send_reset_pos() # automatically reset position after finishing going through thetas
                button_held = True
            elif get_button() == 1:
                button_held = False # if button not pressed
            # if button is pressed but button_held is still true, nothing happens
            # code doesn't move on after going through while once until release button
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

turn_off_all_leds() # just in case LED are left on during code (i.e. if main() is exited), before code terminates