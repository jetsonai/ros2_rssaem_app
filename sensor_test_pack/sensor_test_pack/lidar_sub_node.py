#!/usr/bin/env python3

# Copyright 2024 JetsonAI CO., LTD.
#
# Author: Kate Kim

import rclpy # Python library for ROS 2
from rclpy.node import Node # Handles the creation of nodes
from sensor_msgs.msg import LaserScan # 

 
class LidarSubscriber(Node):

    def __init__(self):
        super().__init__('lidar_sub_node')

        qos = 10
        self.subscription = self.create_subscription(
          LaserScan, 
          '/scan', 
          self.listener_callback, 
          qos)

        self.subscription # prevent unused variable warning
      

    def listener_callback(self, data):
        self.get_logger().info('Receiving lidar frame')

        global ranges_list
        ranges_list = data.ranges
        bsafe = self.safeDistance(ranges_list)
     
    def safeDistance(self, ranges):
        bSafe = 0
        if( len(ranges) > 90) :
            bSafe = 1
            for f in range(340,360):
                #print("ranges[{}] : {}".format(f, ranges[f]))
                if(ranges[f] <= 0.2 and ranges[f] != 0.0):
                    bSafe = 0
                    rospy.loginfo("<WARNING> ranges[{}] : {}".format(f, ranges[f]))
                    break
            if(bSafe == 1):
                for f in range(0,20):
                    #print("ranges[{}] : {}".format(f, ranges[f]))
                    if(ranges[f] <= 0.2 and ranges[f] != 0.0):
                        bSafe = 0
                        rospy.loginfo("<WARNING> ranges[{}] : {}".format(f, ranges[f]))
                        break
        print("bSafe:{}".format(bSafe))
        return bSafe
    
def main(args=None):

  rclpy.init(args=args)
  image_subscriber = LidarSubscriber() 
  rclpy.spin(image_subscriber)
  image_subscriber.destroy_node()
  rclpy.shutdown()
  
if __name__ == '__main__':
  main()
