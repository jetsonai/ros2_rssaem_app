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
from PIL import Image as PILImage  # sensor_msgs.msg.Image 와 이름 충돌 방지
import numpy as np

# 패키지 이름을 몰라서 일단 평범한 import로 둡니다.
# config.py 를 이 노드가 속한 ROS2 패키지의 안쪽 모듈 폴더(cv_basics.config 때와 동일한 위치)에
# 넣으신 뒤, 패키지 이름에 맞게 예: `from yolo_test.config import get_capture` 로 바꿔주세요.
from config import get_capture

ultralytics.checks()

from ultralytics import YOLO

trt_model = YOLO("/home/rssaem/CHECK/yolo26s.engine")

def main(args=None):

    rclpy.init()
    node = rclpy.create_node("yolo_node")

    global bridge
    bridge = CvBridge()

    # 젯슨이면 CSI(nvarguscamerasrc), 그 외(일반 PC/WSL)면 USB 웹캠(index 0)을 자동으로 사용.
    # 강제로 지정하려면 get_capture(force="jetson") / get_capture(force="usb") 사용,
    # 또는 CAMERA_BACKEND=usb / jetson 환경변수로 지정 가능 (config.py 참고).
    cap = get_capture()
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
