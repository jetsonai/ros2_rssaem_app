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
#from sensor_msgs.msg import Image 
from cv_bridge import CvBridge, CvBridgeError
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

import cv2
from sensor_msgs.msg import CompressedImage

gst_str = (
    "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)480, "
    "format=(string)NV12, framerate=(fraction)60/1 ! nvvidconv flip-method=2 ! "
    "video/x-raw, width=(int)640, height=(int)480, format=(string)BGRx ! "
    "videoconvert ! video/x-raw, format=(string)BGR ! appsink"
)

ultralytics.checks()

from ultralytics import YOLO

trt_model = YOLO("/home/rssaem/CHECK/yolo26n.engine")
 
class YoloFramePublisher(Node):

    def __init__(self):
        super().__init__('yolo_comp_pub')  
        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        # 토픽: /camera/image_raw/compressed
        self.publisher_ = self.create_publisher(
            CompressedImage,
            '/camera/image_raw/compressed',
            qos
        )
        timer_period = 0.033  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info('create_timer')
        self.cap = cv2.VideoCapture(gst_str)
        if not self.cap.isOpened():
            self.get_logger().error('Failed to open camera with GStreamer pipeline.')
        else:
            self.get_logger().info('Camera opened.')

        # JPEG 품질(0~100). 네트워크 상황에 따라 60~90 사이 조절
        self.jpeg_quality = 80        
        self.get_logger().info('VideoCapture')
        self.br = CvBridge()
   
    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn('Failed to read frame.')
            return
            
        results = trt_model.predict(frame)
        annotated_frame = results[0].plot()
        # JPEG 압축
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(self.jpeg_quality)]
        ok, jpg = cv2.imencode('.jpg', annotated_frame, encode_param)
        if not ok:
            self.get_logger().warn('Failed to encode frame to JPEG.')
            return

        msg = CompressedImage()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera'
        msg.format = 'jpeg'
        msg.data = jpg.tobytes()

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    yolo_publisher = YoloFramePublisher()
    
    try:
        rclpy.spin(yolo_publisher)
    finally:
        if hasattr(yolo_publisher, 'cap') and yolo_publisher.cap is not None:

            yolo_publisher.cap.release()
             
        yolo_publisher.destroy_node()
        rclpy.shutdown()
  
if __name__ == '__main__':
    main()

# ros2 run yolo_test yolo_test_pub
    
