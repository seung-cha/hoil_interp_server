from hoil_utils import EvaluateExpr, ExecVarContainer
from hoil_dtypes import DType
import typing


class ExecNode:
    def __init__(self, container: ExecVarContainer):
        self.next = None
        self.container = container

    
    def Run(self):
        """Runtime execution. Override this. 
        Return True or False depending on the success of execution"""
        return True


class EmptyNode(ExecNode):
    def __init__(self, container: ExecVarContainer):
        super().__init__(container)


class DeclNode(ExecNode):
    def __init__(self, container: ExecVarContainer, spelling: str, type:str, expr: typing.Optional[str]):
        super().__init__(container)
        self.spelling = spelling
        self.type = type
        self.expr = expr

    def Run(self):
        # TODO: Create different var types based on the supplied type
        var: DType
        var = self.container.varTable.Get(self.spelling)

        if var is not None:
            var.Assign(self.expr)
        else:
            dtype = DType(self.table, self.expr)
            self.container.varTable.Insert(self.spelling, dtype)
        
        return True


class ExprNode(ExecNode):
    def __init__(self, container: ExecVarContainer, expr: str):
        super().__init__(container)
        self.expr = expr
        self.value = None

    def Run(self):
        self.value = EvaluateExpr(self.expr, self.table)
        return True

        
class BranchNode(ExecNode):
    def __init__(self, container: ExecVarContainer):
        super().__init__(container)

        self.ifNode: ConditionalNode
        self.ifNode = EmptyNode(container)

        self.elifNodes = []

        self.elseNode: ExecNode
        self.elseNode = EmptyNode(container)

    def Run(self):
        if self.ifNode.Run():
            return self.ifNode.execOutcome
        
        for elifNode in self.elifNodes:
            if elifNode.Run():
                return elifNode.execOutcome
        
        return self.elseNode.Run()



class ConditionalNode(ExecNode):
    def __init__(self, container: ExecVarContainer):
        super().__init__(container)

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
    def __init__(self, container: ExecVarContainer):
        super().__init__(container)

        self.node: ExecNode
        self.node = EmptyNode(container)
    
    def Run(self):
        self.table.Push()

        node = self.node

        while node is not None:
            if node.Run():
                node = node.next
            else:
                self.container.varTable.Pop()
                return False

        self.container.varTable.Pop()
        return True
    
class LoopNode(ExecNode):
    def __init__(self, container: ExecVarContainer, condNode: ExprNode, bodyNode: ExecNode):
        super().__init__(container)
        self.condNode = condNode
        self.bodyNode = bodyNode

        self.shouldBreak = False

    def Run(self):
        self.container.loopStack.append(self)
        outcome = False
        while True:
            if self.shouldBreak:
                break

            self.condNode.Run()

            if self.condNode.value:
                outcome = self.bodyNode.Run()
            else:
                break
        
        self.container.loopStack.pop()
        return outcome

class BreakNode(ExecNode):
    def __init__(self, container: ExecVarContainer):
        super().__init__(container)

    def Run(self):
        self.container.loopStack[len(self.loopStack) - 1].shouldBreak = True
        return False
    
class ContinueNode(ExecNode):
    def __init__(self, container: ExecVarContainer):
        super().__init__(container)

    def Run(self):
        return False
        
class InstructNode(ExecNode):
    def __init__(self, container: ExecVarContainer, stmt: str):
        super().__init__(container)
        self.id = self.container.instructTable.Insert(stmt)

    def Run(self):
        stmt = self.container.instructTable.Get(self.id)

        print(f'Executing stmt: {stmt}')
        exec(stmt)
        return True


        
        


