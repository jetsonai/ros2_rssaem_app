#!/usr/bin/env python3

# Copyright 2024 JetsonAI CO., LTD.
#
# Author: Kate Kim

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge, CvBridgeError

from cv_basics.config import get_capture


class ImagePublisher(Node):

    def __init__(self):
        super().__init__('image_publisher')
        self.publisher_ = self.create_publisher(Image, 'video_frames', 10)
        timer_period = 0.001  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info('create_timer')

        # 젯슨이면 CSI(nvarguscamerasrc), 그 외(일반 PC)면 USB 웹캠(index 0)을 자동으로 사용.
        # 강제로 지정하려면 get_capture(force="jetson") / get_capture(force="usb") 사용,
        # 또는 실행 시 CAMERA_BACKEND=usb 같은 환경변수로 지정 가능 (config.py 참고).
        self.cap = get_capture()
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

    image_publisher.cap.release()
    cv2.destroyAllWindows()

    image_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

# ros2 run cv_basics img_publisher
