from hoil_utils import VariableTable, EvaluateExpr
from collections import deque
import typing   

class DType:
    
    def __init__(self, varTable:VariableTable, expr:typing.Optional[str]):
        self._assigned = False
        self._table = varTable
        self._expr = expr
        self._val = None

        if self._expr is not None:
            self.Assign(self._expr)


    def Assign(self, expr:str):
        self._expr = expr
        self._assigned = True
        self._val = self._Eval()

    def _Eval(self) -> object:
        return EvaluateExpr(self._expr, self._table)
    
    def Get(self):
        # TODO: Raise error on use-before-assignment
        if self._val is None:
            raise Exception
        else:
            return self._val
        
