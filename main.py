# Set line 25, 30, or 35 (changes depending on OS) to the path of your Tesseract executable (https://tesseract-ocr.github.io/tessdoc/Installation.html)
# After doing so, run the program and press any key while the screenshot window is focused to advance to the next screenshot OR alternatively if not using the visualization window, press return in the terminal to advance to the next run.
# pressing 'Q' will quit the program

# Citations: pytesseract (the OCR library used) https://pypi.org/project/pytesseract/, which is a wrapper for Tesseract (the OCR engine used) https://tesseract-ocr.github.io/tessdoc/Installation.html; pyautogui (the library used to take screenshots and move the mouse) https://pyautogui.readthedocs.io/en/latest/; OpenCV (the library used to alter and process the images) https://docs.opencv.org/4.x/d2/d96/tutorial_py_table_of_contents_imgproc.html; PIL (the library used to convert the screenshots to images) https://pillow.readthedocs.io/en/stable/; Numpy (used to assist in image processing) https://numpy.org/doc/stable/

# import libraries
import cv2
import numpy as np
import pyautogui
from PIL import Image
import pytesseract
import os
import sys
import time
import random

# Get the platform the program is running on; Citation: https://www.devdungeon.com/content/get-operating-system-info-python
platform = sys.platform
# CHANGE ME - Set the path to the Tesseract executable
if platform == 'win32':
    # Change this to make the boxes on the visualization appear further up/down
    third_scale_factor = 1.35
    # Change this to reflect your tesseract path IF YOU ARE ON WINDOWS (this is the path that our tesseract was installed on)
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
elif platform == 'darwin':
    # Change this to make the boxes on the visualization appear further up/down
    third_scale_factor = 1.29
    # Change this to reflect your tesseract path IF YOU ARE ON MACOS (this was the default path from out homebrew installation)
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
else:
    # Change this to make the boxes on the visualization appear further up/down
    third_scale_factor = 1.35
    # Change this to reflect your tesseract path IF YOU ARE ON A NON WINDOWS/MAC OS PLATFORM
    pytesseract.pytesseract.tesseract_cmd = r'INSERT YOUR TESSERACT PATH HERE'

# Get current path
cur_path = os.path.dirname(__file__)

# Get screen width, height; Citation: this is from the pyautogui documentation, which I referenced earlier. For all following instances of code from the documentation of pyautodui (which is already listed at the top), they will not be cited.
w, h = pyautogui.size()
# Set buffers around each screenshot measured in pixels (lb: distance from left, tb: distance from top, rb: distance from right, bb: distance from bottom)
lb, tb, rb, bb = 400, 140, 500, 300

# Define default image processing settings
resizing, resize_scale_factor, gaussian_blur, dilation, erosion, contrast, kernel_size, thresholding = True, 3, False, False, False, True, 1, False
# Set to True to display the visualization window
displayWindow = False

# Set the mouse sensitivity multiplier (default is 1 for being in a normal 2d environment, .35 seemed to work best on our machines while in game)
sensMultiplier = .35

# Define function to create yes/no input prompts
def get_true_false(prompt):
    while True:
        i = input(f"{prompt} Please respond with 'y', 'yes', 'n', or 'no' (not case-sensitive): ")
        if i.lower() in ['y', 'yes']:
            return True
        elif i.lower() in ['n', 'no']:
            return False
        else:
            print("Invalid input. Please try again.")

# Define function to process images; Citation: this is from the PIL documentation, which I referenced earlier. For all following instances of code from the documentation of PIL (which is already listed at the top), they will not be cited.
def preprocess(image_path):
    image = Image.open(image_path)

    # Convert image to greyscale and bitwise; Citation: this is from the cv2 documentation, which I referenced earlier. For all following instances of code from the documentation of cv2 (which is already listed at the top), they will not be cited.
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    image = cv2.bitwise_not(image)
    # If using image resizing, apply it
    if resizing:
        image = cv2.resize(image, None, fx=resize_scale_factor, fy=resize_scale_factor, interpolation=cv2.INTER_CUBIC)
    # If using adaptive thresholding, apply it
    if thresholding:
        image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    # If using gaussian blur, apply it
    if gaussian_blur:
        image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    # If using dilation, apply it; Citation: part of this is from the Numpy documentation, which I referenced earlier. For all following instances of code from the documentation of Numpy (which is already listed at the top), they will not be cited.
    if dilation:
        image = cv2.dilate(image, np.ones((kernel_size, kernel_size), np.uint8), iterations=1)
    # If using erosion, apply it
    if erosion:
        image = cv2.erode(image, np.ones((kernel_size, kernel_size), np.uint8), iterations=1)
    # If using contrast, apply it
    if contrast:
        image = cv2.equalizeHist(image)
    # Save the image as preprocessed_image.png and return it as an image (rather than as a file path)
    cv2.imwrite('preprocessed_image.png', image)
    return image

# Define function to run the Tesseract OCR on the image
def run_ocr(image):
    # Obtain data of the individual characters in the image (not currently used besides visualization which is disabled by default); Citation: this is from the pytesseract documentation, which I referenced earlier. For all following instances of code from the documentation of pytesseract (which is alreadu listed at the top), they will not be cited.
    text_data = pytesseract.image_to_boxes(image)
    # Obtain data of the boxes of words in the image, including location, box size, confidence, etc.
    full_data = pytesseract.image_to_data(image)
    # Return the individual character data and the word box data
    return text_data, full_data

# Define function to display the visualization window
def display_window(image, text_data):
    # Convert the image to cv2 greyscale
    image_cv2 = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    # Iterate through each individual character displayed and draw a box around it
    for line in text_data.splitlines():
        # Split into characters
        words = line.split()
        # Set relevant scale variables
        scale_factor = 1
        new_scale_factor = 1
        # Set x,y,x2,y2 coordinates of each character
        x, y, x2, y2 = int(int(words[1]) / scale_factor), int(int(words[2]) / scale_factor), int(int(words[3]) / scale_factor), int(int(words[4]) / scale_factor)
        # Set the label of each character
        label = words[0]
        
        # Adjust the coordinates of each image box to comensate for the buffers around the screenshot and how the model and for how the visualization deals with Y values opposite of how the model does (0y in the model would be 1440y in the visualization, and the converse)
        y = int((h*third_scale_factor - y*new_scale_factor - tb*new_scale_factor - bb*new_scale_factor))
        y2 = int((h*third_scale_factor - y2*new_scale_factor - tb*new_scale_factor - bb*new_scale_factor))

        # Draw the box and label on the visualization
        cv2.rectangle(image_cv2, (x, y), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image_cv2, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # Scale the image back down to a normal size and display it
    rescaled_image = cv2.resize(image_cv2, (w-rb-lb, h-bb-tb))
    cv2.imshow('Text Detection', rescaled_image)

# Define the function to string together all of the functions, taking a screenshot -> processing it -> running OCR on it -> moving the mouse
def run_main(t,goals):
    # Check if the goal is to find any string besides '' and '~'
    any = False
    if goals == ['ANY']:
        goals = ['']
        any = True
    # Iterate until program ends
    while True:
        startTime = time.time()
        # Take a screenshot and save it
        screenshot_path = f"screenshot.png"
        dst_path = os.path.join(cur_path, screenshot_path)
        img = pyautogui.screenshot(region=(lb, tb, w-rb-lb, h-bb-tb))
        img.save(dst_path)

        # Perform image processing
        image = preprocess(image_path=dst_path)

        # Perform OCR on the image and print the word box data
        text_data, full_data = run_ocr(image)
        print(full_data)

        # Analyze the OCR word box data and find any words that match the goal string(s), then print it
        full_data = analyze_ocr(text_data=full_data,goals=goals,any=any)
        print(full_data)

        # Out of the word boxes that match the goal string(s), find the one with the highest confidence and print it
        best_data = find_most_confident(full_data)
        print(best_data)

        # If there is a word box matching the goal string(s), move the mouse to it
        if best_data != []:
            move_mouse_to_array(best_data)

        # If the visualization window is enabled, display it. Then wait for either a keypress or amount of time to continue (if t=0 wait for a keypress, if t>0 wait for that many milliseconds). If the keypress = q, end the program (fun fact! this is the only way to end the program, and it's locked behind a variable that is hardcoded as false!)
        if displayWindow:
            display_window(image, text_data)
            key = cv2.waitKey(t)
            if key == ord('q'):
                os.remove(dst_path)
                return
        else:
            # If not displaying the visualization window, print the current image processing settings (this is for debugging)
            print(resizing, resize_scale_factor, gaussian_blur, dilation, erosion, contrast, kernel_size)
        executionTime = (time.time() - startTime)
        print('Time to run (seconds): ' + str(executionTime))

# Define function to analyze the OCR word box data and find any words that match the goal string(s)
def analyze_ocr(text_data, goals, any):
    # Initialize the list a to store words that match (any of) the goal string(s)
    a = []
    # Iterate through each word box
    for line in text_data.splitlines():
        # Split the word box data into a comprehensible list
        words = line.split()
        # Somewhat rough fix, since the values returned include a header row this line checks if the 6th value is left (this is the left column, so this should usually be a float) and skips it if so
        if words[6] == 'left':
            continue
        # Iterate through each goal string and check if it makes up part of the text in the current word box (For example, if the goal is 'as' and the text in the word box the model identified is 'pass' the goal is satisfied and that word box is appended to list a)
        try:
            for goal in goals:
                if goal in words[11].lower():
                    if any:
                        if words[11] != '' and words[11] != '~':
                            a.append(words[6:12])
                    else:
                        a.append(words[6:12])
        except:
            pass
    # Return list a, which has all of the word boxes that have any one of the goal strings in their text content
    return a

# Define function to iterate through the text boxes that satisfy any one of the goal string(s) and find the one with the highest confidence value
def find_most_confident(text_array):
    # Set the default highest num to -1, since sometimes word boxes come out of the model with a confidence of 0
    highestNum = -1
    # Set highestArray to an empty array, since it's possible that no word boxes have been passed into this function and if so we still want to return something
    highestArray = []
    # Iterate through each word box
    for i in text_array:
        # Print the text content of each word box
        print(i[5])
        # If the confidence of the current word box is the highest recorded so far, set the highestArray (which is the one that will be returned) to the current word box
        if float(i[4]) > float(highestNum):
            # Set the highest recorded confidence value to the current word box's confidence value and set highestArray to the current word box
            highestNum = i[4]
            highestArray = i
    # Return the word box with the highest confidence value
    return highestArray

# Define function to move the mouse to the center of the given word box (in this case, the word box that will be passed in is the one with the highest confidence value)
def move_mouse_to_array(best_data):
    # Define the factors by which the mouse will be moved away from the origin of the word box. If in demo mode the mouse will be moved to the center of the word box, but if in normal mode the mouse is moved to a position with the x at the midway point of the word box and the y at the top of the word box minus the width of the word box (this is since we're trying to hit players below nametags, not the nametags themselves). clb is the distance offset on the x axis (from the left) and ctb is the distance offset on the y axis (from the top)
    clb = int(best_data[2])/resize_scale_factor/3
    ctb = +int(best_data[2])/resize_scale_factor
    if demo:
        # If in demo mode, move the mouse to the center of the screen (the mouse is permanently in the center of the screen but we need to replicate this when we're demoing the program in a 2d space)
        pyautogui.moveTo(w/2, h/2)
        ctb = int(best_data[3])/resize_scale_factor/2
    # Set the destination for the mouse to move on the X axis. This is derived from the position in the screenshot divided by the resizing factor of the image, and the screenshot buffer (defined line 46) and clb (defined line 220) are both added to this value.
    xPos = int(best_data[0])/resize_scale_factor+lb+clb
    # Set the destination for the mouse to move on the Y axis. This is derived from the position in the screenshot divided by the resizing factor of the image, and the screenshot buffer (defined line 46) and ctb (defined line 221 or line 225) are both added to this value.
    yPos = int(best_data[1])/resize_scale_factor+tb+ctb
    print(xPos,yPos)
    # Define the distance for the mouse to be moved on the x/y from the center of the screen. This is derived from the goal position, from which the width/height are subtracted. Finally, the two values are multiplied by sensMultiplier (the sensitivity variable, which determines what percentage of the distance the mouse actually travels to better line up with how those movements translate in-game)
    xPosRel = (xPos-(w/2))*sensMultiplier
    yPosRel = (yPos-(h/2))*sensMultiplier
    # Use pyautogui.moveRel to move the mouse relative to the current position, which is the center of the screen
    pyautogui.moveRel(xPosRel, yPosRel)
    # If not in demo mode, follow up the mouse movement by pressing shift (exntering zoom), pressing left click twice (to shoot twice), letting go of shift (exiting zoom), and pressing r (reload)
    if demo == False:
        pyautogui.keyDown('shift')
        pyautogui.click()
        time.sleep(.25)
        pyautogui.click()
        pyautogui.keyUp('shift')
        pyautogui.press('r')

# Define function to randomize image processing variables. This was used to attempt to optimize the text recognition of the model and find the best variables. The program returns an output that can be directly pasted into line 46 to set the default variables to those; Citation: https://stackoverflow.com/questions/6824681/get-a-random-boolean-in-python
def randomizeVals():
    resizing = bool(random.getrandbits(1))
    resize_scale_factor=random.uniform(0.75,3)
    gaussian_blur = bool(random.getrandbits(1))
    dilation = bool(random.getrandbits(1))
    erosion = bool(random.getrandbits(1))
    contrast = bool(random.getrandbits(1))
    kernel_size = random.randrange(1,10,2)
    thresholding = bool(random.getrandbits(1))
    return resizing, resize_scale_factor, gaussian_blur, dilation, erosion, contrast, kernel_size, thresholding

# This is the part of the script that runs when you run it (I don't know how to phrase that properly).
# Give the user prompts about changing/not changing the image processing settings
if get_true_false("Do you want to edit the image processing settings?"):
    resizing = get_true_false("Do you want to apply resizing to the images?")
    if resizing:
        resize_scale_factor = float(input("What scale factor do you want to use to resize the images? "))
        gaussian_blur = get_true_false("Do you want to apply gaussian blur to the images?")
        dilation = get_true_false("Do you want to apply dilation to the images?")
        erosion = get_true_false("Do you want to apply erosion to the images?")
        kernel_size = int(input("What kernel size do you want to use for dilation, erosion and or blur? "))
        thresholding = get_true_false("Do you want to apply adaptive thresholding to the images?")
    contrast = get_true_false("Do you want to apply contrast tools to the images?")
# Give the user a prompt to change the sensitivity multiplier (sensMultiplier)
if get_true_false("Do you want to change the default sensitivity multiplier?"):
    sensMultiplier = float(input("What sensitivity multiplier do you want to use? "))
# Give the user a prompt to run the program in demo mode, where it looks for test in a normal 2d window and has no functionality besides moving the mouse to the text
demo = get_true_false("Do you want to run in demo mode? (mouse will recenter each time)")
# If in demo mode, set the sensitivity multiplier to 1
if demo:
    sensMultiplier = 1

# Get the goal string(s) that the user is looking for
# Initialize the list
goals = []
# Run indefinitely
while True:
    userInput = input(f"What string(s) are you looking for? Enter each one individually, and enter 'q' when you are done. Enter 'ANY' to look for any string besides '' and '~'. Currently looking for: {goals} ")
    # End the loop if input 'q'
    if userInput == 'q': 
        break
    # End the loop if input 'ANY', and set the goals to ['ANY'] to prepare the run_main() function to set any to true
    elif userInput == 'ANY':
        goals = ['ANY']
        break
    # If a normal input is given, append it to the goals list
    goals.append(userInput)

# Run main, (t here references the window behavior if the variable displayWindow is set to true. It currently displays text boxes in the wrong places if the scale factor is anything besides 1 (and maybe even if it is 1), and since it being on is an active detriment to the program's intended goal we haven't put effort into fixing that.) If displayWindow were true t equaling 0 would mean that the program continues on any keypress, and it equaling anything else would mean that the program would wait that many milliseconds before continuing.
run_main(t=0, goals=goals)




# OBSOLETE CODE BELOW HERE

# This was the original function to run the code infinitely with no breaks, as compared to running it with a visualization window, but over time the visualization window one morphed into a function that could do both


# def run_indef(goal):
#     while True:
#         # resizing, resize_scale_factor, gaussian_blur, dilation, erosion, contrast, kernel_size = randomizeVals()
#         resizing, resize_scale_factor, gaussian_blur, dilation, erosion, contrast, kernel_size = True, 3, False, False, False, True, 1
#         screenshot_path = "screenshot.png"
#         dst_path = os.path.join(cur_path, screenshot_path)
#         img = pyautogui.screenshot(region=(lb, tb, w-rb-lb, h-bb-tb))
#         img.save(dst_path)

#         # Perform image preprocessing and OCR
#         image = preprocess(image_path=dst_path, resizing=resizing, resize_scale_factor=resize_scale_factor, gaussian_blur=gaussian_blur, dilation=dilation, erosion=erosion, contrast=contrast, kernel_size=kernel_size)
#         text_data, full_data = run_ocr(image)
#         # if full_data != '':
#         #     for i in full_data.splitlines():
#         #         try:
#         #             print(i.split()[11])
#         #         except:
#         #             pass
#             # input("WAITING FOR INPUT")
#         full_data = analyze_ocr(text_data=full_data,goal=goal)
#         best_data = find_most_confident(full_data)
#         if best_data != []:
#             move_mouse_to_array(best_data)
#         # Optional: Remove the screenshot file after analysis if not needed