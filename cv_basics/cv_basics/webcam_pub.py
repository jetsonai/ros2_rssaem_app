#!/usr/bin/env python3

# Copyright 2024 JetsonAI CO., LTD.
#
# Author: Kate Kim

import rclpy 
from rclpy.node import Node 
from sensor_msgs.msg import Image 
import cv2 
from cv_bridge import CvBridge, CvBridgeError

gst_str = ("nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)480, format=(string)NV12, framerate=(fraction)60/1 ! nvvidconv flip-method=2 ! video/x-raw, width=(int)640, height=(int)480, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")
 
class ImagePublisher(Node):

    def __init__(self):
        super().__init__('image_publisher')  
        self.publisher_ = self.create_publisher(Image, 'video_frames', 10)
        timer_period = 0.001  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info('create_timer')
        self.cap = cv2.VideoCapture(gst_str)
        self.get_logger().info('VideoCapture')
        self.br = CvBridge()
   
    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret == True:
            self.publisher_.publish(self.br.cv2_to_imgmsg(frame))
            #cv2.imshow("camera", frame)
            #cv2.waitKey(0.001)

        self.get_logger().info('Publishing video frame')


def main(args=None):
    rclpy.init(args=args)
    image_publisher = ImagePublisher()
    
    rclpy.spin(image_publisher)

    cap.release()
    cv2.destroyAllWindows() 
     
    image_publisher.destroy_node()
    rclpy.shutdown()
  
if __name__ == '__main__':
    main()

# ros2 run cv_basics img_publisher
    
