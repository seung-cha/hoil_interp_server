from hoil_utils import ExecVarContainer, EvaluateExpr
from collections import deque
import typing
import re

class DType:
    
    def __init__(self, container:ExecVarContainer, expr:typing.Optional[str], paramDecl= False):
        self._assigned = False
        self._container = container
        self._expr = expr
        self._val = None

        if self._expr is not None and not paramDecl:
            self.Assign(self._expr)


    def Assign(self, expr:str):
        """
        Assign value by evaluating HOIL bytecode
        """
        self._expr = expr
        self._assigned = True
        self._val = self._Eval()

    def AssignValue(self, val):
        """
        Directly set the value. Useful for LLM-based writing
        """
        if val is not None:
            self._assigned = True
        self._val = val

    def _Eval(self) -> object:
        return EvaluateExpr(self._expr, self._container)
    
    def Get(self):
        # TODO: Raise error on use-before-assignment
        if self._val is None:
            raise Exception
        else:
            # if it's string, interpolate.
            if isinstance(self._val, str):
                string: str
                string = self._val
                regex = '\{[^}]*\}'
                res = set(re.findall(regex, string))

                if res:
                    for match in res:
                        val: DType
                        val = self._container.varTable.Get(f'%{match[1 : -1]}%')
                        string = string.replace(match, str(val.Get()))

                return string
    
            return self._val
        
