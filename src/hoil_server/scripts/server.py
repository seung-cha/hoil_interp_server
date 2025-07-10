#!/usr/bin/env python

import hoil_utils as HoilUtils
from hoil_exec_node_builder import BuildExecNode
import sys
from hoil_exec_nodes import FunctionNode, NativeNode
from hoil_dtypes import DType

from robot import SceneObject
import rospy

# Given 5 sticks of different heights, sort them in ascending order on another table
# The sticks are located at <0, 0.25 ~ 0.5, height / 2>, and they must be sorted at <0.25 ~ 0.5, 0, ...>
# Boxes are stored in array 'boxes' (0 ~ 4), and height can be obtained via the function 'HeightOf'

# TO FIX: variable assignment with array results in no type. Assign a type
# If param and arg are identical, unexpected behaviour occurs.


class HoilServer:

    def __init__(self):
        # TODO: Create a ROSNode that feeds HOIL bytecode
        # TODO: Create a HOIL Function generation code
        file = sys.argv[1]
        with open(file, 'r') as f:
            data = f.read()


        self.container = HoilUtils.ExecVarContainer(noROS= False)

        # Insert functions
        FunctionNode.MakeFunction(self.container, 'Print', ['text'], ['str'],\
                                  NativeNode(self.container, self.Print))
        
        FunctionNode.MakeFunction(self.container, 'Delay', ['second'], 'real',\
                                  NativeNode(self.container, self.Delay))
        
        FunctionNode.MakeFunction(self.container, 'Move', ['speed'], ['real'],\
                                  NativeNode(self.container, self.Move))

        FunctionNode.MakeFunction(self.container, 'RotateLeft', ['speed'], ['real'],\
                                  NativeNode(self.container, self.RotateLeft))
        
        FunctionNode.MakeFunction(self.container, 'RotateRight', ['speed'], ['real'],\
                                  NativeNode(self.container, self.RotateRight))
        
        FunctionNode.MakeFunction(self.container, 'Stop', [], [],\
                                  NativeNode(self.container, self.Stop))
        
        FunctionNode.MakeFunction(self.container, 'DistanceAt', ['angle'], ['real'],\
                                  NativeNode(self.container, self.GetSensorReading))
        
        FunctionNode.MakeFunction(self.container, 'SenseLeft', ['dist'], ['real'],\
                                  NativeNode(self.container, self.SenseLeft))
        
        FunctionNode.MakeFunction(self.container, 'SenseRight', ['dist'], ['real'],\
                                  NativeNode(self.container, self.SenseRight))
        
        FunctionNode.MakeFunction(self.container, 'SenseForward', ['dist'], ['real'],\
                                  NativeNode(self.container, self.SenseForward))
        
        
        
        
        self.node = BuildExecNode(data, self.container)




        self.container.instructTable.Evaluate()

        print('Executing...')
        print('-' * 100)
        
        node = self.node

        while node is not None:
            node.Run()
            node = node.next

    def Print(self, container: HoilUtils.ExecVarContainer):
        """Native function. Print %text% to the screen."""
        s: DType
        s = container.varTable.Get('%text%')
        print(s.Get())

    def Delay(self, container: HoilUtils.ExecVarContainer):
        s: DType
        s = container.varTable.Get('%second%').Get()
        rospy.sleep(s)

    def Move(self, container: HoilUtils.ExecVarContainer):
        """Native function. Move the robot forward and backward"""
        s: DType
        s = container.varTable.Get('%speed%').Get()
        container.robot.Move(s)

    def RotateLeft(self, container: HoilUtils.ExecVarContainer):
        """Native function. Rotate the robot left"""
        s: DType
        s = container.varTable.Get('%speed%').Get()
        container.robot.RotateLeft(s)

    def RotateRight(self, container: HoilUtils.ExecVarContainer):
        """Native function. Rotate the robot right"""
        s: DType
        s = container.varTable.Get('%speed%').Get()
        container.robot.RotateRight(s)
    
    def GetSensorReading(self, container:HoilUtils.ExecVarContainer):
        """Native function. Get the sensor data"""
        s: DType
        s = container.varTable.Get('%angle%').Get()
        value = container.robot.GetSensorData(s)

        self.container.returnVal.append(value)

    def Stop(self, container: HoilUtils.ExecVarContainer):
        """Native function. Stop the robot's movement"""
        container.robot.StopAllAction()

    def SenseLeft(self, container: HoilUtils.ExecVarContainer):
        """Native function. Stop the robot's movement"""
        s: DType
        s = container.varTable.Get('%dist%').Get()
        self.container.returnVal.append(self.container.robot.SenseLeft(s))

    def SenseRight(self, container: HoilUtils.ExecVarContainer):
        """Native function. Stop the robot's movement"""
        s: DType
        s = container.varTable.Get('%dist%').Get()
        self.container.returnVal.append(self.container.robot.SenseRight(s))

    def SenseRight(self, container: HoilUtils.ExecVarContainer):
        """Native function. Stop the robot's movement"""
        s: DType
        s = container.varTable.Get('%dist%').Get()
        self.container.returnVal.append(self.container.robot.SenseForward(s))












if __name__ == '__main__':
    hoil_interp_server = HoilServer()





    


    
