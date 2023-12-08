import cv2
import numpy as np
import pyautogui
from PIL import Image
import pytesseract
import os
# import time

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

cur_path = os.path.dirname(__file__)

w, h = pyautogui.size()
lb, tb, rb, bb = 400, 140, 500, 300
kernel_size = 1

thresholding = False
gaussian_blur = True
contrast = False

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

    # Apply thresholding
    if thresholding:
        _, image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)

    if gaussian_blur:
# Noise reduction using GaussianBlur
        image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

# Adjust contrast
    if contrast:
        image = cv2.equalizeHist(image)
    cv2.imwrite('preprocessed_image.png', image)
    return image

def run_ocr(image):
    text_data = pytesseract.image_to_boxes(image)

    # Convert the image to BGR format for OpenCV
    image_cv2 = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Draw bounding boxes and labels on the image
    for line in text_data.splitlines():
        words = line.split()
        x, y, x2, y2 = int(words[1]), int(words[2]), int(words[3]), int(words[4])
        label = words[0]

        y = int(h) - (y)  # Adjust y-coordinate
        y2 = int(h - (y2))  # Adjust y-coordinate

        cv2.rectangle(image_cv2, (x, y), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image_cv2, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the image with bounding boxes and labels
    cv2.imshow('Text Detection', image_cv2)
    # input("ENTER")
    # time.sleep(5)
    return text_data

w, h = pyautogui.size()
lb, tb, rb, bb = 400, 140, 500, 300

if get_true_false("Do you want to edit the postprocessing settings?"):
    thresholding = get_true_false("Do you want to apply thresholding to the images?")
    gaussian_blur = get_true_false("Do you want to apply Gaussian blur to the images?")
    contrast = get_true_false("Do you want to apply contrast tools to the images?")

i = 0

while True:
    i += 1
    screenshot_path = f"screenshot_{i}.png"
    dst_path = os.path.join(cur_path, screenshot_path)
    img = pyautogui.screenshot()
    img.save(dst_path)

    # Perform image preprocessing and OCR
    image = preprocess(dst_path)
    run_ocr(image)
    # Wait for any keypress (0 delay)
    key = cv2.waitKey(0)

    # Break the loop if 'q' key is pressed
    if key == ord('q'):
        break

    # Optional: Remove the screenshot file after analysis if not needed
    os.remove(dst_path)
