# Eye-Blink Communication GUI

A webcam-based assistive communication tool that lets a user select icons like “Food”, “Water”, “Restroom”, or “Emergency” using intentional eye blinks. The current icon is shown in a PyQt window, and a long blink selects it and triggers spoken feedback using text-to-speech.[web:289][web:291]

## Features

- Real-time face and eye detection using OpenCV Haar cascades.[web:199][web:287]
- Detects **long eye blinks** (eyes closed for a short duration) as a selection gesture.
- PyQt window displaying large, easily recognisable icons with labels:
  - Food, Water, Restroom, Emergency, Outdoor, Fan, Apple.
- Speaks the selected item aloud using `pyttsx3` text-to-speech.
- Visual feedback of eye state (“Eyes Open” / “Eyes Closed”) overlaid on the camera feed.

## Requirements

- Python 3.7–3.10 recommended.
- Webcam connected and accessible by OpenCV.
- Python packages:
  - `PyQt5`
  - `opencv-python`
  - `pyttsx3`

## Install dependencies:

```bash
pip install pyqt5 opencv-python pyttsx3
```

## Project Structure
text
project/
  main.py
  images/
    food.jpg
    bottle.jpg
    washroom.jpg
    emergency.jpg
    outdoor.jpg
    fan.png
    apple.jpg
    
Make sure the image file names match those used in IMAGE_ITEMS inside main.py.

## How It Works

OpenCV captures frames from the webcam and runs:

A face detector (haarcascade_frontalface_default.xml).

An eye detector (haarcascade_eye.xml).[web:199][web:287]

If eyes are detected, the system treats them as open.

When eyes are not detected for longer than a threshold (BLINK_MIN_CLOSED_TIME), it is treated as a long blink.

A long blink selects the currently displayed icon:

The selected label is printed to the console.

A background text-to-speech worker speaks the label using pyttsx3.

Icons automatically cycle every few seconds, so the user can wait for the desired option and then blink to choose it.[web:289][web:291]

## Running the App
From the project folder:

```bash
python main.py
```

## Usage tips

Ensure your face and eyes are clearly visible in front of the webcam.

Watch the “Eye Tracking” window to see the bounding box and the “Eyes Open / Eyes Closed” status.

When your desired icon (e.g. “Water”) is visible in the PyQt window, close your eyes briefly (a long blink) to select it.

Press Esc in the camera window or close the main GUI window to exit.

## Configuration
You can tune behaviour by editing these constants in main.py:

python
```bash
BLINK_MIN_CLOSED_TIME = 0.6   # seconds eyes must be closed to register a blink
CYCLE_INTERVAL = 2.0          # seconds before moving to the next icon
```
Increase BLINK_MIN_CLOSED_TIME if normal blinks are being detected accidentally.

Increase CYCLE_INTERVAL if icons change too quickly.

## Limitations
Blink detection relies on Haar cascades and simple heuristics, so performance can vary with:

Lighting conditions.

Camera quality and resolution.

Glasses or occlusions.

Timing thresholds may need to be tuned for different users.

This is a prototype for demonstration and learning, not a medically certified assistive device.

## Author
Utham Kumar Mohanlal
