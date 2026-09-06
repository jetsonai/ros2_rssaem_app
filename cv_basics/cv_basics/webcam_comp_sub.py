#!/usr/bin/env python3
# Copyright 2024 JetsonAI CO., LTD.
#
# Author: Kate Kim

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy
from sensor_msgs.msg import CompressedImage
import cv2
import numpy as np

class CompressedImageSubscriber(Node):
    def __init__(self):
        super().__init__('webcam_comp_sub')
        
        # 발행자(Publisher)와 동일한 QoS 프로필 설정 필수
        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
        )
        
        # 토픽: /camera/image_raw/compressed
        self.subscription = self.create_subscription(
            CompressedImage,
            '/camera/image_raw/compressed',
            self.listener_callback,
            qos)
        self.subscription  # prevent unused variable warning
        
        self.get_logger().info('Compressed Image Subscriber Node has been started.')

    def listener_callback(self, data):
        # 1. 수신된 바이트 데이터(data.data)를 1차원 numpy 배열로 변환
        np_arr = np.frombuffer(data.data, np.uint8)
        
        # 2. numpy 배열을 OpenCV 이미지(BGR 컬러)로 디코딩 (압축 해제)
        current_frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # 3. 디코딩된 이미지가 유효한 경우 화면에 출력
        if current_frame is not None:
            cv2.imshow("Compressed Camera Show", current_frame)
            cv2.waitKey(1)
        else:
            self.get_logger().warn('Failed to decode compressed image.')

def main(args=None):
    rclpy.init(args=args)
    node = CompressedImageSubscriber()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard Interrupt (SIGINT)')
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
