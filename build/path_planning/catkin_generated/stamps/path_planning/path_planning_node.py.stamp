#!/usr/bin/env python3

import rospy
from std_msgs.msg import String, Float32MultiArray
from geometry_msgs.msg import PoseStamped, TwistStamped
from nav_msgs.msg import Path
import math
#from actionlib import SimpleActionServer
#from ros_action.msg import ros_actionAction

class path_planningNode:
    def __init__(self):
        rospy.loginfo("Start initialization")
        self.pose_pub = rospy.Publisher('/ee_pose_desired', PoseStamped, queue_size=1)
        self.trajectory_pub = rospy.Publisher('/trajectory', Path, queue_size=1)
        self.pose_sub = rospy.Subscriber('/ee_state', PoseStamped, self.cartesianPoseCallBack)
        #self.twist_sub = rospy.Subscriber('/ee_state_dot', TwistStamped, self.cartesianTwistCallBack)
        self.desired_position_sub = rospy.Subscriber('/desired_position', PoseStamped, self.desired_position_callback, 1)
        self.trajectory_cur_ = Path()

        self.degree_pub = rospy.Publisher('/ee_degree', Float32MultiArray, queue_size=1) ##나중에 지우기

        self.twist_cur_ = TwistStamped()
        self.twist_cur_.twist.linear.x = 5.0
        self.twist_cur_.twist.linear.y = 5.0
        self.twist_cur_.twist.linear.z = 5.0

        #self.trajectory_cur_.header.frame_id = "ur5e_mount_link"
        #self.pose_cur_ = 0.0
        #self.twist_cur_ = 0.0
        #self.desired_x = 0.0
        #self.desired_y = 0.0
        #self.desired_z = 0.0
        #self.action_name = rospy.get_name()
        #self.server = SimpleActionServer(self.action_name, ros_actionAction, execute_cb=self.executeCB, auto_start=False)
        #self.server.start()
        #geometry_mtrajectory_cur_sgs::PoseStamped pose_cur_; // current cartesian pose
        #geometry_msgs::TwistStamped twist_cur_; // current cartesian twist
        #nav_msgs::Path trajectory_cur_; // current trajectory

        rospy.loginfo("Finish initialization")

    def cartesianPoseCallBack(self, msg):
        pose_cur = msg
        self.pose_cur_ = pose_cur
        rospy.loginfo("poseCB: (%f, %f, %f)", self.pose_cur_.pose.position.x, self.pose_cur_.pose.position.y, self.pose_cur_.pose.position.z)
        return
    
    """
    def cartesianTwistCallBack(self, msg):
        twist_cur = msg
        self.twist_cur_ = twist_cur
        rospy.loginfo("twistCB: %f", twist_cur.twist.linear.x)
        return
    """

    def desired_position_callback(self, msg, a):
        desired = msg
        self.desired_x = desired.pose.position.x
        self.desired_y = desired.pose.position.y
        self.desired_z = desired.pose.position.z
        #self.desired_w = msg.pose.orientation.w

        
        rospy.loginfo("twistCB: (%f, %f, %f)", self.twist_cur_.twist.linear.x, self.twist_cur_.twist.linear.y, self.twist_cur_.twist.linear.z)
        rospy.loginfo("desiredCB: (%f, %f, %f)", self.desired_x, self.desired_y, self.desired_z)

        if self.pose_cur_ is not None:
            self.executeCB()

    def comparePosition(self, pose_tar, pose_cur):
        if pose_tar.pose.position.x != self.pose_cur_.pose.position.x:
            return False
        if pose_tar.pose.position.y != self.pose_cur_.pose.position.y:
            return False
        if pose_tar.pose.position.z != self.pose_cur_.pose.position.z:
            return False
        return True
    

    def executeCB(self):
        # Initialization
        loop_rate = rospy.Rate(1000)
        success = True

        # Get target position from ROS action goal
        dist=math.sqrt(pow(self.desired_x-self.pose_cur_.pose.position.x,2)+pow(self.desired_y-self.pose_cur_.pose.position.y,2)+pow(self.desired_z-self.pose_cur_.pose.position.z,2))
        pose_tar = PoseStamped()
        execute_duration = 0.1 * (dist / 8)  # Execute interpolation for 5 seconds
        pose_tar.header.frame_id = "ee_link"
        pose_tar.header.stamp = rospy.Time.now() + rospy.Duration(execute_duration)
        # Set position and orientation information
        pose_tar.pose.position.x = self.desired_x
        pose_tar.pose.position.y = self.desired_y
        pose_tar.pose.position.z = self.desired_z
        pose_tar.pose.orientation.w = 1

        # Set time and position for interpolation
        time_start = rospy.Time.now()
        time_end = pose_tar.header.stamp
        pose_start = self.pose_cur_
        twist_start = self.twist_cur_
        pose_goal = PoseStamped()  # ROS message that will be sent to the Cartesian pose controller
        pose_goal.pose.orientation = pose_start.pose.orientation  # Maintain its orientation
        x_start, y_start, z_start = pose_start.pose.position.x, pose_start.pose.position.y, pose_start.pose.position.z
        x_dot_start, y_dot_start, z_dot_start = twist_start.twist.linear.x, twist_start.twist.linear.y, twist_start.twist.linear.z
        x_end, y_end, z_end = pose_tar.pose.position.x, pose_tar.pose.position.y, pose_tar.pose.position.z
        rospy.loginfo("Start time %f, end time: %f, duration: %f", time_start.to_sec(), time_end.to_sec(), time_end.to_sec() - time_start.to_sec())
        rospy.loginfo("Current position of the end_effector: x = %f, y = %f, z = %f", pose_start.pose.position.x, pose_start.pose.position.y, pose_start.pose.position.z)
        rospy.loginfo("Target position of the end_effector: x = %f, y = %f, z = %f", pose_tar.pose.position.x, pose_tar.pose.position.y, pose_tar.pose.position.z)
        rospy.loginfo("Execute callback function for interpolating")

        self.a = Float32MultiArray()
        self.a.data = []
        self.a.data = [0,0,0,0,0,0]
            
        self.degree_pub.publish(self.a) #STM 상에서 최초 현재 관절각 먼저 보내고 다음으로 중간좌표 계속 보내주기
        rospy.loginfo("degree pub")

        # Loop for request
        while not self.comparePosition(pose_tar, self.pose_cur_):
            #rospy.loginfo("compare position loop for interpolating")

            time_cur = rospy.Time.now()
            if (time_cur.to_sec() - time_start.to_sec()) <= 0:  # If current time is earlier than start time
                pose_goal = self.pose_cur_
                rospy.loginfo("current time is earlier than start time")

            elif (time_cur.to_sec() - time_end.to_sec()) >= 0:  # If interpolation is done
                pose_goal = pose_tar
                self.pose_pub.publish(pose_goal)  # Publish command
                rospy.loginfo("publish pose_goal and finish the compare position loop")
                break  # Finish the loop
            else:
                x_goal = x_start + x_dot_start * (time_cur.to_sec() - time_start.to_sec()) + \
                         (3.0 * (x_end - x_start) / (pow((time_end.to_sec() - time_start.to_sec()), 2))) * pow((time_cur.to_sec() - time_start.to_sec()), 2) + \
                         (-2.0 * x_dot_start / (time_end.to_sec() - time_start.to_sec())) * pow((time_cur.to_sec() - time_start.to_sec()), 2) + \
                         (-2.0 * (x_end - x_start) / (pow((time_end.to_sec() - time_start.to_sec()), 3))) * pow((time_cur.to_sec() - time_start.to_sec()), 3) + \
                         (x_dot_start / (pow((time_end.to_sec() - time_start.to_sec()), 2))) * pow((time_cur.to_sec() - time_start.to_sec()), 3)
                y_goal = y_start + y_dot_start * (time_cur.to_sec() - time_start.to_sec()) + \
                         (3.0 * (y_end - y_start) / (pow((time_end.to_sec() - time_start.to_sec()), 2))) * pow((time_cur.to_sec() - time_start.to_sec()), 2) + \
                         (-2.0 * y_dot_start / (time_end.to_sec() - time_start.to_sec())) * pow((time_cur.to_sec() - time_start.to_sec()), 2) + \
                         (-2.0 * (y_end - y_start) / (pow((time_end.to_sec() - time_start.to_sec()), 3))) * pow((time_cur.to_sec() - time_start.to_sec()), 3) + \
                         (y_dot_start / (pow((time_end.to_sec() - time_start.to_sec()), 2))) * pow((time_cur.to_sec() - time_start.to_sec()), 3)
                z_goal = z_start + z_dot_start * (time_cur.to_sec() - time_start.to_sec()) + \
                         (3.0 * (z_end - z_start) / (pow((time_end.to_sec() - time_start.to_sec()), 2))) * pow((time_cur.to_sec() - time_start.to_sec()), 2) + \
                         (-2.0 * z_dot_start / (time_end.to_sec() - time_start.to_sec())) * pow((time_cur.to_sec() - time_start.to_sec()), 2) + \
                         (-2.0 * (z_end - z_start) / (pow((time_end.to_sec() - time_start.to_sec()), 3))) * pow((time_cur.to_sec() - time_start.to_sec()), 3) + \
                         (z_dot_start / (pow((time_end.to_sec() - time_start.to_sec()), 2))) * pow((time_cur.to_sec() - time_start.to_sec()), 3)
                pose_goal.pose.position.x = x_goal
                pose_goal.pose.position.y = y_goal
                pose_goal.pose.position.z = z_goal

                if len(self.trajectory_cur_.poses) == 0:

                    self.trajectory_cur_.poses.append(pose_goal)
                
                i=0
                rospy.loginfo("[trajectory_cur_] x = %f", self.trajectory_cur_.poses[i].pose.position.x)
                #print(self.trajectory_cur_.poses[i].pose.position.x)
                i+=1

                #rospy.loginfo("[calculated pose_goal] x = %f, y = %f, z = %f", pose_goal.pose.position.x, pose_goal.pose.position.y, pose_goal.pose.position.z)
                
                rospy.loginfo("[calculated pose_goal] x = %f", pose_goal.pose.position.x)
                #rospy.loginfo("[trajectory_cur_] %f", self.trajectory_cur_.poses)


            rospy.loginfo("[Final publish pose_goal] x = %f, y = %f, z = %f", pose_goal.pose.position.x, pose_goal.pose.position.y, pose_goal.pose.position.z)
            
            loop_rate.sleep()

        # Send interpolated Intermediate coordinate value in path.poses[], list form
            
            
            self.trajectory_pub.publish(self.trajectory_cur_)

        # If finished, send success message to action client
        
        rospy.loginfo("Finish the interpolation of the manipulator")

        if success:
            #self.result.success = True
            rospy.loginfo("result_success_TRUE")
            rospy.loginfo(
                "Current position of the end_effector: x = %f, y = %f, z = %f", self.pose_cur_.pose.position.x,
                self.pose_cur_.pose.position.y, self.pose_cur_.pose.position.z)
            #self.as_.set_succeeded(self.result)
            self.trajectory_cur_ = Path()

def main():
    rospy.init_node("path_planning_node")
    node = path_planningNode()
    #node.main()
    #server = RosTopic("interpolation")
    rospy.spin()


if __name__ == "__main__":
    main()