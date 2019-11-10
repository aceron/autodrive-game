# Sample program for loading NN weights, capture game screen, predict action and send it to a game window

# Import libraries:
import numpy as np
import cv2
from mss import mss
import time
import datetime
import os
from xdo import Xdo
from pynput.keyboard import Key, Controller
import pygame
import sys

# Import libraries for NN
import numpy as np
import tensorflow as tf
import keras
from keras.models import model_from_json
from keras import layers
from keras.callbacks import Callback
from keras.models import Model
from keras.models import Sequential
from keras.utils import to_categorical
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from itertools import groupby

# Library initialization
xdo = Xdo()
pygame.init()
sct = mss()

# Screen Settings:
display_width = 640
display_height = 400

# General variables:
idle_counter = 0
res_x = 124
res_y = 50
cords = {'top':70 , 'left': 5 , 'width': display_width, 'height': display_height }
win_name = "GAMEWINDOWNAME"
predict = False
home_folder = "/home/user0/autodrive-game/"
sample_count = 0

# Get window for sending key events to a window
print(len(xdo.search_windows(win_name.encode())))
win_id = xdo.search_windows(win_name.encode())[0]
print("WIN ID:" + str(win_id))

# Initialize display for monitoring
gameDisplay = pygame.display.set_mode((int(3*res_x),int(res_y)))
pygame.display.set_caption('Driving')

# Key mappings
joy_keys = []
joy_keys.append(0)#accel
joy_keys.append(0)#break
joy_keys.append(0)#jump
joy_keys.append(0)#left
joy_keys.append(0)#right

# Helper callbacks
def on_key_press(key):
    print(key)

def on_key_release(key):
    print(key)

# Load the NN model and its weights for making predictions
json_file = open(home_folder + 'model_v1.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights(home_folder + "model_v1.h5")
print("Loaded model")

# Compile the loaded model
loaded_model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adam(),
              metrics=['accuracy'])

# Prepare buffers
prev_frame = np.array([])
prev_prev_frame = np.array([])

# Main loop
sample_count = 0
time.sleep(1)
while True:

    # Capture image sample
    input_frame = np.array(sct.grab(cords))
    input_frame = cv2.cvtColor(input_frame, cv2.COLOR_BGR2RGB)
    height, width, depth = input_frame.shape
    input_frame = cv2.resize(input_frame, (res_x, res_y))
    
    # Assemble the sample (previous previous + previous + current)
    if sample_count > 2:
        
        h0, w0 = prev_prev_frame.shape[:2]
        h1, w1 = prev_frame.shape[:2]
        h2, w2 = input_frame.shape[:2]

        # Create empty matrix
        finalimg = np.zeros((max(h0, h1, h2), w0+w1+w2,3), np.uint8)

        # Combine images
        finalimg[:h0, :w0,:3] = prev_prev_frame
        finalimg[:h1, w0:w0+w1,:3] = prev_frame
        finalimg[:h2, w0+w1:w0+w1+w2,:3] = input_frame

        # Display assembled sample for monitoring
        shape = finalimg.shape[1::-1]
        pygame_image = pygame.image.frombuffer(finalimg.tostring(), shape, 'RGB')
        gameDisplay.blit(pygame_image, (0, 0))
        pygame.display.update()
        
        # Prepare assembled sample for NN
        pred_set_t = []
        pred_set_t.append(finalimg.copy())
        pred_set_np_t = np.array(pred_set_t)
        if len(pred_set_np_t.shape) != 4:
            pred_set_np_t = np.expand_dims(pred_set_np_t, axis=3)
        pred_set_np_t = pred_set_np_t.astype('float') / 255

        # Get predicted action
        y_pred_t = loaded_model.predict_classes(pred_set_np_t)

        # To avoid getting "stuck" in an IDLE action, after being "too long" in IDLE state, do a RIGHT+ACCEL action 
        if(idle_counter>10):
            idle_counter = idle_counter - 1
            y_pred_t[0]=5

        if(idle_counter<0):
            idle_counter = 0

        # Map predicted action into key presses
        if(y_pred_t[0]==0):
            print("IDLE")
            joy_keys[0] = 0
            joy_keys[3] = 0
            joy_keys[4] = 0
            idle_counter = idle_counter + 1
        elif(y_pred_t[0]==1):
            joy_keys[0] = 1
            joy_keys[3] = 0
            joy_keys[4] = 0
            print("ACCEL")
        elif(y_pred_t[0]==2):
            joy_keys[0] = 0
            joy_keys[3] = 1
            joy_keys[4] = 0
            print("LEFT")
        elif(y_pred_t[0]==3):
            joy_keys[0] = 0
            joy_keys[3] = 0
            joy_keys[4] = 1
            print("RIGHT")
        elif(y_pred_t[0]==4):
            joy_keys[0] = 1
            joy_keys[3] = 1
            joy_keys[4] = 0
            print("LEFT + ACCEL")
        elif(y_pred_t[0]==5):
            joy_keys[0] = 1
            joy_keys[3] = 0
            joy_keys[4] = 1
            print("RIGHT + ACCEL")

        # Capture program and key events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cv2.destroyAllWindows()
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
                if(event.key == 32): # Space key will trigger start of sending key presses from predicted results
                    predict = not predict
            
            # Register key up events
            if event.type == pygame.KEYUP:
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

        # If automatic control from predictions is enabled, send key presses to the game application
        if predict:
            print("...ACTIVE...")
            # Key Down events
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

            # Key Up events
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

    sample_count = sample_count + 1 # keep track of how many frames we have taken so far

    # Store previous frames for future predictions
    prev_prev_frame = prev_frame.copy()
    prev_frame = input_frame.copy()

    time.sleep(0.001)
