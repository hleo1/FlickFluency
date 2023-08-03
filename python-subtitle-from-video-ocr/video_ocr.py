from paddleocr import PaddleOCR
import cv2
import logging
logging.disable(logging.CRITICAL)
import re
import os
import time
# # If you want to use GPU (use_gpu=True), make sure to have the paddlepaddle-gpu library installed
# ocr = PaddleOCR(use_gpu=False) 
# img_path = 'Capture.PNG' # replace 'test.jpg' with your image
# result = ocr.ocr(img_path)

# for line in result:
#     for word_info in line:
#         print(word_info[-1]) 

start_time = time.time()

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
        
def frame_to_time(frame_number, fps):
    # Calculate total seconds
    total_seconds = frame_number / fps

    # Calculate hours, minutes, and seconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    # Calculate milliseconds
    milliseconds = int((total_seconds - int(total_seconds)) * 1000)

    # Return formatted string
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

# Open video file
video = cv2.VideoCapture('subtitle extractor test.mp4')

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

previous_subtitle_text = ""
current_subtitle_text = ""
first = True

subtitle_data = []
ocr_seconds = 0

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
            ocr_start_time = time.time()
            result = ocr_output(image_name)
            ocr_end_time = time.time()
            print("ocr time took: " + str(ocr_end_time - ocr_start_time) + " seconds to complete")
            ocr_seconds += (ocr_end_time - ocr_start_time)

            if (result != None) :
                previous_subtitle_text = current_subtitle_text
                current_subtitle_text =  remove_special_chars(result[0])
                accuracy = str(result[1])
            else:
                previous_subtitle_text = current_subtitle_text
                current_subtitle_text = "nothing"
                # print("nothing in frame")

            # print("frame count is: " + str(frame_count) + " previous subtitle: " + previous_subtitle_text + " current subtitle: " + current_subtitle_text)
            if (previous_subtitle_text != current_subtitle_text) :
                if (first == False) :
                    # print("to frame count " + str(frame_count - 5))

                    subtitle_data[-1]["end_frame"] = frame_to_time((frame_count - 5), frame_rate)
                first = False
                # print(current_subtitle_text + " from frame: " + str(frame_count))

                subtitle_data.append(
                    {
                        "title" : current_subtitle_text if (current_subtitle_text != "nothing") else "",
                        "start_frame": frame_to_time((frame_count), frame_rate)
                    }
                )
    else:
        break
    frame_count += 1

# print(" to frame count " + str(frame_count))
subtitle_data[-1]["end_frame"] = frame_to_time((frame_count), frame_rate)

subtitle_data = [item for item in subtitle_data if item['title'] != '']
print(subtitle_data)

#550 frames total for subtitle extractor test.mp4
# Release the VideoCapture
video.release()
cv2.destroyAllWindows()


end_time = time.time()
execution_time = end_time - start_time
print(f"The program took {execution_time} seconds to complete.")

print(str(ocr_seconds) + " total ocr time")