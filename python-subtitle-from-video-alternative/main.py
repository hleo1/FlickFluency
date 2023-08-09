import sys
from paddleocr import PaddleOCR
import cv2
import logging
logging.disable(logging.CRITICAL)
import re
import os
import time


def delete_file(filename):
    # Check if the file exists
    if os.path.exists(filename):
        # Remove the file
        os.remove(filename)
        print(f"{filename} has been deleted.")
    else:
        print(f"The file {filename} does not exist.")

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

def time_to_frame(time_string, frame_rate):
    hours, minutes, seconds, milliseconds = map(int, time_string.replace(',', ':').split(':'))
    total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
    frame_number = round(total_seconds * frame_rate)
    return frame_number

def quartiles(start, end):
    # Calculate the quartiles
    lower_quartile = start + 0.25 * (end - start)
    median = start + 0.5 * (end - start)
    upper_quartile = start + 0.75 * (end - start)

    return [round(lower_quartile), round(median), round(upper_quartile)]

def convert_srt(file_path):
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            block = []
            for line in f:
                if line.strip() == '':
                    if block:
                        index, time, *text = block
                        start, end = map(str.strip, time.split('-->'))
                        data.append({
                            'text': ' '.join(text),
                            'start': start,
                            'end': end,
                            'start_frame': time_to_frame(start, 25),
                            'end_frame': time_to_frame(end, 25),
                            'frames': quartiles(time_to_frame(start, 25), time_to_frame(end, 25))
                        })
                        block = []
                else:
                    block.append(line.strip())
            # For last block
            if block:
                index, time, *text = block
                start, end = map(str.strip, time.split('-->'))
                data.append({
                    'text': ' '.join(text),
                    'start': start,
                    'end': end,
                    'start_frame': time_to_frame(start, 25),
                    'end_frame': time_to_frame(end, 25),
                    'frames': quartiles(time_to_frame(start, 25), time_to_frame(end, 25))
                })


        with open('subtitle.txt', 'a', encoding='utf-8') as f:
            f.write(str(data))
        return data
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
    except IOError as e:
        print(f"An I/O error occurred: {str(e)}")

def start_frame_to_index(data) :
    result = {}
    for idx, dat in enumerate(data) :
        result[dat["frames"][0]] = idx
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please provide a file path as argument.")
    else:
        data_array = convert_srt(sys.argv[1])
        start_frame_hm = start_frame_to_index(data_array)

        file_name = "cutter_test.mp4"
        # Open video file
        video = cv2.VideoCapture(file_name)

        frame_array = []
        three_subtitles_with_accuracy = []
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
                cv2.imwrite(f'assets/{frame_count}.jpg', frame)  
                # if frame_count in start_frame_hm.keys():
                #     index = start_frame_hm[frame_count]
                #     frame_array = data_array[index]['frames']
                
                # if frame_count in frame_array:
                #     image_name = f'assets/capture.jpg'
                #     cv2.imwrite(image_name, frame)     
                #     result = ocr_output(image_name)
                #     three_subtitles_with_accuracy.append(result)


                # if(len(three_subtitles_with_accuracy) == 3) :
                #     print(frame_array)
                #     print(three_subtitles_with_accuracy)
                #     best_accuracy = 0
                #     best_text = ""
                #     for res in three_subtitles_with_accuracy :
                #         (text, accuracy) = res
                #         if (accuracy > best_accuracy) :
                #             best_accuracy = accuracy
                #             best_text = text
            
                #     three_subtitles_with_accuracy = []
                #     data_array[index]["chinese_text"] = best_text
            else:
                break
            frame_count += 1

        with open('end_result.txt', 'a', encoding='utf-8') as f:
            f.write(str(data_array))
        #550 frames total for subtitle extractor test.mp4
        # Release the VideoCapture
        video.release()
        cv2.destroyAllWindows()

        #                     print("progress: " + str(round(((frame_count / total_frames) * 100), 4)) + "%")