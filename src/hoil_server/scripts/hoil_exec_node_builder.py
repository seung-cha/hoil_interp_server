from hoil_exec_nodes import *
from hoil_utils import VariableTable
from collections import deque
import typing

class ExecNodeBuilder:
    def __init__(self, varTable:VariableTable):
        self.table = varTable

    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        # Override this
        return None
    
    def GetLine(self, stack: deque) -> list:
        return stack[0].split()

class DeclNodeBuilder(ExecNodeBuilder):
    def __init__(self, varTable: VariableTable):
        super().__init__(varTable)

    def Run(self, stack:deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)
        if line[0] != '$decl':
            return None
        
        stack.popleft()
        if len(line) == 4:
            return DeclNode(self.table, line[1], line[2], line[3])
        else:
            return DeclNode(self.table, line[1], line[2], None)


class BranchNodeBuilder(ExecNodeBuilder):
    def __init__(self, varTable: VariableTable):
        super().__init__(varTable)

    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)

        if line[0] != '$branch_begin':
            return None
        
        branchNode = BranchNode()

        stack.popleft()
        line = self.GetLine(stack)
        
        while line[0] != '$branch_end':
            if line[0] == '$if' or line[0] == '$elif':
                condNode = ConditionalNode()

                cond = ExprNode(self.table, line[1])
                stack.popleft()

                # Will always terminate upon '$*_end'
                stmt = _BuildExecNode(stack, self.table)
                
                condNode.condNode = cond
                condNode.execNode = stmt

                line = self.GetLine(stack)
                if line[0] == '$if_end':
                    branchNode.ifNode = condNode
                else:
                    branchNode.elifNodes.append(condNode)
                stack.popleft()
            elif line[0] == '$else_begin':
                stack.popleft()
                node = _BuildExecNode(stack, self.table)

                branchNode.elseNode = node
                stack.popleft()
        
            line = self.GetLine(stack)

        stack.popleft()
        return branchNode

class ScopedNodeBuilder(ExecNodeBuilder):
    def __init__(self, varTable: VariableTable):
        super().__init__(varTable)
    
    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)

        if line[0] != '$open_scope':
            return None
        
        stack.popleft()
        scopedNode = ScopedNode(self.table)
        scopedNode.node = _BuildExecNode(stack, self.table)
        stack.popleft()

        return scopedNode



            
def _BuildExecNode(stack: deque, varTable: VariableTable) -> typing.Optional[ExecNode]:
    """Called recursively to create linked list of execnodes.
    Exit upon encountering end region (if_end, while_end etc)
    as well-formed program will always have a matching pair and therefore a matching func call to handle them"""
    
    builderList = list()
    builderList.append(DeclNodeBuilder(varTable))
    builderList.append(BranchNodeBuilder(varTable))
    builderList.append(ScopedNodeBuilder(varTable))


    head = EmptyNode()
    cur = None

    while len(stack) > 0:

        print(f'BuildExecNode():: Current stmt: {stack[0]}')

        if  stack[0] == '$if_end'        or\
            stack[0] == '$elif_end'      or\
            stack[0] == '$else_end'      or\
            stack[0] == '$close_scope'   or\
            stack[0] == '$branch_end':
            return head

        builder:ExecNodeBuilder
        for builder in builderList:

            # Prev builder may drain all lines
            if len(stack) <= 0:
                break

            node = builder.Run(stack)

            if node is not None:
                if isinstance(head, EmptyNode):
                    head = node
                    cur = node
                else:
                    cur.next = node
                    cur = node

    return head
    



# Node builder produces a complete list of ExecNodes
def BuildExecNode(source: str, varTable: VariableTable) -> typing.Optional[ExecNode]:
    stack = deque([x for x in source.splitlines() if x != ''])
    return _BuildExecNode(stack, varTable)
    
    

        



