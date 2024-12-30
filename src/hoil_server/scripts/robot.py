
import rospy
import moveit_commander

from geometry_msgs.msg import Pose, PoseStamped
from tf.transformations import quaternion_from_euler
from math import pi

# For instantiating a demo scene
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive

class RobotArm:
    def __init__(self):
        # Initialise components for Kinova arm
        self.hoilRosNode = rospy.init_node('hoil_execution_server', anonymous= False)
        self.scene = moveit_commander.PlanningSceneInterface()
        self.robot = moveit_commander.RobotCommander()
        self.arm_group = moveit_commander.MoveGroupCommander('arm')
        self.gripper_group = moveit_commander.MoveGroupCommander('gripper')
        self.arm_pose = Pose()

        # print(f'Hoil Server:: Initialising robot')
        # self.InitialiseDemoScene()
        # self.InitialRobotPose()
        # print(f'Hoil Server:: Initialisation finished')

        # print(f'Executing node')
        # self.MoveTo(0.5, 0.0, 0.5)
        # self.MoveBy(0.0, 0.0, -0.05)
        # self.CloseGripper()
        # self.arm_group.pick('obj')
        # self.MoveBy(0.0, 0.0, 0.05)
        # self.MoveTo(0.0, 0.5, 0.5)
        # self.MoveBy(0.0, 0.0, -0.05)
        # self.OpenGripper()
        # self.arm_group.place('obj')

        self.MoveBy(0.0, 0.0, 0.05)

    def InitialiseDemo(self):
        self.InitialiseDemoScene()
        self.InitialRobotPose()

    def InitialRobotPose(self) -> Pose:
        """Set the robot pose to the initial state"""
        p = Pose()
        q = quaternion_from_euler(0, pi, pi/2)

        p.orientation.x = q[0]
        p.orientation.y = q[1]
        p.orientation.z = q[2]
        p.orientation.w = q[3]
        p.position.x = 0.0
        p.position.y = 0.5
        p.position.z = 0.5

        self.arm_pose = p
        self.arm_group.set_pose_target(self.arm_pose)
        self.arm_group.go(wait= True)
        self.arm_group.clear_pose_targets()
        self.OpenGripper()
        return p
    
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

        tablePose = PoseStamped()
        tablePose.header.frame_id = 'root'
        tablePose.pose.position.x = 0.5
        tablePose.pose.position.y = 0.0
        tablePose.pose.position.z = 0.2

        tablePose2 = PoseStamped()
        tablePose2.header.frame_id = 'root'
        tablePose2.pose.position.x = 0.0
        tablePose2.pose.position.y = 0.5
        tablePose2.pose.position.z = 0.2

        objPose = PoseStamped()
        objPose.header.frame_id = 'root'
        objPose.pose.position.x = 0.5
        objPose.pose.position.y = 0.0
        objPose.pose.position.z = 0.4



        self.scene.add_box('table1', tablePose, [0.2, 0.4, 0.4])
        self.scene.add_box('table2', tablePose2, [0.4, 0.2, 0.4])
        self.scene.add_box('obj', objPose, [0.02, 0.02, 0.1])