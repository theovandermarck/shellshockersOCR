import cv2
import numpy as np
import pyautogui
from PIL import Image
import pytesseract
import os
# import time

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

cur_path = os.path.dirname(__file__)

# Function for image preprocessing and OCR
def preprocess_and_ocr(image_path, lb, tb, w, h):
    # Open the image
    image = Image.open(image_path)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # Apply thresholding
    _, threshold_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)

    # Noise reduction using GaussianBlur
    blurred_image = cv2.GaussianBlur(threshold_image, (5, 5), 0)

    # Adjust contrast
    contrast_image = cv2.equalizeHist(blurred_image)
    final_image = contrast_image
    # Save the preprocessed image (optional)
    cv2.imwrite('preprocessed_image.png', final_image)

    # Use Tesseract for text detection on the preprocessed image
    text_data = pytesseract.image_to_boxes(final_image)

    # Convert the image to BGR format for OpenCV
    image_cv2 = cv2.cvtColor(final_image, cv2.COLOR_GRAY2BGR)

    # Draw bounding boxes and labels on the image
    for line in text_data.splitlines():
        words = line.split()
        x, y, x2, y2 = int(words[1]), int(words[2]), int(words[3]), int(words[4])
        label = words[0]

        # Adjust coordinates based on the region of interest
        # x += int(w * lb / 2560)
        y = int(h) - (y)+h  # Adjust y-coordinate

        # x2 += int(w * lb / 2560)
        y2 = int(h - (y2)+h)  # Adjust y-coordinate

        cv2.rectangle(image_cv2, (x, y), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image_cv2, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the image with bounding boxes and labels
    cv2.imshow('Text Detection', image_cv2)
    # input("ENTER")
    # time.sleep(5)
    return text_data

# Region of interest (ROI) coordinates
w, h = pyautogui.size()
lb, tb, rb, bb = 400, 140, 500, 300

i = 0
while True:
    i += 1
    screenshot_path = f"screenshot_{i}.png"
    dst_path = os.path.join(cur_path, screenshot_path)
    img = pyautogui.screenshot()
    img.save(dst_path)

    # Perform image preprocessing and OCR
    print("; ", preprocess_and_ocr(dst_path, lb, tb, w, h))

    # Wait for any keypress (0 delay)
    key = cv2.waitKey(0)

    # Break the loop if 'q' key is pressed
    if key == ord('q'):
        break

    # Optional: Remove the screenshot file after analysis if not needed
    os.remove(dst_path)
