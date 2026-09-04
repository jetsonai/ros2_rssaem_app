#!/usr/bin/env python3

# Copyright 2024 JetsonAI CO., LTD.
#
# Author: Kate Kim

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

import cv2
from sensor_msgs.msg import CompressedImage

from cv_basics.config import get_capture


class ImagePublisher(Node):
    def __init__(self):
        super().__init__('webcam_comp_pub')

        # 센서 데이터에 흔히 쓰는 QoS (네트워크/브리지 환경에서 유리한 편)
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

        timer_period = 0.033  # 30Hz 권장 (원본 0.001s는 로그/CPU 과부하 유발 가능)
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # 젯슨이면 CSI(nvarguscamerasrc), 그 외(일반 PC)면 USB 웹캠(index 0)을 자동으로 사용.
        # 강제로 지정하려면 get_capture(force="jetson") / get_capture(force="usb") 사용,
        # 또는 실행 시 CAMERA_BACKEND=usb 같은 환경변수로 지정 가능 (config.py 참고).
        self.cap = get_capture()
        if not self.cap.isOpened():
            self.get_logger().error('Failed to open camera.')
        else:
            self.get_logger().info('Camera opened.')

        # JPEG 품질(0~100). 네트워크 상황에 따라 60~90 사이 조절
        self.jpeg_quality = 80

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn('Failed to read frame.')
            return

        # JPEG 압축
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(self.jpeg_quality)]
        ok, jpg = cv2.imencode('.jpg', frame, encode_param)
        if not ok:
            self.get_logger().warn('Failed to encode frame to JPEG.')
            return

        msg = CompressedImage()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera'
        msg.format = 'jpeg'
        msg.data = jpg.tobytes()

        self.publisher_.publish(msg)
        # 너무 잦은 로그는 성능 저하가 큼 → 필요 시 주석 해제/간헐 출력 추천
        # self.get_logger().info('Publishing /camera/image_raw/compressed')

def main(args=None):
    rclpy.init(args=args)
    node = ImagePublisher()

    try:
        rclpy.spin(node)
    finally:
        if hasattr(node, 'cap') and node.cap is not None:
            node.cap.release()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
