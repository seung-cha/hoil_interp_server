
import rospy
import moveit_commander

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

from tf.transformations import quaternion_from_euler

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


# Turtlebot class
class RobotArm:
    def __init__(self):
        rospy.init_node("HOIL_exec_server")
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size= 10)
        self.odom_sub = rospy.Subscriber('/scan', LaserScan, self._OnScanPublished)
        self.sensor_data = LaserScan()

        self.vel_data = Twist()

        # Wait til subscribed to cmd_vel
        # 1 subscription from gazebo
        print('Waiting for 1 seconds to establish connections . . .')
        rospy.sleep(1.0)
        print('ready to execute!')

    def _OnScanPublished(self, data: LaserScan):
        #print(str(len(self.sensor_data.ranges)))
        self.sensor_data = data


    def Move(self, speed: float):
        self.vel_data.linear.x = speed
        self.cmd_pub.publish(self.vel_data)

    def RotateLeft(self, speed: float):
        speed = abs(speed)
        self.vel_data.angular.z = speed
        self.cmd_pub.publish(self.vel_data)

    def RotateRight(self, speed: float):
        speed = -abs(speed)
        self.vel_data.angular.z = speed
        self.cmd_pub.publish(self.vel_data)

    def StopAllAction(self):
        self.vel_data = Twist()
        self.cmd_pub.publish(self.vel_data)

    




