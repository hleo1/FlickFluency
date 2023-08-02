from paddleocr import PaddleOCR
import cv2
import logging
logging.disable(logging.CRITICAL)
import re
import os
# # If you want to use GPU (use_gpu=True), make sure to have the paddlepaddle-gpu library installed
# ocr = PaddleOCR(use_gpu=False) 
# img_path = 'Capture.PNG' # replace 'test.jpg' with your image
# result = ocr.ocr(img_path)

# for line in result:
#     for word_info in line:
#         print(word_info[-1]) 

def remove_special_chars(text):
    # Replace all non-word characters (everything except numbers and letters)
    # and non-Chinese characters with an empty string
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)

    return text

def ocr_output(image_name) :
    ocr = PaddleOCR(use_gpu=False) 
    img_path = image_name # replace 'test.jpg' with your image
    result = ocr.ocr(img_path)
    for line in result:
        for word_info in line:
            return word_info[-1]

# Open video file
video = cv2.VideoCapture('subtitle extractor test.mp4')

# Check if video opened successfully
if not video.isOpened(): 
    print("Error opening video file")

# Define the codec and create VideoWriter object
frame_rate = video.get(cv2.CAP_PROP_FPS)
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
            image_name = f'assets/frame{frame_count}.jpg'
            cv2.imwrite(image_name, frame)
            result = ocr_output(image_name)
            if (result != None) :
                print(image_name + " is: " + remove_special_chars(result[-1][0]) + " confidence level is: " + str(result[-1][1]))

            else:
                print("nothing in frame")
    else:
        break

    frame_count += 1

#550 frames total for subtitle extractor test.mp4
# Release the VideoCapture
video.release()
cv2.destroyAllWindows()

# ocr_output('frame156.jpg')
