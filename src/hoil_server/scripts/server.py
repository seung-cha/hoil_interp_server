#!/usr/bin/env python3
import rospy
import hoil_utils as HoilUtils
from hoil_exec_node_builder import BuildExecNode
import sys


if __name__ == '__main__':

    file = sys.argv[1]

    with open(file, 'r') as f:
        data = f.read()

    #print(data)

    varTable = HoilUtils.VariableTable()
    node = BuildExecNode(data, varTable)

    while node is not None:
        node.Run()
        node = node.next

    print(varTable.Get('%grade%').Get())
    print(varTable.Get('%result%').Get())


    


    
