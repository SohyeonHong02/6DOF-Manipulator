#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float32MultiArray
from sensor_msgs.msg import JointState

class JAConverterNode:
    def __init__(self):
        rospy.init_node('ja_converter_node')
        self.degree_sub = rospy.Subscriber('/ja_degree', Float32MultiArray, self.degree_callback)
        self.joint_pub = rospy.Publisher('/joint_states', JointState, queue_size=100)
        
    def degree_callback(self, msg):
        joint_state_msg = JointState()
        joint_state_msg.header.stamp = rospy.Time.now()
        joint_state_msg.name = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']  # Joint 이름을 적절하게 변경해주세요.
        joint_state_msg.position = msg.data  # 받은 ja_degree 값을 position 필드에 대입합니다.
        joint_state_msg.velocity = [0.8,0.8,0.8,0.8,0.8,]
        self.joint_pub.publish(joint_state_msg)
        
    def run(self):
        rate = rospy.Rate(1)  # 발행 속도를 조정할 수 있습니다.
        while not rospy.is_shutdown():
            rate.sleep()

if __name__ == '__main__':
    try:
        converter_node = JAConverterNode()
        converter_node.run()
    except rospy.ROSInterruptException:
        pass

