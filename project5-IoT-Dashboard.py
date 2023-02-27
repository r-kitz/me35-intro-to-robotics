# All Python code written by my partner, Sloan Woodberry
# All MicroPython code written by me (Rose Kitz)
# check out my documentation to see my physical design:
# https://brawny-egret-76f.notion.site/5-IoT-Dashboard-971cbc07b5044d88a7a6f910da25fb13

import serial, random, time
import spotipy

from spotipy.oauth2 import SpotifyOAuth

s = serial.Serial('/dev/cu.usbmodem14201', baudrate=115200, timeout=10)
song_uri=''
CtrlC = '\x03'#abort
CtrlD = '\x04'#runs the code/ takes you out of code format
CtrlE = '\x05'#switches u to code download for mat
username = 'Username'
clientID = 'ClientID'
clientSecret = 'ClientSecret'
redirectURI = 'http://google.com'
scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=clientID,
                                                    client_secret=clientSecret,
                                                    redirect_uri=redirectURI,
                                                    scope=scope))

#doDisco
#--What it does--: 
#   *picks random disco song
#   *calculates beats per second
#   *make the servos move to the bpm (edit micropython in code1)
#   *opens the disco song in spotify player
def doDisco():#this will pick a random 
    mySong,bpm=randSong('spotify:playlist:6KHo6cTD1FKiSSNy9GZDGO')
    
    bps=bpm/60
    # map bps to time to sleep btwn servo setAngle's iteration on 1 degree later (less sleep for higher bps, more sleep for lower bps)
    # i.e. for 1 bps (60 bpm) turn 1 deg every 1/20 second, so wait 1/20 sec btwn angle changes
    # i.e. for 2 bps (120 bpm) turn 1 deg every 1/40 sec (based on testing for what looks like a good speed for each!)
    denom_factor = 10 # increase for faster servo (less sleep btwn angle changes), for faster bpm
    sleep_btwn_5deg =  1 / (denom_factor*bps) # calculate sleep inverse proportional to tempo of song to adjust speed of disco rotating!
    print(sleep_btwn_5deg)

    #edit this guy to edit the 2040's micropython
    code1 = '''
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
    
    while True:
        # after running servo for certain number of loops get error in motorController.py
        print("new while loop")
        for dir in range(2):
            # switch servo dirs b/c can't run in one dir past 200 deg
            # forward
            start = 0
            end = 200
            step = 5
            if dir == 1: # switch direction of servo on second loop to keep going forward/backward with controlled speed (vs. restarting at 0 every time, servo will move fast from 200 to 0)
                start = 200
                end = 0
                step = -5
                
            # servo seems to only set angles up to 200, then this loop brings it back to 0 fast so need decrement angle loop
            for i in range(start,end,step):  # Servo sweep from 0 position to 180 (trying step by 3 for smoother motion
                # Choose which of the servo connectors you want to use: servo1(default), servo2, servo3 or servo4
                for servo in servos:
                    reply = servo.setAngle(i)
                # increase sleep for slower bpm songs
                # decreases sleep (wait) for faster bpm songs
                time.sleep({})
                print(i)
            
        time.sleep_ms(200)
        board.ping()
        time.sleep_ms(50)
    '''.format(sleep_btwn_5deg)
    time.sleep(3)
    CtrlC = '\x03'#abort
    CtrlD = '\x04'#runs the code/ takes you out of code format
    CtrlE = '\x05'#switches you to code download for mat
    s.write(CtrlE.encode())
    code1 = code1.replace('\n','\r\n').encode()
    s.write(code1)
    s.write(CtrlD.encode())


    time.sleep(3)#added so rp2040 has sometime to start running the code

    s.close()
    sp.start_playback(uris=[mySong])#plays song on spotify



#doMetal
#--What it does--: 
#   *picks random metal song
#   *calculates beats per second
#   *make the servos move to the bpm (edit micropython in code1)
#   *opens the metal song in spotify player
def doMetal():
    mySong,bpm=randSong('spotify:playlist:7vuz2ExiHqp5wXdt5eNmiB')
    
    bps=bpm/60
    # map bps to time to sleep btwn servo setAngle's iteration on 1 degree later (less sleep for higher bps, more sleep for lower bps)
    # i.e. for 1 bps (60 bpm) turn 1 deg every 1/20 second, so wait 1/20 sec btwn angle changes
    # i.e. for 2 bps (120 bpm) turn 1 deg every 1/40 sec (based on testing for what looks like a good speed for each!)
    denom_factor = 10 # increase for faster servo (less sleep btwn angle changes), for faster bpm
    sleep_btwn_5deg =  1 / (denom_factor*bps) # calculate sleep inverse proportional to tempo of song to adjust speed of disco rotating!
    print(sleep_btwn_5deg)

    #code for rp2040
    code1 = '''
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
    
    while True:
        # after running servo for certain number of loops get error in motorController.py
        print("new while loop")
        for dir in range(2):
            # switch servo dirs b/c can't run in one dir past 200 deg
            # forward
            start = 0
            end = 200
            step = 5
            if dir == 1: # switch direction of servo on second loop to keep going forward/backward with controlled speed (vs. restarting at 0 every time, servo will move fast from 200 to 0)
                start = 200
                end = 0
                step = -5
                
            # servo seems to only set angles up to 200, then this loop brings it back to 0 fast so need decrement angle loop
            for i in range(start,end,step):  # Servo sweep from 0 position to 180 (trying step by 3 for smoother motion
                # Choose which of the servo connectors you want to use: servo1(default), servo2, servo3 or servo4
                for servo in servos:
                    reply = servo.setAngle(i)
                # increase sleep for slower bpm songs
                # decreases sleep (wait) for faster bpm songs
                time.sleep({})
                print(i)
            
        time.sleep_ms(200)
        board.ping()
        time.sleep_ms(50)
    '''.format(sleep_btwn_5deg)

    
    CtrlC = '\x03'#abort
    CtrlD = '\x04'#runs the code/ takes you out of code format
    CtrlE = '\x05'#switches you to code download for mat
    s.write(CtrlE.encode())
    code1 = code1.replace('\n','\r\n').encode()
    s.write(code1)
    s.write(CtrlD.encode())#runs servo code on 2040
    time.sleep(3)#added so rp2040 has sometime to start running the code

    s.close()
    sp.start_playback(uris=[mySong])#plays song on spotify

#randSong
#--What it does:
#     *picks random disco/metal song from input playlist
def randSong(playlist_uri):
    myPlaylist=sp.playlist(playlist_uri)
    songs=myPlaylist['tracks']['items']
    song_uris=[]
    for song in songs:
        song_uris.append(song['track']['uri'])

    chosen_song=song_uris[random.randint(0,len(song_uris)-1)]
    q=sp.audio_features(chosen_song)
    bpm=int(q[0]['tempo'])
    return chosen_song,bpm

#readButtons
#--What it does:
#     *takes in rp2040 port  (for us it's port 28 and 29))
#     *goes into to serial and reads that port 
#     *prints the reply from that port
#     *decides if set reply is high enough to be considered a press
def readButtons(music_type,port):
    isPressed=False
    code_initial='import machine\r\nbutton_{}=machine.ADC({})\r\n'.format(music_type, port)
    s.write(code_initial.encode())
    code2='button_{}.read_u16()\r\n'.format(music_type)
    s.write(code2.encode())
    time.sleep(.1)
    reply=s.read_all()

    reply=str(reply)
    if reply.find('.read_u16()')!=-1:
          isolate= reply.split('.read_u16()')
          isolate=isolate[1]
          isolate=isolate[4:-9]
          print(isolate)
          isolate=int(isolate)
          if isolate>3000:
               return True
          else:
               return False


waiting=True
while waiting:
    isDisco=readButtons('disco',29)
    isMetal= readButtons('metal',28)
    if isDisco:
        waiting=False
        print('Groovy Baby!')
        doDisco()
        
    if isMetal:
        waiting=False
        print('Hardcore Bro!')
        doMetal()
