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

# 패키지 이름을 몰라서 일단 평범한 import로 둡니다.
# config.py 를 이 노드가 속한 ROS2 패키지의 안쪽 모듈 폴더에 넣으신 뒤,
# 패키지 이름에 맞게 예: `from yolo_test.config import get_capture` 로 바꿔주세요.
from config import get_capture

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

        # 젯슨이면 CSI(nvarguscamerasrc), 그 외(일반 PC/WSL)면 USB 웹캠(index 0)을 자동으로 사용.
        # 강제로 지정하려면 get_capture(force="jetson") / get_capture(force="usb") 사용,
        # 또는 CAMERA_BACKEND=usb / jetson 환경변수로 지정 가능 (config.py 참고).
        self.cap = get_capture()
        self.get_logger().info('VideoCapture')
        self.br = CvBridge()

    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret == True:
            results = trt_model.predict(frame)
            annotated_frame = results[0].plot()
            cv2.imshow("YOLOv26", annotated_frame)
            # imshow 만 호출하고 waitKey 를 안 부르면 GUI 이벤트 루프가 안 돌아서
            # 창이 갱신되지 않거나 "응답 없음"으로 보일 수 있어 waitKey(1)을 살렸습니다.
            cv2.waitKey(1)
            self.publisher_.publish(self.br.cv2_to_imgmsg(annotated_frame))

        self.get_logger().info('Publishing yolo frame')


def main(args=None):
    rclpy.init(args=args)
    yolo_publisher = YoloFramePublisher()

    rclpy.spin(yolo_publisher)

    yolo_publisher.cap.release()
    cv2.destroyAllWindows()

    yolo_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

# ros2 run yolo_test yolo_test_pub
