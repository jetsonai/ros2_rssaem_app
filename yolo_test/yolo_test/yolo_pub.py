#!/usr/bin/env python3

# Copyright 2025 JetsonAI CO., LTD.
#
# Author: Kate Kim

import rclpy 
from rclpy.node import Node 
from sensor_msgs.msg import Image 
import cv2 
from cv_bridge import CvBridge, CvBridgeError

import ultralytics
import rclpy 
from rclpy.node import Node 
from sensor_msgs.msg import Image 
import cv2 
from cv_bridge import CvBridge, CvBridgeError

gst_str = ("nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)480, format=(string)NV12, framerate=(fraction)60/1 ! nvvidconv flip-method=2 ! video/x-raw, width=(int)640, height=(int)480, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")

ultralytics.checks()

from ultralytics import YOLO

trt_model = YOLO("/home/rssaem/CHECK/yolo26s.engine")
 
class YoloFramePublisher(Node):

    def __init__(self):
        super().__init__('yolo_pub')  
        self.publisher_ = self.create_publisher(Image, 'yolo_frames', 10)
        timer_period = 0.03  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info('create_timer')
        self.cap = cv2.VideoCapture(gst_str)
        self.get_logger().info('VideoCapture')
        self.br = CvBridge()
   
    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret == True:
            results = trt_model.predict(frame)
            annotated_frame = results[0].plot()
            cv2.imshow("YOLOv26", annotated_frame)
            self.publisher_.publish(self.br.cv2_to_imgmsg(annotated_frame))
            #cv2.waitKey(30)

        self.get_logger().info('Publishing yolo frame')


def main(args=None):
    rclpy.init(args=args)
    yolo_publisher = YoloFramePublisher()
    
    rclpy.spin(yolo_publisher)

    cap.release()
    cv2.destroyAllWindows() 
     
    yolo_publisher.destroy_node()
    rclpy.shutdown()
  
if __name__ == '__main__':
    main()

# ros2 run yolo_test yolo_test_pub
    
