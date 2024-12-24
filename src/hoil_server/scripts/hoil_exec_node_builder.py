from hoil_exec_nodes import *
from hoil_utils import VariableTable
from collections import deque
import typing

class ExecNodeBuilder:
    
    def Run(self, stack:deque) -> typing.Optional[ExecNode]:
        # Override this
        return None
    
    def GetLine(self, stack:deque) -> list:
        return stack[0].split()

class DeclNodeBuilder(ExecNodeBuilder):
    def __init__(self, varTable: VariableTable):
        self.table = varTable

    def Run(self, stack:deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)
        if line[0] != '$decl':
            return None
        
        stack.popleft()
        if len(line) == 4:
            return DeclNode(self.table, line[1], line[2], line[3])
        else:
            return DeclNode(self.table, line[1], line[2], None)

        



# Node builder produces a complete list of ExecNodes
def BuildExecNode(source: str, varTable: VariableTable) -> typing.Optional[ExecNode]:
    stack = deque(source.splitlines())
    builderList = list()
    builderList.append(DeclNodeBuilder(varTable))

    head = None
    cur = None


    while len(stack) > 0:

        print(f'BuildExecNode():: Current stmt: {stack[0]}')
        
        while len(stack) > 0 and stack[0] == '':
            stack.popleft()

        builder:ExecNodeBuilder
        for builder in builderList:

            if len(stack) <= 0:
                break

            # TODO: Trim blank spaces
            node = builder.Run(stack)

            if node is not None:
                if head is None:
                    head = node
                    cur = node
                else:
                    cur.next = node
                    cur = node

    return head
    

        



