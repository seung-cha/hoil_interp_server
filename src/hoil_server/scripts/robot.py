
import rospy
import moveit_commander

from geometry_msgs.msg import Pose, PoseStamped
from tf.transformations import quaternion_from_euler
from math import pi

# For instantiating a demo scene
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive

import random

class SceneObject:
    def __init__(self, id: str, x= 0.0, y= 0.0, z= 0.0, height= 0.0):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.height = height


class RobotArm:
    def __init__(self):
        # Initialise components for Kinova arm
        self.hoilRosNode = rospy.init_node('hoil_execution_server', anonymous= False)
        self.scene = moveit_commander.PlanningSceneInterface()
        self.robot = moveit_commander.RobotCommander()
        self.arm_group = moveit_commander.MoveGroupCommander('arm')
        self.gripper_group = moveit_commander.MoveGroupCommander('gripper')
        self.arm_pose = Pose()
        self.scene_objects = self.InitialiseDemo()

        self.eef_link = self.arm_group.get_end_effector_link()
        print(self.arm_group.get_planning_frame())
        print(self.arm_group.get_end_effector_link())
        print(self.robot.get_group_names())
        print(self.arm_group.get_current_joint_values())
        print(self.robot.get_joint_names('arm'))


        # self.arm_group.detach_object()
        # self.MoveTo(0.0, 0.5, 0.45)
        # self.CloseGripper()
        # self.arm_group.attach_object('obj', self.eef_link)

        # self.MoveTo(0.5, 0.0, 0.5)
        # self.arm_group.detach_object()



    def InitialiseDemo(self):
        o = self.InitialiseDemoScene()
        self.InitialRobotPose()
        return o

    def InitialRobotPose(self) -> Pose:
        """Set the robot pose to the initial state"""
        p = Pose()
        q = quaternion_from_euler(0, pi, pi/2)

        p.orientation.x = q[0]
        p.orientation.y = q[1]
        p.orientation.z = q[2]
        p.orientation.w = q[3]
        p.position.x = 0.5
        p.position.y = 0.0
        p.position.z = 0.5

        self.arm_pose = p
        self.arm_group.set_pose_target(self.arm_pose)
        self.arm_group.go(wait= True)
        self.arm_group.clear_pose_targets()

        self.OpenGripper()

        # Rotate the arm gripper
        # g = self.arm_group.get_current_joint_values()
        # g[5] = -1.57 # list of len = 6, last index is the rotation of the gripper

        # self.arm_group.go(g, wait= True)

        return self.arm_pose
    
    def MoveBy(self, x, y, z, wait= True):
        """Add x, y, z to current position"""
        cur_pose = self.arm_group.get_current_pose()
        p = Pose()
        p.position.x = cur_pose.pose.position.x + x
        p.position.y = cur_pose.pose.position.y + y
        p.position.z = cur_pose.pose.position.z + z
        p.orientation.x = cur_pose.pose.orientation.x
        p.orientation.y = cur_pose.pose.orientation.y
        p.orientation.z = cur_pose.pose.orientation.z
        p.orientation.w = cur_pose.pose.orientation.w

        self.arm_pose = p
        self.arm_group.set_pose_target(self.arm_pose)
        self.arm_group.go(wait= wait)
        self.arm_group.clear_pose_targets()

    def MoveTo(self, x, y, z, wait= True):
        """Assign x, y, z to robot position"""
        cur_pose = self.arm_group.get_current_pose()
        p = Pose()
        p.position.x = x
        p.position.y = y
        p.position.z = z
        p.orientation.x = cur_pose.pose.orientation.x
        p.orientation.y = cur_pose.pose.orientation.y
        p.orientation.z = cur_pose.pose.orientation.z
        p.orientation.w = cur_pose.pose.orientation.w

        self.arm_pose = p
        self.arm_group.set_pose_target(p)
        self.arm_group.go(wait= wait)
        self.arm_group.clear_pose_targets()

    def OpenGripper(self, wait= True):
        self.gripper_group.set_named_target('Open')
        self.gripper_group.go(wait= wait)
        self.gripper_group.clear_pose_targets()
    
    def CloseGripper(self, wait= True):
        self.gripper_group.set_named_target('Close')
        self.gripper_group.go(wait= wait)
        self.gripper_group.clear_pose_targets()

    def InitialiseDemoScene(self):
        self.scene.clear()
        out = []
        heights = random.sample(range(5), 5)

        for i in range(5):
            id = 'obj' + str(i)
            height = 0.05 + heights[i] * 0.1/5
            x =  (0.7/5) * i - 0.7/2
            y = 0.3
            z = 0.3 + height / 2

            objPose = PoseStamped()
            objPose.header.frame_id = 'root'
            objPose.pose.position.x = x
            objPose.pose.position.y = y
            objPose.pose.position.z = z
            self.scene.add_box(id, objPose, [0.02, 0.02, height])

            out.append(SceneObject(id= id, x= x, y= y, z= z, height= height))
        
        return out