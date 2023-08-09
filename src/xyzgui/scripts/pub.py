#!/usr/bin/python3

import rospy
from std_msgs.msg import Float32MultiArray
import random

class RandomListPublisher:
    def __init__(self):
        rospy.init_node('random_list_publisher')
        self.pub = rospy.Publisher('/cur_degree', Float32MultiArray, queue_size=10)
        self.rate = rospy.Rate(1)  # 퍼블리시 주기 (1초에 한 번)

    def publish_random_list(self):
        while not rospy.is_shutdown():
            # 랜덤한 0과 1 사이의 값으로 이루어진 6개의 리스트 생성
            data = [0,0,0,0,0,0]

            # Float32MultiArray 메시지 생성 및 값 설정
            msg = Float32MultiArray()
            msg.data = data

            # 메시지 퍼블리시
            self.pub.publish(msg)

            self.rate.sleep()

if __name__ == '__main__':
    try:
        publisher = RandomListPublisher()
        publisher.publish_random_list()
    except rospy.ROSInterruptException:
        pass
