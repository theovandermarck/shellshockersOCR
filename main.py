# Set line 21, 26, or 31 (changes depending on OS) to the path of your Tesseract executable (https://tesseract-ocr.github.io/tessdoc/Installation.html)
# After doing so, run the program and press any key while the screenshot window is focused to advance to the next screenshot OR alternatively if not using the visualization window, press return in the terminal to advance to the next run.
# pressing 'Q' will quit the program


import cv2
import numpy as np
import pyautogui
from PIL import Image
import pytesseract
import os
import sys
import time

platform = sys.platform
# CHANGE ME - Set the path to the Tesseract executable
if platform == 'win32':
    #Change this to make the boxes on the visualization appear further up/down
    third_scale_factor = 1.35
    #Change this to reflect your tesseract path for windows (this is the path that our tesseract was installed on)
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
elif platform == 'darwin':
    #Change this to make the boxes on the visualization appear further up/down
    third_scale_factor = 1.29
    #Change this to reflect your tesseract path for mac (this was the default path from out homebrew installation)
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
else:
    #Change this to make the boxes on the visualization appear further up/down
    third_scale_factor = 1.35
    #Change this to reflect your tesseract path for any other platform
    pytesseract.pytesseract.tesseract_cmd = r'INSERT YOUR TESSERACT PATH HERE'

cur_path = os.path.dirname(__file__)

w, h = pyautogui.size()
lb, tb, rb, bb = 400, 140, 500, 300
kernel_size = 1

thresholding = False
gaussian_blur = True
contrast = True
displayWindow = True

def get_true_false(prompt):
    while True:
        i = input(f"{prompt} Please respond with 'y', 'yes', 'n', or 'no' (not case-sensitive): ")
        if i.lower() in ['y', 'yes']:
            return True
        elif i.lower() in ['n', 'no']:
            return False
        else:
            print("Invalid input. Please try again.")


# Function for image preprocessing and OCR
def preprocess(image_path):
    # Open the image
    image = Image.open(image_path)

    # Convert the image to grayscale
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    # image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    image = cv2.bitwise_not(image)
    # Apply thresholding
    image = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    # if thresholding:
    #     _, image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)

    if gaussian_blur:
# Noise reduction using GaussianBlur
        image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    # Dilation to connect nearby text pixels
    image = cv2.dilate(image, np.ones((kernel_size, kernel_size), np.uint8), iterations=1)

# Erosion to reduce noise and separate connected components
    image = cv2.erode(image, np.ones((kernel_size, kernel_size), np.uint8), iterations=1)
    
# Adjust contrast
    if contrast:
        image = cv2.equalizeHist(image)
    cv2.imwrite('preprocessed_image.png', image)
    return image

def run_ocr(image):
    text_data = pytesseract.image_to_boxes(image)
    full_data = pytesseract.image_to_data(image)
    return text_data, full_data
def display_window(image, text_data):
    # Convert the image to BGR format for OpenCV
    image_cv2 = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Draw bounding boxes and labels on the image
    for line in text_data.splitlines():
        words = line.split()
        scale_factor = 1
        new_scale_factor = 1
        # print(words[6])
        x, y, x2, y2 = int(int(words[1]) / scale_factor), int(int(words[2]) / scale_factor), int(int(words[3]) / scale_factor), int(int(words[4]) / scale_factor)
        label = words[0]
        

        y = int((h*1.29 - y*new_scale_factor - tb*new_scale_factor - bb*new_scale_factor))
        y2 = int((h*1.29 - y2*new_scale_factor - tb*new_scale_factor - bb*new_scale_factor))

        cv2.rectangle(image_cv2, (x, y), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image_cv2, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    rescaled_image = cv2.resize(image_cv2, (w-rb-lb, h-bb-tb))
    cv2.imshow('Text Detection', rescaled_image)
def run_in_window(t,goal):
    i = 0
    while True:
        i += 1
        screenshot_path = f"screenshot_{i}.png"
        dst_path = os.path.join(cur_path, screenshot_path)
        img = pyautogui.screenshot(region=(lb, tb, w-rb-lb, h-bb-tb))
        img.save(dst_path)

        # Perform image preprocessing and OCR
        image = preprocess(dst_path)
        text_data, full_data = run_ocr(image)
        print(full_data)
        print(analyze_ocr(text_data=full_data,goal=goal))
        if displayWindow:
            display_window(image, text_data)
        # Wait for any keypress (0 delay)
            key = cv2.waitKey(t)
        # Break the loop if 'q' key is pressed
            if key == ord('q'):
                os.remove(dst_path)
                return
        else:
            input("Press return to continue")
        
        time.sleep(1)
        # Optional: Remove the screenshot file after analysis if not needed
        os.remove(dst_path)
def analyze_ocr(text_data, goal):
    a = []
    for line in text_data.splitlines():
        words = line.split()
        if words[6] == 'left':
            continue
        try:
            if goal in words[11].lower():
                a.append(words[6:12])
        except:
            pass
    return a

w, h = pyautogui.size()
lb, tb, rb, bb = 400, 140, 500, 300

if get_true_false("Do you want to edit the postprocessing settings?"):
    thresholding = get_true_false("Do you want to apply thresholding to the images?")
    gaussian_blur = get_true_false("Do you want to apply Gaussian blur to the images?")
    contrast = get_true_false("Do you want to apply contrast tools to the images?")
displayWindow = get_true_false("Do you want to display a visualization with bounding boxes and labels?")
goal = input("What string are you looking for? ")

run_in_window(t=0, goal=goal)

