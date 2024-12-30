#!/usr/bin/env python3

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







        




if __name__ == '__main__':
    hoil_interp_server = HoilServer()





    


    
