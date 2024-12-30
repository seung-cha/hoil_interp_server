from collections import deque
from robot import RobotArm 
import typing


def _AddOp(var1, var2):
    return var1 + var2

def _SubOp(var1, var2):
    return var1 - var2

def _MulOp(var1, var2):
    return var1 * var2

def _DivOp(var1, var2):
    return var1 / var2

def _ModOp(var1, var2):
    return var1 % var2

def _AndOp(var1, var2):
    # TODO: Attrib handling
    return var1 and var2

def _OrOp(var1, var2):
    return var1 or var2

def _EqOp(var1, var2):
    return var1 == var2

def _NeqOp(var1, var2):
    return var1 != var2

def _NotOp(var):
    return not var

def _GterOp(var1, var2):
    return var1 > var2

def _GeqOp(var1, var2):
    return var1 >= var2

def LtenOp(var1, var2):
    return var1 < var2

def _LeqOp(var1, var2):
    return var1 <= var2

Ops = {
    '+': lambda v1, v2: _AddOp(v1, v2),
    '-': lambda v1, v2: _SubOp(v1, v2),
    '*': lambda v1, v2: _MulOp(v1, v2),
    '/': lambda v1, v2: _DivOp(v1, v2),
    '%': lambda v1, v2: _ModOp(v1, v2),
    '&&': lambda v1, v2: _AndOp(v1, v2),
    '||': lambda v1, v2: _OrOp(v1, v2),
    '==': lambda v1, v2: _EqOp(v1, v2),
    '!=': lambda v1, v2: _NeqOp(v1, v2),
    '!': lambda v1: _NotOp(v1),
    '>': lambda v1, v2: _GterOp(v1, v2),
    '>=': lambda v1, v2: _GeqOp(v1, v2),
    '<': lambda v1, v2: LtenOp(v1, v2),
    '<=': lambda v1, v2: _LeqOp(v1, v2),
}


class HoilExprLexeme:
    def __init__(self, spelling:str, value= None, isVar= False, isLiteral= False, isOp= False):
        self.spelling = spelling
        self.value = value
        self.isVar = isVar
        self.isLiteral = isLiteral
        self.isOp = isOp


class HoilExprLexer:
    def __init__(self, expr:str):
        self._queue = deque(expr.split(';'))

    def GetNextLexeme(self) -> typing.Optional[HoilExprLexeme]:
        if len(self._queue) == 0:
            return None
        spelling = self._queue.popleft()

        # Extract var
        if spelling[0] == '%':
            return HoilExprLexeme(spelling, isVar= True)
        
        if spelling[0] == '"':
            return HoilExprLexeme(spelling, value= spelling, isLiteral= True)
        
        # Extract number
        if spelling.isnumeric():
            return HoilExprLexeme(spelling, value= float(spelling), isLiteral= True)
        
        # Extract literal (boolean)
        if spelling.isalpha():
            
            return HoilExprLexeme(spelling, value= True if spelling == 'true' else False, isLiteral= True)


        return HoilExprLexeme(spelling, isOp= True)
    


class VariableTable:

    def __init__(self):
        self._stack = deque()
        self.Push()

    def Push(self):
        self._stack.append(_VarScope())
    
    def Pop(self):
        self._stack.pop()

    def Insert(self, var:str, val):
        self._stack[len(self._stack) - 1].Insert(var, val)

    def Get(self, var:str):
        for scope in self._stack:
            v = scope.Get(var)
            if v is None:
                continue
            return v
        
        return None
    
    def GetTempName(self) -> str:
        return self._stack[len(self.stack) - 1].GetTempName()



class _VarScope:
    
    def __init__(self):
        self._table = {}
        self._tempCtr = 0

    def Insert(self, var:str, val):
        self._table[var] = val

    def Get(self, var:str):
        if var not in self._table.keys():
            return None
        
        return self._table[var]
    
    def GetTempName(self) -> str:
        s = f'%_temp{self._tempCtr}_%'
        self._tempCtr = self._tempCtr + 1
        return s
    

def EvaluateExpr(expr, table:VariableTable) -> object:
    stack = deque()
    lexer = HoilExprLexer(expr)

    while True:
        lex = lexer.GetNextLexeme()

        if lex is None:
            break

        if lex.isLiteral:
            stack.append(lex.value)
        elif lex.isVar:
            var = table.Get(lex.spelling)
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

class ExecVarContainer:
    def __init__(self):
        self.varTable = VariableTable() 
        self.loopStack = deque()
        self.robot = RobotArm()
    