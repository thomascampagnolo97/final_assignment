#! /usr/bin/env python3

import rospy
import numpy
import time
from geometry_msgs.msg import Twist, Vector3    #for cmd_vel topic
from sensor_msgs.msg import LaserScan           #for scan topic


threshold = 0.7 # limit distance to avoid collision with obstacles
vel_msg = Twist()   # initialize Twist object for the publisher

class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
   

'''
    Function called each time arrives a message from the LaserScan topic.
    This function gets the minimum value among 5 regions of the laser scan 
    and take a decision setting the velocity to avoid obstacles.
''' 
def assisted_driving(data):
    global section, vel_msg

    # Initialize publisher
    pub_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

    # section the ranges array in 5 parts and store the minimum value (distance) for each of them  
    section = {
        'right':  min(data.ranges[0:143]),
        'fright': min(data.ranges[144:287]),
        'front':  min(data.ranges[288:431]),
        'fleft':  min(data.ranges[432:575]),
        'left':   min(data.ranges[576:719]),
    }

    # states to avoid dangerous situations with obstacles
    # Ostacle on the right of the robot
    if section['right'] < threshold:
        # Allow only rotation on the left
        if vel_msg.linear.x == 0 and vel_msg.angular.z < 0:
            vel_msg.linear.x = 0    # Reset linear velocity
            vel_msg.angular.z = 0   # Reset angular velocity

    # Ostacle on the front-right of the robot    
    elif section['fright'] < threshold:
        # Allow only rotation on the left
        if vel_msg.linear.x > 0 and vel_msg.angular.z < 0:
            vel_msg.linear.x = 0    # Reset linear velocity
            vel_msg.angular.z = 0   # Reset angular velocity

    # Ostacle in front of the robot
    elif section['front'] < threshold:
        # Allow only rotation
        if vel_msg.linear.x > 0 and vel_msg.angular.z == 0:
            vel_msg.linear.x = 0 # Reset linear velocity

    # Ostacle on the front-left of the robot
    elif section['fleft'] < threshold: 
        # Allow only rotation on the right
        if vel_msg.linear.x > 0 and vel_msg.angular.z > 0:
            vel_msg.linear.x = 0    # Reset linear velocity
            vel_msg.angular.z = 0   # Reset angular velocity

    # Ostacle on the left of the robot
    elif section['left'] < threshold: 
        # Allow only rotation on the right
        if vel_msg.linear.x == 0 and vel_msg.angular.z > 0:
            vel_msg.linear.x = 0    # Reset linear velocity
            vel_msg.angular.z = 0   # Reset angular velocity

    # Publish the new velocity
    pub_vel.publish(vel_msg)

'''
    Callback function to copy the new topic collision_cmd_vel on vel_msg 
    which can be modified or not
''' 
def callBack_remap(data):
    global vel_msg
    vel_msg = data

'''
    Function that initialises the subscribers for the assisted driving mode
'''   
def assisted_manual_drive():
    global sub_laser, sub_user_vel

    #initialize the node
    rospy.init_node('inputKey_node')
    # Initialize subscribers
    sub_user_vel = rospy.Subscriber('/collision_cmd_vel', Twist, callBack_remap) # subscriber to topic collision_cmd_vel 
    sub_laser = rospy.Subscriber('/scan', LaserScan, assisted_driving) # subscriber to topic scan

    rospy.spin()
    
#main 
if __name__=="__main__":
    assisted_manual_drive()