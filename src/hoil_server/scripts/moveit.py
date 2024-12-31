#!/usr/bin/env python3

import sys
import moveit_commander
import rospy
from math import pi
import geometry_msgs.msg
import copy
from tf.transformations import quaternion_from_euler

moveit_commander.roscpp_initialize(sys.argv)
rospy.init_node('move_group_tut', anonymous= True)

robot = moveit_commander.RobotCommander()
scene = moveit_commander.PlanningSceneInterface()

group_name = 'arm'
group = moveit_commander.MoveGroupCommander(group_name)

arm_name = 'gripper'
arm_group = moveit_commander.MoveGroupCommander(arm_name)

plan_frame = group.get_planning_frame()
eef_link = group.get_end_effector_link()

print(f'Ref frame: {plan_frame}')
print(f'eef frame: {eef_link}')

q = quaternion_from_euler(0, pi, pi/2)
print(q)
pose_goal = geometry_msgs.msg.Pose()
pose_goal.orientation.x = q[0]
pose_goal.orientation.y = q[1]
pose_goal.orientation.z = q[2]
pose_goal.orientation.w = q[3]

pose_goal.position.x = 0.0
pose_goal.position.y = 0.5
pose_goal.position.z = 0.5
group.set_pose_target(pose_goal)

group.go(wait= True)
group.stop()
print('plan end')

# Clear target pose
group.clear_pose_targets()
print('clear pose')

arm_group.set_named_target('Open')
arm_group.go(wait= True)


print(group.get_current_pose())
print(group.get_current_rpy())
