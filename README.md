# autodrive-game
Educational purpose code from training a NN to control a racing game

- Introduction:
  - This is a code that was generated to practice the basics of training a NN and use the predictions on a demo application.
  - The demo application is to make automatic control of a game character in a racing game.
  - The inputs for the NN are images samples taken from the game screen and the key presses representing actions corresponding to a certain game state represented by the screen.
  - The key presses are used to categorize the screen samples into the following actions: IDLE, ACCEL, LEFT, RIGHT, LEFT+ACCEL and RIGHT+ACCEL
  - For the training, the samples are 3 images concatenated together in an attempt to represent the game state sequences which lead to take certain actions (i.e. key presses)
  - The tests were run under Ubuntu 16.04 and Python 3.5
  
- Programs:
  - cap-screen-game.py:
    - Capture frames from a region of the screen
    - Manipulates the captured frame for displaying it
    - Displays the captured frames
    - Listens and records key-events (press and release)
    - Sends key presses to a window (i.e. the game window)
    - Saves the logged image frames and key events
  - train-from-samples.ipynb:
    - Loads the saved image frames and key events
    - Concatenates 3 consecutive frames to provide a sequence (i.e. samples)
    - Assigns categories to the samples based on the corresponding recorded key-events
    - Builds a NN model
    - Trains the model using the samples
    - Saves the model and its weights
  - pred-screen-game.py:
    - Loads the trained model
    - Capture frames from a region of the screen
    - Manipulates the captured frame
    - Creates the image sequences
    - Displays the image sequences
    - Inputs the sequence into the NN model
    - Predicts an action
    - Converts the action into key events
    - Sends the key events to a window (i.e. the game window)

- Test settings:
  - Game: Wacky Wheels Version 1.1 Shareware Release
  - Character: RAZER
  - Class: Pro
  - Length: 6 Laps
  - Engine: Fast 12 HP
  - Race: Bronze Wheels
  - Track: 1
  - Human Driver: 1
  - CPU Drivers: 7
  - Sampling framerate: ~15 fps
  - Played games: 7 (for a total of 8129 screen samples)

- Training settings:
  - Samples for training:	5691
  - Samples for validation:	2438
  - Original sample dimensions: 640x400x3
  - Sample preprocessing:
	  - Need to consider changes in time for better result -> provide 3 consecutive frames as 1 sample
	  - Resize samples into 124x50x3
	  - Concatenate 3 consecutive samples horizontally (right-most = oldest, left-most = newest)
	  - Take category from left-most sample 
  - Final Sample dimensions: 372x50x3
  - Batch size:	175
  - Validation split: 0.25
  - Total Epochs: 46
  - NN Structure: Please refer to the "train-from-samples" notebook

- Results:

  | Class | Precision | Recall | F1 Score |
  |---|---|---|---|
  | IDLE | 0.68181818 | 0.16304348 | 0.26315789 |
  | ACCEL | 0.79347055 | 0.90453074 | 0.84536862 |
  | LEFT | 0.42519685 | 0.26732673 | 0.32826748 |
  | RIGHT | 0.00000000 | 0.00000000 | 0.00000000 |
  | LEFT+ACCEL | 0.70734908 | 0.70000000 | 0.70365535 |
  | RIGHT+ACCEL | 0.80769231 | 0.33333333 | 0.47191011 |

- Result video:
  - Name: auto-drive-run.mp4
  - Notes: The video is only for educational purposes. I do not own any of the characters, graphic art, source code or any other intellectual asset pertinent to the game. 

- Comments:
  - The player who took the samples was not expert in playing this game. It was useful to take samples of poor driving in order to learn how to recover from a mistake.
  - The prediction works better when the same character (RAZER) is selected during a run.
  - The prediction does not work for different Races and Tracks, as the samples for training only include images and actions for the mentioned Race and Track.
  - The prediction also performs well in Champion Class.
  - From the training result, looks like with the current samples it is not clear when to trigger the "RIGHT" category (turning right without accelerating).
  - Highest F1 scores are for ACCEL, LEFT+ACCEL and RIGHT+ACCEL classes.
