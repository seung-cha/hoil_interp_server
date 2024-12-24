from hoil_utils import HoilExprLexer, VariableTable, Ops
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
        stack = deque()
        lexer = HoilExprLexer(self._expr)

        while True:
            lex = lexer.GetNextLexeme()

            if lex is None:
                break

            if lex.isLiteral:
                stack.append(lex.value)
            elif lex.isVar:
                var = self._table.Get(lex.spelling)
                if var is None: 
                    # TODO: handle use-of-variable before assignment
                    raise Exception
                
                stack.append(var.Get())
            elif lex.isOp:
                var2 = stack.pop()
                var1 = stack.pop()
                val = Ops[lex.spelling](var1, var2)
                
                stack.append(val)
        
        val = stack.pop()

        if len(stack) != 0:
            # TODO: Raise error on stack not empty after expr
            raise Exception
    
        return val
    
    def Get(self):
        # TODO: Raise error on use-before-assignment
        if self._val is None:
            raise Exception
        else:
            return self._val
        
