#!/usr/bin/env python3

import numpy as np
from math import pi
import rospy
from std_msgs.msg import String, Bool, Float32MultiArray

from geometry_msgs.msg import PoseStamped, TwistStamped
from nav_msgs.msg import Path

class jacobianNode:
    def __init__(self):
        rospy.loginfo("Start initialization")
        self.degree_pub = rospy.Publisher('/ja_degree', Float32MultiArray, queue_size=1)
        self.mid_success_sub = rospy.Subscriber('/success', Bool, self.SuccessCallBack)
        self.trajectory_sub = rospy.Subscriber('/trajectory', Path, self.TrajectoryCallBack)
        self.pose_sub = rospy.Subscriber('/ee_degree', Float32MultiArray, self.CurDegreeCallBack)
        self.d_poses_q = Float32MultiArray()
        self.success = 0
        self.i = 0
        self.positions = [] 
        self.pose_cur_ = 0
        self.trajectory = Path()

        rospy.loginfo("Finish initialization")


    def SuccessCallBack(self, msg):
        self.success = 1
        return
    
    def CurDegreeCallBack(self, msg):
        #i=0

        pose_cur = msg
        #self.pose_cur_ = [0,0,0,0,0,0]
        self.pose_cur_ = pose_cur.data
        rospy.loginfo("cur_degreeCB1: (%f, %f, %f, %f, %f, %f)", self.pose_cur_[0], self.pose_cur_[1], self.pose_cur_[2], self.pose_cur_[3], self.pose_cur_[4], self.pose_cur_[5])

        
                
        return

    def TrajectoryCallBack(self, msg):
        self.trajectory = msg
        t_len = len(self.trajectory.poses)        
        print(t_len)


        """for i in range(t_len):
            x = self.trajectory.poses[i].pose.position.x
            y = self.trajectory.poses[i].pose.position.y
            z = self.trajectory.poses[i].pose.position.z

            self.positions=[x, y, z]"""

        # Now the positions list contains the extracted position values
        # You can use this list as needed in your code
        #self.i += 1

        #print(self.i)
        if self.pose_cur_ is not None:
            rospy.loginfo("cur_degreeCB2: (%f, %f, %f, %f, %f, %f)\n", self.pose_cur_[0], self.pose_cur_[1], self.pose_cur_[2], self.pose_cur_[3], self.pose_cur_[4], self.pose_cur_[5])

            
            
            q_0_0 = [0,0,0,0,0,0]

            for i in range(t_len):
                x = self.trajectory.poses[i].pose.position.x
                y = self.trajectory.poses[i].pose.position.y
                z = self.trajectory.poses[i].pose.position.z
                self.positions=[x, y, z]
                print(self.positions)

                self.traj_cur=[0,0,0,0,1,0]
                self.start_q_0 = [0,0,0,0,0,0]
                self.traj_cur[0] = self.positions[0]
                self.traj_cur[1] = self.positions[1]
                self.traj_cur[2] = self.positions[2]

                if i==0:
                    #현재 각 관절의 theta_start를 구하기위해 /ee_state 의 inverse 계산
                    #cur_position = (self.pose_cur_.pose.position.x, self.pose_cur_.pose.position.y, self.pose_cur_.pose.position.z,0,1,0)
                    
                    #self.start_q_0 = self.pseudo_inverse(theta_start = q_0_0, goal_position = cur_position, max_steps=100)

                    #interpolated된 중간값들을 goal_position으로 갱신하여 /trajectory_poses[i] inverse 계산
                    endeffector_goal_position = (self.traj_cur[0], self.traj_cur[1], self.traj_cur[2], 0,1,0)
                    poses_q = self.pseudo_inverse(theta_start = self.pose_cur_, goal_position=endeffector_goal_position, max_steps=25)
                    
                    self.start_q_0 = poses_q
                
                elif i>0:
                    
                    #interpolated된 중간값들을 goal_position으로 갱신하여 /trajectory_poses[i] inverse 계산
                    endeffector_goal_position = (self.traj_cur[0], self.traj_cur[1], self.traj_cur[2],0,1,0)
                    poses_q = self.pseudo_inverse(theta_start = self.start_q_0, goal_position=endeffector_goal_position, max_steps=25)
                    self.start_q_0 = poses_q
                
                array_to_send = (poses_q[0],poses_q[1], poses_q[2], poses_q[3], poses_q[4], poses_q[5])
                self.d_poses_q.data = array_to_send

                #print(f'Joint 1: {np.degrees(poses_q[0])}, Joint 2: {np.degrees(poses_q[1])}, Joint 3: {np.degrees(poses_q[2])}')
                #print(f'Joint 4: {np.degrees(poses_q[3])}, Joint 5: {np.degrees(poses_q[4])}, Joint 6: {np.degrees(poses_q[5])}')
                
                rospy.loginfo("[%d] publish to robot", i)
                self.degree_pub.publish(self.d_poses_q)
                rospy.sleep(0.01)
                
                # self.w
                # while not self.success :
                #     rospy.loginfo("wait for move")
                #     self.w = 1
                # rospy.loginfo("mid point move ends")
                # self.success = 0
            rospy.loginfo("finish publishing")

    
    

    def calculate_postion(self, Q):

        T1 = Q[0]
        T2 = Q[1]
        T3 = Q[2]
        T4 = Q[3]
        T5 = Q[4]
        T6 = Q[5]

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

        # tmpd01 = np.array([H0_1[0, 3], H0_1[1, 3], H0_1[2, 3]])
        # tmpd02 = np.array([H0_2[0, 3], H0_2[1, 3], H0_2[2, 3]])
        # tmpd03 = np.array([H0_3[0, 3], H0_3[1, 3], H0_3[2, 3]])
        # tmpd04 = np.array([H0_4[0, 3], H0_4[1, 3], H0_4[2, 3]])
        # tmpd05 = np.array([H0_5[0, 3], H0_5[1, 3], H0_5[2, 3]])
        # tmpd06 = np.array([H0_6[0, 3], H0_6[1, 3], H0_6[2, 3]])

        # positon_matrix = np.concatenate((tmpd01, tmpd02, tmpd03, tmpd04, tmpd05, tmpd06), axis=1)
        # print(H0_1)
        # print("-------------------")
        # print(H0_2)
        # print("-------------------")
        # print(H0_3)
        # print("-------------------")
        # print(H0_4)
        # print("-------------------")
        # print(H0_5)
        # print("-------------------")
        # print(H0_6)
        # print("-------------------")

        # for i in range(6):
        #     print("Tmatrix",i)
        #     print(H_matrices[i])
        #     print("-------------------")


        return H0_6#H0_6

    def calculate_jacobian_matrix(self, Q):


        T1 = Q[0]
        T2 = Q[1]
        T3 = Q[2]
        T4 = Q[3]
        T5 = Q[4]
        T6 = Q[5]

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


        # calculate the linear and angular components of the Jacobian matrix
        Z0 = np.array([0,0,1])
        Z1 = np.array(H0_1[0:3, 2])
        Z2 = np.array(H0_2[0:3, 2])
        Z3 = np.array(H0_3[0:3, 2])
        Z4 = np.array(H0_4[0:3, 2])
        Z5 = np.array(H0_5[0:3, 2])

        O0 = np.array([0,0,1])
        O1 = np.array(H0_1[0:3, 3])
        O2 = np.array(H0_2[0:3, 3])
        O3 = np.array(H0_3[0:3, 3])
        O4 = np.array(H0_4[0:3, 3])
        O5 = np.array(H0_5[0:3, 3])
        O6 = np.array(H0_6[0:3, 3])

        O6_0 = O6 - O0
        O6_1 = O6 - O1
        O6_2 = O6 - O2
        O6_3 = O6 - O3
        O6_4 = O6 - O4
        O6_5 = O6 - O5

        tmpjv1 = np.cross(Z0,O6_0)
        tmpjv2 = np.cross(Z1,O6_1)
        tmpjv3 = np.cross(Z2,O6_2)
        tmpjv4 = np.cross(Z3,O6_3)
        tmpjv5 = np.cross(Z4,O6_4)
        tmpjv6 = np.cross(Z5,O6_5)

        jv1 = tmpjv1.reshape(3, 1)
        jv2 = tmpjv2.reshape(3, 1)
        jv3 = tmpjv3.reshape(3, 1)
        jv4 = tmpjv4.reshape(3, 1)
        jv5 = tmpjv5.reshape(3, 1)
        jv6 = tmpjv6.reshape(3, 1)

        jw1 = Z0.reshape(3, 1)
        jw2 = Z1.reshape(3, 1)
        jw3 = Z2.reshape(3, 1)
        jw4 = Z3.reshape(3, 1)
        jw5 = Z4.reshape(3, 1)
        jw6 = Z5.reshape(3, 1)

        jacobian_matrix_v = np.concatenate((jv1, jv2, jv3, jv4, jv5, jv6), axis=1)
        jacobian_matrix_w = np.concatenate((jw1, jw2, jw3, jw4, jw5, jw6), axis=1)

        jacobian_matrix = np.concatenate((jacobian_matrix_v, jacobian_matrix_w), axis=0)

        return jacobian_matrix

    def pseudo_inverse(self, theta_start, goal_position, max_steps = np.inf):

        v_step_size =0.1  #0.1
        theta_max_step = 0.1  #0.3
        # 조인트 시작 값
        Q_j = theta_start
        #도착 xyz angular 값
        p_end = np.array([goal_position[0], goal_position[1], goal_position[2], 
                goal_position[3], goal_position[4], goal_position[5]])
        #시작 시 xyz angular 값
        p_H = self.calculate_postion(Q_j)
        p_r = p_H[:3, :3]
        s_w = np.array([[0], [1], [0]])
        p_w = p_r[:, :3].dot(s_w)
        p_p = np.array([p_H[0][3], p_H[1][3],p_H[2][3]])
        p_j = np.concatenate((p_p,p_w.flatten()),axis=0)

        delta_p = p_end - p_j
        j = 0

        while np.linalg.norm(delta_p) > 0.01 and j < max_steps:
            #print(f'j{j} : Q{Q_j} , P{p_j}')
            
            v_p = delta_p * v_step_size / np.linalg.norm(delta_p)
            J_j = self.calculate_jacobian_matrix(Q_j)
            J_invj = np.linalg.pinv(J_j)
            v_Q = np.matmul(J_invj,v_p)

            Q_j = Q_j + np.clip(v_Q,-1*theta_max_step,theta_max_step)
            p_H = self.calculate_postion(Q_j)
            p_r = p_H[:3, :3]
            s_w = np.array([[0], [1], [0]])
            p_w = p_r[:, :3].dot(s_w)
            p_p = np.array([p_H[0][3], p_H[1][3],p_H[2][3]])
            p_j = np.concatenate((p_p,p_w.flatten()),axis=0)

            j +=1

            delta_p = p_end - p_j
        #print(f'j{j} : Q{Q_j}')
        print(f'j{j} : P{p_j}')

        return Q_j



        # np.set_printoptions(precision=3, suppress=True)

def main():
    """q_0 = [0,0,0,0,0,0]
    
    endeffector_goal_position = (2,1,2,0,1,0)
    final_q = pseudo_inverse(theta_start = q_0, goal_position=endeffector_goal_position, max_steps=100)
    print(f'Joint 1: {np.degrees(final_q[0])}, Joint 2: {np.degrees(final_q[1])}, Joint 3: {np.degrees(final_q[2])}')
    print(f'Joint 4: {np.degrees(final_q[3])}, Joint 5: {np.degrees(final_q[4])}, Joint 6: {np.degrees(final_q[5])}')
    print(f'Joint 1: {final_q[0]}, Joint 2: {final_q[1]}, Joint 3: {final_q[2]}')
    print(f'Joint 4: {final_q[3]}, Joint 5: {final_q[4]}, Joint 6: {final_q[5]}')
    print(calculate_postion(final_q))
    """
    rospy.init_node("jacobian_node")
    node = jacobianNode()
    rospy.spin()

    #print(calculate_postion(q_0))    
    # #calculate_postion(q_0)
    #print(calculate_jacobian_matrix(q_0))

if __name__ == "__main__":
    main()

    # input
    # 시작할때 초기 관절 각도 입력
    # 골 포지션 값 입력
    # -------------------------------#

    #output
    #최종 관절 각도 출력