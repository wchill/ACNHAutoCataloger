import cv2
import sys
from image_processing import process_frame


if __name__ == '__main__':
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        print('Error opening camera')
        sys.exit(1)

    try:
        while True:
            ret, frame = capture.read()
            process_frame(frame)
            input()
    except KeyboardInterrupt:
        pass
    capture.release()