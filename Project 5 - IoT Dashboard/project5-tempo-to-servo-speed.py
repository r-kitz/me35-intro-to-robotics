import time
from motorController import *
    
board = NanoMotorBoard()
print("reboot")
board.reboot()
time.sleep_ms(500)
    
servos = []
    
for i in range(4):
    servos.append(Servo(i))
        
    # reset all servos to 0
for servo in servos:
    reply = servo.setAngle(0)
    
while True:# after running servo for certain number of loops get error in motorController.py
    print("new while loop")
    for dir in range(2):# switch servo dirs b/c can't run in one dir past 200 deg# forward
        start = 0
        end = 200
        step = 5
        if dir == 1: # switch direction of servo on second loop to keep going forward/backward with controlled speed (vs. restarting at 0 every time, servo will move fast from 200 to 0)
            start = 200
            end = 0
            step = -5# servo seems to only set angles up to 200, then this loop brings it back to 0 fast so need decrement angle loop
            for i in range(start,end,step):  # Servo sweep from 0 position to 180 (trying step by 3 for smoother motion
                # Choose which of the servo connectors you want to use: servo1(default), servo2, servo3 or servo4
                for servo in servos:
                    reply = servo.setAngle(i)
                # increase sleep for slower bpm songs
                # decreases sleep (wait) for faster bpm songs
                time.sleep(sleep_btwn_5deg)
                print(i)
    time.sleep_ms(200)
    board.ping()
    time.sleep_ms(50)
