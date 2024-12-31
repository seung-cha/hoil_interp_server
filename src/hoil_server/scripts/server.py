#!/usr/bin/env python

import hoil_utils as HoilUtils
from hoil_exec_node_builder import BuildExecNode
import sys


class HoilServer:

    def __init__(self):
        # TODO: Create a ROSNode that feeds HOIL bytecode
        file = sys.argv[1]
        with open(file, 'r') as f:
            data = f.read()

        self.container = HoilUtils.ExecVarContainer()
        self.node = BuildExecNode(data, self.container)

        self.container.robot.InitialiseDemo()
        self.container.instructTable.Evaluate()

        node = self.node
        while node is not None:
            node.Run()
            node = node.next


if __name__ == '__main__':
    hoil_interp_server = HoilServer()





    


    
