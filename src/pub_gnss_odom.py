#!/usr/bin/env python
#coding=utf-8

import numpy 
import rospy
import requests
import json
from sensor_msgs.msg import NavSatFix 
from nav_msgs.msg import Odometry

#original point
E0 = 0.0
N0 = 0.0
U0 = 0.0
flag_initial = False
    
def get_gnss_info (msg):
    global flag_initial
    global E0
    global N0
    global U0
    lat_str = str(msg.latitude)
    lon_str = str(msg.longitude)
    h_str = str(msg.altitude)
    string = "http://www.geodetic.gov.hk/transform/v2/?inSys=wgsgeog&outSys=hkgrid&lat="+lat_str+"&long="+lon_str+"&h="+h_str
    response = requests.get(string)
    result = response.json()
    E = result['hkE']
    N = result['hkN']
    U = result['hkpd']
    if not flag_initial:
        flag_initial = True
        E0 = E
        N0 = N
        U0 = U
        E = 0.0
        N = 0.0
        U = 0.0
        print("GNSS Initialised!")
    else:
        E = E - E0
        N = N - N0
        U = U - U0
    gnss_odom =  Odometry()
    gnss_odom.header = msg.header
    gnss_odom.header.frame_id = "odom"
    gnss_odom.pose.pose.position.x = E
    gnss_odom.pose.pose.position.y = N
    gnss_odom.pose.pose.position.z = U
    gnss_odom.pose.pose.orientation.w = 1.0
    gnss_odom.pose.covariance[0] = msg.position_covariance[0]
    gnss_odom.pose.covariance[7] = msg.position_covariance[4]
    gnss_odom.pose.covariance[14] = msg.position_covariance[8]
    pub_GNSS_fix.publish(gnss_odom)
 
if __name__ == '__main__':
    rospy.init_node('pub_gnss_odom')
    pub_GNSS_fix = rospy.Publisher('/odometry/gps', Odometry, queue_size=200)
    sub = rospy.Subscriber ('/gnss_fix', NavSatFix, get_gnss_info, queue_size=200)
    rospy.spin()
