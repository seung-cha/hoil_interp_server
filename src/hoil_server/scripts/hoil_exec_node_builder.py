from hoil_exec_nodes import *
from hoil_utils import VariableTable
from collections import deque
import typing
import shlex

class ExecNodeBuilder:
    def __init__(self, varTable:VariableTable, loopStack, robot):
        self.table = varTable
        self.loopStack = loopStack
        self.robot = robot

    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        # Override this
        return None
    
    def GetLine(self, stack: deque) -> list:
        return shlex.split(stack[0], posix= False)

class DeclNodeBuilder(ExecNodeBuilder):
    def __init__(self, varTable: VariableTable, loopStack, robot):
        super().__init__(varTable, loopStack, robot)

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
    def __init__(self, varTable: VariableTable, loopStack, robot):
        super().__init__(varTable, loopStack, robot)

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
                stmt = _BuildExecNode(stack, self.table, self.loopStack, self.robot)
                
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
                node = _BuildExecNode(stack, self.table, self.loopStack, self.robot)

                branchNode.elseNode = node
                stack.popleft()
        
            line = self.GetLine(stack)

        stack.popleft()
        return branchNode

class ScopedNodeBuilder(ExecNodeBuilder):
    def __init__(self, varTable: VariableTable, loopStack, robot):
        super().__init__(varTable, loopStack, robot)
    
    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)

        if line[0] != '$open_scope':
            return None
        
        stack.popleft()
        scopedNode = ScopedNode(self.table)
        scopedNode.node = _BuildExecNode(stack, self.table, self.loopStack, self.robot)
        stack.popleft()

        return scopedNode

class LoopNodeBuilder(ExecNodeBuilder):
    def __init__(self, varTable: VariableTable, loopStack, robot):
        super().__init__(varTable, loopStack, robot)

    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)

        if line[0] != '$while':
            return None
    
        cond = ExprNode(self.table, 'true')

        if len(line) == 2:
            cond = ExprNode(self.table, line[1])
    
        stack.popleft()

        body = _BuildExecNode(stack, self.table, self.loopStack, self.robot)

        stack.popleft()

        return LoopNode(self.table, self.loopStack, cond, body)

class JumpNodeBuilder(ExecNodeBuilder):
    def __init__(self, varTable: VariableTable, loopStack, robot):
        super().__init__(varTable, loopStack, robot)
    
    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)

        
        if line[0] == '$break':
            stack.popleft()
            return BreakNode(self.loopStack)
        elif line[0] == '$continue':
            stack.popleft()
            return ContinueNode()

        return None



            
def _BuildExecNode(stack: deque, varTable: VariableTable, loopStack, robot) -> typing.Optional[ExecNode]:
    """Called recursively to create linked list of execnodes.
    Exit upon encountering end region (if_end, while_end etc)
    as well-formed program will always have a matching pair and therefore a matching func call to handle them"""
    
    builderList = list()
    builderList.append(DeclNodeBuilder(varTable, loopStack, robot))
    builderList.append(BranchNodeBuilder(varTable, loopStack, robot))
    builderList.append(ScopedNodeBuilder(varTable, loopStack, robot))
    builderList.append(LoopNodeBuilder(varTable, loopStack, robot))
    builderList.append(JumpNodeBuilder(varTable, loopStack, robot))


    head = EmptyNode()
    cur = None

    while len(stack) > 0:

        print(f'BuildExecNode():: Current stmt: {stack[0]}')

        if  stack[0] == '$if_end'        or\
            stack[0] == '$elif_end'      or\
            stack[0] == '$else_end'      or\
            stack[0] == '$close_scope'   or\
            stack[0] == '$branch_end'    or\
            stack[0] == '$while_end':
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
def BuildExecNode(source: str, varTable: VariableTable, loopStack, robot) -> typing.Optional[ExecNode]:
    stack = deque([x for x in source.splitlines() if x != ''])
    return _BuildExecNode(stack, varTable, loopStack, robot)
    
    

        



