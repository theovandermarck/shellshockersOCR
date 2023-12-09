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
import random

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
displayWindow = False
thresh_scale_factor=3
dilation = True
erosion = True

sensMultiplier = .35

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
def preprocess(image_path, thresholding, thresh_scale_factor, gaussian_blur, dilation, erosion, contrast, kernel_size):
    # Open the image
    image = Image.open(image_path)

    # Convert the image to grayscale
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    # image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    image = cv2.bitwise_not(image)
    # Apply thresholding
    if thresholding:
        image = cv2.resize(image, None, fx=thresh_scale_factor, fy=thresh_scale_factor, interpolation=cv2.INTER_CUBIC)
    # if thresholding:
    #     _, image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)

    if gaussian_blur:
# Noise reduction using GaussianBlur
        image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    # Dilation to connect nearby text pixels
    if dilation:
        image = cv2.dilate(image, np.ones((kernel_size, kernel_size), np.uint8), iterations=1)

# Erosion to reduce noise and separate connected components
    if erosion:
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
        

        y = int((h*third_scale_factor - y*new_scale_factor - tb*new_scale_factor - bb*new_scale_factor))
        y2 = int((h*third_scale_factor - y2*new_scale_factor - tb*new_scale_factor - bb*new_scale_factor))

        cv2.rectangle(image_cv2, (x, y), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image_cv2, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    rescaled_image = cv2.resize(image_cv2, (w-rb-lb, h-bb-tb))
    cv2.imshow('Text Detection', rescaled_image)
def run_in_window(t,goal):
    i = 0
    while True:
        # thresholding, thresh_scale_factor, gaussian_blur, dilation, erosion, contrast, kernel_size = randomizeVals()
        thresholding, thresh_scale_factor, gaussian_blur, dilation, erosion, contrast, kernel_size = True, 3, False, False, False, True, 1
        i += 1 
        screenshot_path = f"screenshot_{i}.png"
        dst_path = os.path.join(cur_path, screenshot_path)
        img = pyautogui.screenshot(region=(lb, tb, w-rb-lb, h-bb-tb))
        img.save(dst_path)

        # Perform image preprocessing and OCR
        image = preprocess(image_path=dst_path, thresholding=thresholding, thresh_scale_factor=thresh_scale_factor, gaussian_blur=gaussian_blur, dilation=dilation, erosion=erosion, contrast=contrast, kernel_size=kernel_size)
        text_data, full_data = run_ocr(image)
        print(full_data)
        full_data = analyze_ocr(text_data=full_data,goal=goal)
        print(full_data)
        best_data = find_most_confident(full_data)
        print(best_data)
        if best_data != []:
            move_mouse_to_array(best_data)
        if displayWindow:
            display_window(image, text_data)
        # Wait for any keypress (0 delay)
            key = cv2.waitKey(t)
        # Break the loop if 'q' key is pressed
            if key == ord('q'):
                os.remove(dst_path)
                return
        else:
            print(thresholding, thresh_scale_factor, gaussian_blur, dilation, erosion, contrast, kernel_size)
        # input("Press return to continue")
        
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
def find_most_confident(text_array):
    highestNum = -1
    highestArray = []
    # print(text_array)
    for i in text_array:
        print(i[4])
        if float(i[4]) > float(highestNum):
            highestNum = i[4]
            highestArray = i
    return highestArray

def move_mouse_to_array(best_data):
    print("startingpos",pyautogui.position())
    # print(best_data)  
    # pyautogui.moveTo(w/2, h/2)
    # print(w/2, best_data[0], nt(best_data[0]))
    # print(best_data)
    xPosRel = int(best_data[0])/thresh_scale_factor+lb+int(best_data[2])/thresh_scale_factor/3
    # xPosRel = int(best_data[0])/thresh_scale_factor+lb
    # xPosRel = int(int(best_data[0])+(int(best_data[2])/2))+lb
    print(best_data[1], tb, bb)
    yPosRel = (int(best_data[1])/thresh_scale_factor+tb)+int(best_data[2])/thresh_scale_factor
    # yPosRel = (int(best_data[1])/thresh_scale_factor+tb)
    print(xPosRel,yPosRel)
    pyautogui.moveRel((xPosRel-(w/2))*sensMultiplier, (yPosRel-(h/2))*sensMultiplier)
    pyautogui.keyDown('shift')
    pyautogui.click()
    time.sleep(.1)
    pyautogui.click()
    pyautogui.keyUp('shift')
    pyautogui.press('r')
    # pyautogui.moveTo(xPosRel, yPosRel)

w, h = pyautogui.size()
lb, tb, rb, bb = 400, 140, 500, 300

# if get_true_false("Do you want to edit the postprocessing settings?"):
#     thresholding = get_true_false("Do you want to apply thresholding to the images?")
#     gaussian_blur = get_true_false("Do you want to apply Gaussian blur to the images?")
#     contrast = get_true_false("Do you want to apply contrast tools to the images?")
displayWindow = get_true_false("Do you want to display a visualization with bounding boxes and labels?")
goal = input("What string are you looking for? ")
# goal = "nuc"
def run_indef(goal):
    
    while True:
        # thresholding, thresh_scale_factor, gaussian_blur, dilation, erosion, contrast, kernel_size = randomizeVals()
        thresholding, thresh_scale_factor, gaussian_blur, dilation, erosion, contrast, kernel_size = True, 3, False, False, False, True, 1
        screenshot_path = "screenshot.png"
        dst_path = os.path.join(cur_path, screenshot_path)
        img = pyautogui.screenshot(region=(lb, tb, w-rb-lb, h-bb-tb))
        img.save(dst_path)

        # Perform image preprocessing and OCR
        image = preprocess(image_path=dst_path, thresholding=thresholding, thresh_scale_factor=thresh_scale_factor, gaussian_blur=gaussian_blur, dilation=dilation, erosion=erosion, contrast=contrast, kernel_size=kernel_size)
        text_data, full_data = run_ocr(image)
        # if full_data != '':
        #     for i in full_data.splitlines():
        #         try:
        #             print(i.split()[11])
        #         except:
        #             pass
            # input("WAITING FOR INPUT")
        full_data = analyze_ocr(text_data=full_data,goal=goal)
        best_data = find_most_confident(full_data)
        if best_data != []:
            move_mouse_to_array(best_data)
        # Optional: Remove the screenshot file after analysis if not needed
def randomizeVals():
    thresholding = bool(random.getrandbits(1))
    thresh_scale_factor=random.uniform(0.75,3)
    gaussian_blur = bool(random.getrandbits(1))
    dilation = bool(random.getrandbits(1))
    erosion = bool(random.getrandbits(1))
    contrast = bool(random.getrandbits(1))
    kernel_size = random.randrange(1,10,2)
    # thresholding = True
    # thresh_scale_factor=3
    # gaussian_blur = True
    # dilation = False
    # erosion = False
    # contrast = True
    # kernel_size = 9
    return thresholding, thresh_scale_factor, gaussian_blur, dilation, erosion, contrast, kernel_size

run_in_window(t=0, goal=goal)
# run_indef(goal=goal)
# False 1.5529785178152617 False False False True 7 - 3
# False 2.2303022685087965 False True True True 3
# True 1.8698499999999999 True True True True 9
# True 2.181624970153785 False False True True 3
# True 2.575352706572116 False True False False 1
# True 2.602982023765442 False True True False 9
# False 1.4623642398902799 True True False False 5
# False 2.9798685055361998 True True True True 9