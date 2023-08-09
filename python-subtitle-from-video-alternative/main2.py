from paddleocr import PaddleOCR
import cv2
import logging
logging.disable(logging.CRITICAL)
import re
import os
import time


def remove_special_chars(text):
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
    return text

def ocr_output(image_name) :
    ocr = PaddleOCR(use_gpu=True) 
    img_path = image_name
    result = ocr.ocr(img_path)
    for line in result:
        for word_info in line:
            return word_info[-1]
        

file_name = "cutter_test.mp4"

# Open video file
video = cv2.VideoCapture(file_name)

# Check if video opened successfully
if not video.isOpened(): 
    print("Error opening video file")

# Define the codec and create VideoWriter object
frame_rate = video.get(cv2.CAP_PROP_FPS)
total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
# 25.0 frames per second
frame_count = 0

if not os.path.exists('assets'):
    os.makedirs('assets')

while video.isOpened():
    # Capture frame-by-frame
    ret, frame = video.read()
    if ret:
        if frame_count % (frame_rate // 5) == 0:  # Adjust as needed to change screenshot frequency
            # Save frame as image
            print("progress: " + str(round(((frame_count / total_frames) * 100), 4)) + "%")
            # image_name = f'assets/frame{frame_count}.jpg'
            image_name = f'assets/capture.jpg'
            cv2.imwrite(image_name, frame)     
            result = ocr_output(image_name)
    else:
        break
    frame_count += 1

#550 frames total for subtitle extractor test.mp4
# Release the VideoCapture
video.release()
cv2.destroyAllWindows()