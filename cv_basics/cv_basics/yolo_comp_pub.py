#!/usr/bin/env python3

# Copyright 2025 JetsonAI CO., LTD.
#
# Author: Kate Kim

import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge, CvBridgeError
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

import cv2
from sensor_msgs.msg import CompressedImage

import ultralytics

# 패키지 이름을 몰라서 일단 평범한 import로 둡니다.
# config.py 를 이 노드가 속한 ROS2 패키지의 안쪽 모듈 폴더에 넣으신 뒤,
# 패키지 이름에 맞게 예: `from yolo_test.config import get_capture` 로 바꿔주세요.
from config import get_capture

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

        # 젯슨이면 CSI(nvarguscamerasrc), 그 외(일반 PC/WSL)면 USB 웹캠(index 0)을 자동으로 사용.
        # 강제로 지정하려면 get_capture(force="jetson") / get_capture(force="usb") 사용,
        # 또는 CAMERA_BACKEND=usb / jetson 환경변수로 지정 가능 (config.py 참고).
        self.cap = get_capture()
        if not self.cap.isOpened():
            self.get_logger().error('Failed to open camera.')
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
