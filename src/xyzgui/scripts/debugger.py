#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
import rospy
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32MultiArray
import random
import numpy as np
from math import pi

class ROSPublisher(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ros()
        self.init_ui()

        self.r_poses_q = []

    def init_ros(self):
        rospy.init_node('pub_position', anonymous=True)
        self.pub = rospy.Publisher('/desired_position', PoseStamped, queue_size=10)
        #self.pub1 = rospy.Publisher('/present_position', PoseStamped, queue_size=10)
        self.pub1 = rospy.Publisher('/ee_state', PoseStamped, queue_size=10)

        self.pose_sub = rospy.Subscriber('/cur_degree', Float32MultiArray, self.CurDegreeCallBack)


    def init_ui(self):
        self.setGeometry(100, 100, 500, 300)  # 좌표 (100, 100), 크기 500x300

        self.setWindowTitle('manipulator_end_effoctor_position')

        layout = QVBoxLayout()
        self.setLayout(layout)

        x_label = QLabel('X:')
        self.x_input = QLineEdit()
        layout.addWidget(x_label)
        layout.addWidget(self.x_input)

        y_label = QLabel('Y:')
        self.y_input = QLineEdit()
        layout.addWidget(y_label)
        layout.addWidget(self.y_input)

        z_label = QLabel('Z:')
        self.z_input = QLineEdit()
        layout.addWidget(z_label)
        layout.addWidget(self.z_input)

        publish_button = QPushButton('Publish')
        publish_button.clicked.connect(self.publish_coordinates)
        layout.addWidget(publish_button)

        random_publish_button = QPushButton('Publish Random')
        random_publish_button.clicked.connect(self.publish_random_coordinates)
        layout.addWidget(random_publish_button)
        
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.status_label_random = QLabel()
        layout.addWidget(self.status_label_random)

        self.status_label1 = QLabel()
        layout.addWidget(self.status_label1)

    def CurDegreeCallBack(self,msg):
    
        self.r_poses_q = msg.data

        T1 = self.r_poses_q[0]
        T2 = self.r_poses_q[1]
        T3 = self.r_poses_q[2]
        T4 = self.r_poses_q[3]
        T5 = self.r_poses_q[4]
        T6 = self.r_poses_q[5]
        
        a6 = 1.0
        d3 = 2.5
        d5 = 2.0

        dh = [[T1+pi/2,  -pi/2,   0,      0],
            [T2+pi/2,   pi/2,   0,      0],
            [T3-pi/2,   pi/2,   d3,     0],
            [T4-pi/2,  -pi/2,   0,      0],
            [T5,        pi/2,   d5,     0],
            [T6+pi/2,      0,   0,     a6]
            ]
        
        # the homogenous transformation
        H_matrices = []
        for dh_row in dh:
            H = [
                [np.cos(dh_row[0]), -np.sin(dh_row[0])*np.cos(dh_row[1]), np.sin(dh_row[0])*np.sin(dh_row[1]), dh_row[3]*np.cos(dh_row[0])],
                [np.sin(dh_row[0]), np.cos(dh_row[0])*np.cos(dh_row[1]), -np.cos(dh_row[0])*np.sin(dh_row[1]), dh_row[3]*np.sin(dh_row[0])],
                [0, np.sin(dh_row[1]), np.cos(dh_row[1]), dh_row[2]],
                [0, 0, 0, 1]
            ]
            H_matrices.append(np.array(H))
        
        # calculate the composite transformation matrices
        H0_1 = H_matrices[0]
        H0_2 = np.dot(H0_1, H_matrices[1])
        H0_3 = np.dot(H0_2, H_matrices[2])
        H0_4 = np.dot(H0_3, H_matrices[3])
        H0_5 = np.dot(H0_4, H_matrices[4])
        H0_6 = np.dot(H0_5, H_matrices[5])


        x = H0_6[0][3]
        y = H0_6[1][3]
        z = H0_6[2][3]

        present_p = PoseStamped()
        present_p.pose.position.x = x
        present_p.pose.position.y = y
        present_p.pose.position.z = z
        
        rospy.loginfo("Published message: %s %s %s", x,y,z)

        self.status_label1.setText(f"로봇이 현재 \n x : {x}, \n y : {y}, \n z : {z} \t에 있습니다.")

        self.pub1.publish(present_p)


    def publish_coordinates(self):
        x = self.x_input.text()
        y = self.y_input.text()
        z = self.z_input.text()

        if x and y and z:
            try:
                x = float(x)
                y = float(y)
                z = float(z)

                coordinates = PoseStamped()
                coordinates.pose.position.x = x
                coordinates.pose.position.y = y
                coordinates.pose.position.z = z

                self.pub.publish(coordinates)

                self.status_label.setText(f"로봇이 {x}, {y}, {z}로 이동합니다.")
            except ValueError:
                self.status_label.setText("좌표를 올바르게 입력하세요.")
        else:
            self.status_label.setText("다른 좌표를 입력하세요.")

    def publish_random_coordinates(self):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        z = random.uniform(0, 1)

        coordinates = PoseStamped()
        coordinates.pose.position.x = x
        coordinates.pose.position.y = y
        coordinates.pose.position.z = z

        self.status_label.setText(f"로봇이 {x}, {y}, {z}로 이동합니다.")
        self.pub.publish(coordinates)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    publisher = ROSPublisher()
    publisher.show()
    sys.exit(app.exec_())
