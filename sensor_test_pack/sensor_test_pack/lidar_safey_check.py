#!/usr/bin/env python3

# Copyright 2026 JetsonAI CO., LTD.
#
# Author: Kate Kim
# colcon build --packages-select sensor_test_pack
# ros2 run sensor_test_pack lidar_sub_node

import rclpy # Python library for ROS 2
from rclpy.node import Node # Handles the creation of nodes
from sensor_msgs.msg import LaserScan 
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy
from std_msgs.msg import Int32  # Int32 메시지 타입

ranges_list = []
 
class LidarSubscriber(Node):

    def __init__(self):
        super().__init__('lidar_safey_check')

        # 1. '/scan' 구독 설정
        # qos = QoSProfile(
        #     reliability=QoSReliabilityPolicy.BEST_EFFORT,
        #     history=QoSHistoryPolicy.KEEP_LAST,
        #     depth=10,
        #     durability=QoSDurabilityPolicy.VOLATILE,
        # )
        qos = QoSProfile(depth=10)   
        self.subscription = self.create_subscription(
          LaserScan, 
          '/scan', 
          self.listener_callback, 
          qos_profile=qos)
        self.subscription # prevent unused variable warning

        # 2. 'safe_topic' 발행자 설정 추가
        self.publisher_safe = self.create_publisher(Int32, 'safe_topic', qos)
   
    def listener_callback(self, data):
        global ranges_list
        ranges_list = data.ranges

        #self.get_logger().info("len(ranges_list) : {}".format(len(ranges_list)))
        bSafe_value = self.safeDistance(ranges_list) 
        
        # 3. 결과값을 Int32 메시지로 담아 발행
        msg = Int32()
        msg.data = bSafe_value
        self.publisher_safe.publish(msg)
 
    def safeDistance(self, ranges):
        bSafe = 0
        safe_dist = 0.3
        maxlen= len(ranges)
        if maxlen > 90:
            bSafe = 1
            for f in range(maxlen - 40 ,maxlen):
                if(ranges[f] <= safe_dist and ranges[f] > 0.01):
                    bSafe = 0
                    self.get_logger().info("<WARNING> L ranges[{}] : {:.2f}".format(f, ranges[f]))
                    break
            if(bSafe == 1):
                for f in range(0,40):
                    if(ranges[f] <= safe_dist and ranges[f] > 0.01):
                        bSafe = 0
                        self.get_logger().info("<WARNING> R ranges[{}] : {:.2f}".format(f, ranges[f]))
                        break
        #print("bSafe:{}".format(bSafe))
        return bSafe



 
def main(args=None):

    rclpy.init(args=args)
    lidar_subscriber = LidarSubscriber() 
    rclpy.spin(lidar_subscriber)
    lidar_subscriber.destroy_node()
    rclpy.shutdown()
  
if __name__ == '__main__':
    main()
