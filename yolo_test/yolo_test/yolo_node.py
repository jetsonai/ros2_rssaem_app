#!/usr/bin/env python3

# Copyright 2024 JetsonAI CO., LTD.
#
# Author: Kate Kim

import rclpy 
from rclpy.node import Node 
from sensor_msgs.msg import Image 
import cv2 
from cv_bridge import CvBridge, CvBridgeError

import ultralytics
from PIL import Image
import numpy as np

gst_str = ("nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)480, format=(string)NV12, framerate=(fraction)60/1 ! nvvidconv flip-method=2 ! video/x-raw, width=(int)640, height=(int)480, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")

ultralytics.checks()

from ultralytics import YOLO

trt_model = YOLO("/home/rssaem/CHECK/yolo26s.engine")

def main(args=None):
  
    rclpy.init()
    node = rclpy.create_node("yolo_node")

    global bridge
    bridge = CvBridge()

    #cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture(gst_str)
    if not (cap.isOpened()):
        print("Could not open video device")
    # To set the resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        # Display the resulting frame
        #cv2.imshow('preview',frame)
        if ret:
            
            results = trt_model.predict(frame)
            annotated_frame = results[0].plot()
            cv2.imshow("YOLO Node", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

    node.destroy_node()
    rclpy.shutdown()
  
if __name__ == '__main__':
  main()

# ros2 run cv_basics cam_node
