#!/usr/bin/env python3

# Copyright 2025 JetsonAI CO., LTD.
#
# Author: Kate Kim

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy
from sensor_msgs.msg import CompressedImage
import cv2
from cv_bridge import CvBridge, CvBridgeError

class YoloCompFrameSubscriber(Node):

  def __init__(self):
    super().__init__('yolo_comp_sub')

    # yolo_comp_pub.py 가 publish 할 때 쓰는 QoS와 맞춰줘야 정상적으로 붙습니다
    # (특히 reliability=BEST_EFFORT 는 양쪽이 같아야 함).
    qos = QoSProfile(
      history=QoSHistoryPolicy.KEEP_LAST,
      depth=10,
      reliability=QoSReliabilityPolicy.BEST_EFFORT,
      durability=QoSDurabilityPolicy.VOLATILE,
    )

    self.subscription = self.create_subscription(
      CompressedImage,
      '/camera/image_raw/compressed',
      self.listener_callback,
      qos)
    self.subscription # prevent unused variable warning

    self.br = CvBridge()

  def listener_callback(self, data):
    self.get_logger().info('Receiving compressed yolo frame')

    try:
      # JPEG 로 압축된 CompressedImage 를 cv2 프레임(BGR)으로 디코딩
      current_frame = self.br.compressed_imgmsg_to_cv2(data)
    except CvBridgeError as e:
      self.get_logger().warn(f'Failed to decode JPEG frame: {e}')
      return

    cv2.imshow("yolo comp show", current_frame)

    cv2.waitKey(30)

def main(args=None):

  rclpy.init(args=args)
  yolo_comp_subscriber = YoloCompFrameSubscriber()
  rclpy.spin(yolo_comp_subscriber)
  yolo_comp_subscriber.destroy_node()
  rclpy.shutdown()

if __name__ == '__main__':
  main()

# ros2 run yolo_test yolo_comp_sub
