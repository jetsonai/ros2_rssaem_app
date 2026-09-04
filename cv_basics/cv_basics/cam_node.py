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


def main(args=None):

    rclpy.init()
    node = rclpy.create_node("cam_viewer")

    global bridge
    bridge = CvBridge()

    # 젯슨이면 CSI(nvarguscamerasrc), 그 외(일반 PC)면 USB 웹캠(index 0)을 자동으로 사용.
    # 강제로 지정하려면 get_capture(force="jetson") / get_capture(force="usb") 사용,
    # 또는 실행 시 CAMERA_BACKEND=usb 같은 환경변수로 지정 가능 (config.py 참고).
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
        cv2.imshow('preview',frame)
        #print('view video frame')
        # Waits for a user input to quit the application
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
