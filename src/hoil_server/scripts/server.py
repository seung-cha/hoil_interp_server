#!/usr/bin/env python

import hoil_utils as HoilUtils
from hoil_exec_node_builder import BuildExecNode
import sys
from hoil_exec_nodes import FunctionNode, NativeNode
from hoil_dtypes import DType

from robot import SceneObject

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
        self.node = BuildExecNode(data, self.container)

        # Insert functions
        FunctionNode.MakeFunction(self.container, 'Print', ['text'],\
                                  NativeNode(self.container, self.Print))
        
        FunctionNode.MakeFunction(self.container, 'MoveTo', ['x', 'y', 'z'],\
                                  NativeNode(self.container, self.MoveTo))
        
        FunctionNode.MakeFunction(self.container, 'MoveBy', ['x', 'y', 'z'],\
                                  NativeNode(self.container, self.MoveBy))
        
        FunctionNode.MakeFunction(self.container, 'Grab', ['obj'],\
                                  NativeNode(self.container, self.Grab))
        
        FunctionNode.MakeFunction(self.container, 'Release', [],\
                                  NativeNode(self.container, self.Release))
        
        FunctionNode.MakeFunction(self.container, 'PositionOf', ['obj'],\
                                  NativeNode(self.container, self.PositionOf))
        
        FunctionNode.MakeFunction(self.container, 'HeightOf', ['obj'],\
                                  NativeNode(self.container, self.HeightOf))
        

        # Add an array that contains 5 unordered sticks
        boxObjs = {}
        for i in range(len(self.container.robot.scene_objects)):
            # dtype = DType(self.container, fixed= True)
            # dtype.AssignValue(self.container.robot.scene_objects[i])
            boxObjs[i] = self.container.robot.scene_objects[i]
        
        box_arr = DType(self.container, fixed= True, directAssignment= True, expr= boxObjs)
        self.container.varTable.Insert("%boxes%", box_arr)
                    
        #self.container.robot.InitialiseDemo()
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

    def MoveTo(self, container: HoilUtils.ExecVarContainer):
        """Native function. Move arm to %x%, %y%, %z%"""
        x: DType
        y: DType
        z: DType
        x = container.varTable.Get("%x%")
        y = container.varTable.Get("%y%")
        z = container.varTable.Get("%z%")

        print(f'Move to {x.Get()}, {y.Get()}, {z.Get()}')
        container.robot.MoveTo(x.Get(), y.Get(), z.Get())

    def MoveBy(self, container: HoilUtils.ExecVarContainer):
        """Native function. Move arm to %x%, %y%, %z%"""
        x: DType
        y: DType
        z: DType
        x = container.varTable.Get("%x%")
        y = container.varTable.Get("%y%")
        z = container.varTable.Get("%z%")

        print(f'Move by {x.Get()}, {y.Get()}, {z.Get()}')
        container.robot.MoveBy(x.Get(), y.Get(), z.Get())

    def Grab(self, container: HoilUtils.ExecVarContainer):
        """Native function. Close the gripper and call attach_object internally"""
        obj: DType
        obj = container.varTable.Get('%obj%')

        # TODO: Specify type in llm-based function calling so it doesnt confuse obj with str
        if isinstance(obj.Get(), str):
            obj = container.varTable.Get(f'%{obj.Get()}%')

        container.robot.CloseGripper()
        container.robot.arm_group.attach_object(obj.Get().id)

    def Release(self, container: HoilUtils.ExecVarContainer):
        """Native function. Release the gripper and detach_object"""
        container.robot.OpenGripper()
        container.robot.arm_group.detach_object()

    def PositionOf(self, container: HoilUtils.ExecVarContainer):
        """Native function. Get the position of object"""
        obj: DType
        obj = container.varTable.Get('%obj%')

        # TODO: Specify type in llm-based function calling so it doesnt confuse obj with str
        if isinstance(obj.Get(), str):
            obj = container.varTable.Get(f'%{obj.Get()}%')
        
        # HOIL array is internally a dict() for now.
        # TODO: Refactor returnVal
        self.container.returnVal.append(
            {0: obj.Get().x, 1: obj.Get().y, 2: obj.Get().z})
        
    def HeightOf(self, container: HoilUtils.ExecVarContainer):
        """Native function. Get the height of object"""
        obj: DType
        obj = container.varTable.Get('%obj%')

        # TODO: Specify type in llm-based function calling so it doesnt confuse obj with str
        if isinstance(obj.Get(), str):
            obj = container.varTable.Get(f'%{obj.Get()}%')
        
        # HOIL array is internally a dict() for now.
        # TODO: Refactor returnVal
        self.container.returnVal.append(obj.Get().height)









if __name__ == '__main__':
    hoil_interp_server = HoilServer()





    


    
