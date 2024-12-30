from hoil_utils import VariableTable, EvaluateExpr
from hoil_dtypes import DType
from collections import deque
import typing


class ExecNode:
    def __init__(self):
        self.next = None

    
    def Run(self):
        """Runtime execution. Override this. 
        Return True or False depending on the success of execution"""
        return True


class EmptyNode(ExecNode):
    def __init__(self):
        super().__init__()


class DeclNode(ExecNode):
    def __init__(self, table: VariableTable, spelling: str, type:str, expr: typing.Optional[str]):
        super().__init__()
        self.table = table
        self.spelling = spelling
        self.type = type
        self.expr = expr

    def Run(self):
        # TODO: Create different var types based on the supplied type
        var: DType
        var = self.table.Get(self.spelling)

        if var is not None:
            var.Assign(self.expr)
        else:
            dtype = DType(self.table, self.expr)
            self.table.Insert(self.spelling, dtype)
        
        return True


class ExprNode(ExecNode):
    def __init__(self, table: VariableTable, expr: str):
        super().__init__()
        self.table = table
        self.expr = expr
        self.value = None

    def Run(self):
        self.value = EvaluateExpr(self.expr, self.table)
        return True

        
class BranchNode(ExecNode):
    def __init__(self):
        super().__init__()

        self.ifNode: ConditionalNode
        self.ifNode = EmptyNode()

        self.elifNodes = []

        self.elseNode: ExecNode
        self.elseNode = EmptyNode()

    def Run(self):
        if self.ifNode.Run():
            return self.ifNode.execOutcome
        
        for elifNode in self.elifNodes:
            if elifNode.Run():
                return elifNode.execOutcome
        
        return self.elseNode.Run()



class ConditionalNode(ExecNode):
    def __init__(self):
        super().__init__()

        self.condNode:ExprNode
        self.condNode = None

        self.execNode:ExecNode
        self.execNode = None

        self.execOutcome = False

    def Run(self):
        self.condNode.Run()

        if not self.condNode.value:
            return False
        
        self.execOutcome = self.execNode.Run()
        return True


class ScopedNode(ExecNode):
    def __init__(self, table:VariableTable):
        super().__init__()
        self.table = table

        self.node: ExecNode
        self.node = EmptyNode()
    
    def Run(self):
        self.table.Push()

        node = self.node

        while node is not None:
            if node.Run():
                node = node.next
            else:
                self.table.Pop()
                return False

        self.table.Pop()
        return True
    
class LoopNode(ExecNode):
    def __init__(self, table:VariableTable, loopStack: deque, condNode: ExprNode, bodyNode: ExecNode):
        super().__init__()
        self.table = table
        self.loopStack = loopStack

        self.condNode = condNode
        self.bodyNode = bodyNode

        self.shouldBreak = False

    def Run(self):
        self.loopStack.append(self)
        outcome = False
        while True:
            if self.shouldBreak:
                break

            self.condNode.Run()

            if self.condNode.value:
                outcome = self.bodyNode.Run()
            else:
                break
        
        self.loopStack.pop()
        return outcome

class BreakNode(ExecNode):
    def __init__(self, loopStack: deque):
        super().__init__()
        self.loopStack = loopStack

    def Run(self):
        self.loopStack[len(self.loopStack) - 1].shouldBreak = True
        return False
    
class ContinueNode(ExecNode):
    def __init__(self):
        super().__init__()

    def Run(self):
        return False
        
class InstructNode(ExecNode):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot

    def Run(self):
        pass


        
        


