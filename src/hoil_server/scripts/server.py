#!/usr/bin/env python

import hoil_utils as HoilUtils
from hoil_exec_node_builder import BuildExecNode
import sys
from hoil_exec_nodes import FunctionNode, NativeNode
from hoil_dtypes import DType


class HoilServer:

    def __init__(self):
        # TODO: Create a ROSNode that feeds HOIL bytecode
        # TODO: Create a HOIL Function generation code
        file = sys.argv[1]
        with open(file, 'r') as f:
            data = f.read()


        self.container = HoilUtils.ExecVarContainer(noROS= True)
        self.node = BuildExecNode(data, self.container)

        # Insert functions
        FunctionNode.MakeFunction(self.container, 'Print', ['text'],\
                                  NativeNode(self.container, self.Print))
        
        FunctionNode.MakeFunction(self.container, 'MoveTo', ['x', 'y', 'z'],\
                                  NativeNode(self.container, self.MoveTo))
        
        FunctionNode.MakeFunction(self.container, 'MoveBy', ['x', 'y', 'z'],\
                                  NativeNode(self.container, self.MoveTo))
        
        
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

        container.robot.MoveTo(x.Get(), y.Get(), z.Get())

    def MoveTo(self, container: HoilUtils.ExecVarContainer):
        """Native function. Move arm to %x%, %y%, %z%"""
        x: DType
        y: DType
        z: DType
        x = container.varTable.Get("%x%")
        y = container.varTable.Get("%y%")
        z = container.varTable.Get("%z%")

        container.robot.MoveBy(x.Get(), y.Get(), z.Get())





if __name__ == '__main__':
    hoil_interp_server = HoilServer()





    


    
