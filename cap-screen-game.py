# Sample program for capturing image frames + key presses from a game window
# Outputs are JPEG images and CSV files

# Import libraries:
import numpy as np
import cv2
from mss import mss
import time
import datetime
import os
from xdo import Xdo
from pynput.keyboard import Key
import pygame
import sys

# Library initialization
xdo = Xdo()
pygame.init()
sct = mss()

# Screen Settings:
display_width = 640
display_height = 400

# General variables:
record = False
win_name = "GAMEWINDOWNAME"
cords = {'top':70 , 'left': 5 , 'width': display_width, 'height': display_height }
button_delay = 0.2
dir_name = ""
sample_count = 0

# Get window for capturing sample
print(len(xdo.search_windows(win_name.encode())))
win_id = xdo.search_windows(win_name.encode())[0]
print("WIN ID:" + str(win_id))

# Initialize display for monitoring
gameDisplay = pygame.display.set_mode((int(display_width/4),int(display_height/4)))
pygame.display.set_caption('Training')

# Key mappings
joy_keys = []
joy_keys.append(0)#accel
joy_keys.append(0)#break
joy_keys.append(0)#shoot
joy_keys.append(0)#left
joy_keys.append(0)#right

# Helper callbacks
def on_key_press(key):
    print(key)

def on_key_release(key):
    print(key)

# Main loop
time.sleep(1)
start_time = time.time()
while True:
    # Timestamp for sample name
    d = datetime.datetime.utcnow().isoformat("T") + "Z" # <- get time in UTC
    file_name = d.replace(":","-")
    
    # Capture image sample
    img = np.array(sct.grab(cords))
    height, width, depth = img.shape

    # Downsize sample for displaying it in monitoring window
    img_disp = cv2.resize(img, (int(width/4), int(height/4)))
    img_disp = cv2.cvtColor(img_disp, cv2.COLOR_BGR2RGB)
    shape = img_disp.shape[1::-1]
    pygame_image = pygame.image.frombuffer(img_disp.tostring(), shape, 'RGB')
    gameDisplay.blit(pygame_image, (0, 0))
    pygame.display.update()
    
    # Capture program and key events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cv2.destroyAllWindows()
            logfile.close()
            pygame.quit()
            sys.exit()

        # Register key down events
        if event.type == pygame.KEYDOWN:
            if(event.key == 122): # Z key
                joy_keys[0] = 1
            if(event.key == 97): # A key
                joy_keys[1] = 1
            if(event.key == 99): # C key
                joy_keys[2] = 1
            if(event.key == 276): # LEFT key
                joy_keys[3] = 1
            if(event.key == 275): # RIGHT key
                joy_keys[4] = 1
            if(event.key == 32): # Space key will trigger recording
                record = not record
                if(record):
                    logfile = open(file_name+".csv", "w")
                    dir_name = file_name
                    os.mkdir("./imgs/"+dir_name)
                    sample_count = 0
                    print("start rec...")
                if(not record):
                    logfile.close()
                    print("stop rec...")

        # Register key up events
        if event.type == pygame.KEYUP:
            #print("UP: " + str(event.key))
            if(event.key == 122): # Z key
                joy_keys[0] = 0
            if(event.key == 97): # A key
                joy_keys[1] = 0
            if(event.key == 99): # C key
                joy_keys[2] = 0
            if(event.key == 276): # LEFT key
                joy_keys[3] = 0
            if(event.key == 275): # RIGHT key
                joy_keys[4] = 0

    # Serialize key presses (used later for categorize the samples)
    data = d+","+str(joy_keys[0])+","+str(joy_keys[1])+","+str(joy_keys[2])+","+str(joy_keys[3])+","+str(joy_keys[4])+"\n"
    
    # Send the pressed keys to the game application
    if joy_keys[0] == 1 or joy_keys[1] == 1 or joy_keys[2] == 1 or joy_keys[3] == 1 or joy_keys[4] == 1:
        keys_to_press = []
        if joy_keys[0] == 1:
            keys_to_press.append('Z')
        if joy_keys[1] == 1:
            keys_to_press.append('A')
        if joy_keys[2] == 1:
            keys_to_press.append('C')
        if joy_keys[3] == 1:
            keys_to_press.append('Left')
        if joy_keys[4] == 1:
            keys_to_press.append('Right')
        
        for key in keys_to_press: xdo.send_keysequence_window_down(win_id, key.encode())

    # Send the unpressed keys to the game application
    if joy_keys[0] == 0 or joy_keys[1] == 0 or joy_keys[2] == 0 or joy_keys[3] == 0 or joy_keys[4] == 0:
        keys_to_release = []
        if joy_keys[0] == 0:
            keys_to_release.append('Z')
        if joy_keys[1] == 0:
            keys_to_release.append('A')
        if joy_keys[2] == 0:
            keys_to_release.append('C')
        if joy_keys[3] == 0:
            keys_to_release.append('Left')
        if joy_keys[4] == 0:
            keys_to_release.append('Right')
        
        for key in keys_to_release: xdo.send_keysequence_window_up(win_id, key.encode())

    # Log the image samples + key presses
    if record:
        print("rec...")
        logfile.write(data)
        cv2.imwrite("./imgs/"+dir_name+"/"+str(sample_count).zfill(6)+".jpg",img,[cv2.IMWRITE_JPEG_QUALITY, 85])
        sample_count=sample_count+1

    # Calculate time taken for measuring sampling framerate
    time.sleep(0.001)
    time_diff = time.time() - start_time
    start_time = time.time()
    print(time_diff)
    