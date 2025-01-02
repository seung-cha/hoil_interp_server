from hoil_exec_nodes import *
from hoil_utils import ExecVarContainer
from collections import deque
import typing
import shlex

class ExecNodeBuilder:
    def __init__(self, container:ExecVarContainer):
        self.container = container

    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        # Override this
        return None
    
    def GetLine(self, stack: deque) -> list:
        return shlex.split(stack[0], posix= False)

class DeclNodeBuilder(ExecNodeBuilder):
    def __init__(self, container:ExecVarContainer):
        super().__init__(container)

    def Run(self, stack:deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)
        if line[0] != '$decl':
            return None
        
        stack.popleft()
        if len(line) == 4:
            return DeclNode(self.container, line[1], line[2], line[3])
        else:
            return DeclNode(self.container, line[1], line[2], None)


class BranchNodeBuilder(ExecNodeBuilder):
    def __init__(self, container:ExecVarContainer):
        super().__init__(container)

    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)

        if line[0] != '$branch_begin':
            return None
        
        branchNode = BranchNode(self.container)

        stack.popleft()
        line = self.GetLine(stack)
        
        while line[0] != '$branch_end':
            if line[0] == '$if' or line[0] == '$elif':
                condNode = ConditionalNode(self.container)

                cond = ExprNode(self.container, line[1])
                stack.popleft()

                # Will always terminate upon '$*_end'
                stmt = _BuildExecNode(stack, self.container)
                
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
                node = _BuildExecNode(stack, self.container)

                branchNode.elseNode = node
                stack.popleft()
        
            line = self.GetLine(stack)

        stack.popleft()
        return branchNode

class ScopedNodeBuilder(ExecNodeBuilder):
    def __init__(self, container:ExecVarContainer):
        super().__init__(container)
    
    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)

        if line[0] != '$open_scope':
            return None
        
        stack.popleft()
        scopedNode = ScopedNode(self.container)
        scopedNode.node = _BuildExecNode(stack, self.container)
        stack.popleft()

        return scopedNode

class LoopNodeBuilder(ExecNodeBuilder):
    def __init__(self, container:ExecVarContainer):
        super().__init__(container)

    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)

        if line[0] != '$while':
            return None
    
        cond = ExprNode(self.container, 'true')

        if len(line) == 2:
            cond = ExprNode(self.container, line[1])
    
        stack.popleft()

        body = _BuildExecNode(stack, self.container)

        stack.popleft()

        return LoopNode(self.container, cond, body)

class JumpNodeBuilder(ExecNodeBuilder):
    def __init__(self, container:ExecVarContainer):
        super().__init__(container)
    
    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)

        
        if line[0] == '$break':
            stack.popleft()
            return BreakNode(self.container)
        elif line[0] == '$continue':
            stack.popleft()
            return ContinueNode(self.container)

        return None
    
class InstructNodeBuilder(ExecNodeBuilder):
    def __init__(self, container:ExecVarContainer):
        super().__init__(container)

    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)

        if line[0] != '$instruct':
            return None

        node = InstructNode(self.container, line[1])
        stack.popleft()

        return node
    
class FunctionNodeBuilder(ExecNodeBuilder):
    def __init__(self, container: ExecVarContainer):
        super().__init__(container)
    
    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)

        if line[0] != '$func_decl':
            return None
        
        funcContainer = ExecVarContainer(
            self.container.robot, 
            self.container.instructTable, 
            self.container.functionMap)
        
        # TODO: Parse param
        ident = line[1]
        param = []
        
        if line[2] == '$param':
            # No return value, only params
            param_index = 3
        else:
            ret = line[2]
            param_index = 4

        # add params
        while param_index < len(line):
            param_ident = line[param_index]

            if param_index + 1 < len(line) and line[param_index + 1][0] == '$':
                param_type = line[param_index + 1]
                param_index += 1
            else:
                param_type = None
            
            param.append(DeclNode(funcContainer, param_ident, param_type, None))
            param_index += 1

        stack.popleft()

        node = _BuildExecNode(stack, funcContainer)

        stack.popleft()

        funcNode = FunctionNode(funcContainer, ident, param, node)
        return funcNode


class ReturnNodeBuilder(ExecNodeBuilder):
    def __init__(self, container: ExecVarContainer):
        super().__init__(container)

    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)

        if line[0] != '$return':
            return None
        
        if len(line) == 1:
            expr = ''
        else:
            expr = line[1]

        node = ReturnNode(self.container, expr)
        stack.popleft()
        return node

class CallNodeBuilder(ExecNodeBuilder):
    def __init__(self, container: ExecVarContainer):
        super().__init__(container)

    def Run(self, stack: deque) -> typing.Optional[ExecNode]:
        line = self.GetLine(stack)

        if line[0] != '$call':
            return None
        
        args = []

        if len(line) == 3:
            args = line[2].split(',')


        node = CallNode(self.container, line[1], args)
        stack.popleft()

        return node


            
def _BuildExecNode(stack: deque, container:ExecVarContainer) -> typing.Optional[ExecNode]:
    """Called recursively to create linked list of execnodes.
    Exit upon encountering end region (if_end, while_end etc)
    as well-formed program will always have a matching pair and therefore a matching func call to handle them"""
    
    builderList = list()
    builderList.append(DeclNodeBuilder(container))
    builderList.append(BranchNodeBuilder(container))
    builderList.append(ScopedNodeBuilder(container))
    builderList.append(LoopNodeBuilder(container))
    builderList.append(JumpNodeBuilder(container))
    builderList.append(InstructNodeBuilder(container))
    builderList.append(FunctionNodeBuilder(container))
    builderList.append(ReturnNodeBuilder(container))
    builderList.append(CallNodeBuilder(container))




    head = EmptyNode(container)
    cur = None

    while len(stack) > 0:
        print(f'BuildExecNode():: Current stmt: {stack[0]}')

        if  stack[0] == '$if_end'        or\
            stack[0] == '$elif_end'      or\
            stack[0] == '$else_end'      or\
            stack[0] == '$close_scope'   or\
            stack[0] == '$branch_end'    or\
            stack[0] == '$while_end'     or\
            stack[0] == '$func_decl_end':
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
def BuildExecNode(source: str, container:ExecVarContainer) -> typing.Optional[ExecNode]:
    stack = deque([x for x in source.splitlines() if x != ''])
    return _BuildExecNode(stack, container)
    
    

        



