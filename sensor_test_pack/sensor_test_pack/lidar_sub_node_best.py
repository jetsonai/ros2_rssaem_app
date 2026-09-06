#!/usr/bin/env python3

# Copyright 2026 JetsonAI CO., LTD.
#
# Author: Kate Kim
# ros2 run sensor_test_pack lidar_node_best

import rclpy # Python library for ROS 2
from rclpy.node import Node # Handles the creation of nodes
from sensor_msgs.msg import LaserScan 
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

ranges_list = []
 
class LidarSubscriber(Node):

    def __init__(self):
        super().__init__('lidar_sub_node')

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

    def listener_callback(self, data):
        global ranges_list
        ranges_list = data.ranges

        #self.get_logger().info("len(ranges_list) : {}".format(len(ranges_list)))
        bSafe = self.safeDistance(ranges_list) 
 
    def safeDistance(self, ranges):
        bSafe = 0
        safe_dist = 0.4
        maxlen= len(ranges)
        if maxlen > 90:
            bSafe = 1
            for f in range(maxlen - 30 ,maxlen):
                if(ranges[f] <= safe_dist and ranges[f] != 0.0):
                    bSafe = 0
                    self.get_logger().info("<WARNING> ranges[{}] : {:.2f}".format(f, ranges[f]))
                    break
            if(bSafe == 1):
                for f in range(0,30):
                    if(ranges[f] <= safe_dist and ranges[f] != 0.0):
                        bSafe = 0
                        self.get_logger().info("<WARNING> ranges[{}] : {:.2f}".format(f, ranges[f]))
                        break
        print("bSafe:{}".format(bSafe))
        return bSafe

def main(args=None):

    rclpy.init(args=args)
    lidar_subscriber = LidarSubscriber() 
    rclpy.spin(lidar_subscriber)
    lidar_subscriber.destroy_node()
    rclpy.shutdown()
  
if __name__ == '__main__':
    main()
