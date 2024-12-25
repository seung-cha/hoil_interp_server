from hoil_utils import VariableTable, EvaluateExpr
from hoil_dtypes import DType
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

        self.ifNode: ExecNode
        self.ifNode = EmptyNode()

        self.elifNodes = []

        self.elseNode: ExecNode
        self.elseNode = EmptyNode()

    def Run(self):
        if self.ifNode.Run():
            return True
        
        for elifNode in self.elifNodes:
            if elifNode.Run():
                return True
        
        self.elseNode.Run()
        return True



class ConditionalNode(ExecNode):
    def __init__(self):
        super().__init__()

        self.condNode:ExprNode
        self.condNode = None

        self.execNode:ExecNode
        self.execNode = None

    def Run(self):
        self.condNode.Run()

        if not self.condNode.value:
            return False
        
        self.execNode.Run()
        return True


class ScopedNode(ExecNode):
    def __init__(self, table:VariableTable):
        super().__init__()
        self.table = table

        self.node: ExecNode
        self.node = EmptyNode()
    
    def Run(self):
        self.table.Push()
        self.node.Run()
        self.table.Pop()
        return True
    
    


        
        


