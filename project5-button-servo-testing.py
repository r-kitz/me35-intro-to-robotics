import time
from motorController import *
from machine import Pin, Timer, I2C
from MC_Consts import *

# check battery: print('Battery: %0.1f' % board.battery(1))

board = NanoMotorBoard()
print("reboot")
board.reboot()
time.sleep_ms(500)

servo = Servo(0)


# A3 = machine 29
# A2 = machine 28
button_black = machine.ADC(28)
button_purple = machine.ADC(29)

button_pressed_min = 30000

#button_count = 0
#button_was_pressed = False

'''
current_angle = 0

def set_servo(angle):
    servo.setAngle(angle)
    
    global current_angle
    current_angle = angle
'''
    
def get_button(button_name):
    button_current = button_name.read_u16()
    #print("button value:", button_current)
    return button_current
    
# function to call spotify action for left button press
def black_button_pressed():
    print("black button pressed")
    
# function to call spotify action for right button press
def purple_button_pressed():
    print("purple button pressed")

def test_buttons(): # should I add press and release?
    button_black_current = get_button(button_black)
    button_purple_current = get_button(button_purple)
    
    if button_black_current > button_pressed_min:
        black_button_pressed()
    elif button_purple_current > button_pressed_min:
        purple_button_pressed()
    else:
        print("none")
    
    time.sleep_ms(500)
    
def test_servo():
    for i in range(20):
        servo.setAngle(
    
while True:
    test_buttons() # working
    #test_servo() # servo ran once, not anymore...check back notes from meeting w Chris need even higher resistors on button? check currenta across button when pressed w multimeter, check voltage/current to motor
