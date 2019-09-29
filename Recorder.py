################ Record video service ################
import cv2
import numpy as np
import threading
import os

videoCounter = 1
fileName = "output_264"
fileExt = ".mp4"
videoArray = []
quality = '28'                          # quality 0 best, 51 wrost
frame = 10                              # frame per seconds
videoLength = 300                       # videoLength / frame = length time
recordVideoFlg = False                  # recordVideo flag
t1 = threading.Thread()

cap = cv2.VideoCapture()

################ Rest Full Server Library ################

from flask import Flask, jsonify
from json import dumps
from gevent.pywsgi import WSGIServer

app = Flask(__name__)

def initialize():
    ################ Set camera source ################

    global cap
    cap = cv2.VideoCapture(0)   # to local webcam
    global recordVideoFlg
    recordVideoFlg = True

    global videoArray
    videoArray = []

def real_time_service():

    global recordVideoFlg
    global videoArray
    global videoLength
    global cap
 
    # Check if camera opened successfully. Otherwise exit
    if (cap.isOpened() == False): 
        print("Unable to read camera feed")

    while(recordVideoFlg):
      ret, frame = cap.read()
    
      if ret == True: 
        if (len(videoArray) >= videoLength):
            videoArray.pop(0)

        videoArray.append(frame)
    
      # Break the loop
      else:
        break 

def record_file():
    print("start record file")

    global frame

    # Default resolutions of the frame are obtained.The default resolutions are system dependent.
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    fourccLow = cv2.VideoWriter_fourcc(*'X264')

    global fileName
    global fileExt
    global videoCounter
    global quality

    name = fileName + fileExt
    videoCounter = videoCounter + 1

    outL = cv2.VideoWriter(name, fourccLow, frame, (frame_width, frame_height))

    global videoArray
    for frame in videoArray:
        outL.write(frame)

    outL.release()
    
    print("end record file")

# RestApi Server Call

@app.route('/api/recordFile')
def VideoAlarm():
    t2 = threading.Thread(target=record_file)
    t2.start()
    t2.join()
    return jsonify("File recorded")

@app.route('/api/start')
def StartVideoAlarmRecorder():
    
    initialize()

    global t1
    t1 = threading.Thread(target=real_time_service)
    t1.start()
    return jsonify("VideoAlarm Recorder started")

@app.route('/api/stop')
def StopVideoAlarmRecorder():
    global recordVideoFlg
    recordVideoFlg = False
    cap.release()

    # Closes all the frames
    cv2.destroyAllWindows() 
    return jsonify("VideoAlarm Recorder stopped")

if __name__ == '__main__':
    http_server = WSGIServer(('127.0.0.1', 5000), app)
    http_server.serve_forever()