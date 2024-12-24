from hoil_utils import VariableTable
from hoil_dtypes import DType
import typing

class ExecNode:
    
    def __init__(self):
        self.next = None

    
    def Run(self):
        """Runtime execution. Override this"""
        pass


class DeclNode(ExecNode):
    def __init__(self, table: VariableTable, spelling: str, type:str, expr: typing.Optional[str]):
        super().__init__()
        self.table = table
        self.spelling = spelling
        self.type = type
        self.expr = expr

    def Run(self):
        # TODO: Create different var types based on the supplied type
        dtype = DType(self.table, self.expr)
        self.table.Insert(self.spelling, dtype)


        
        


