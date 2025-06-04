from collections import deque
from robot import RobotArm 
import typing
from openai import OpenAI
import json
from gpt_prompt import prompt
from copy import deepcopy



def _AddOp(var1, var2):
    return var1 + var2

def _SubOp(var1, var2):
    return var1 - var2

def _UnarySub(var1, var2):
    # Conventional function params
    return -var2

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

def _LtenOp(var1, var2):
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
    '<': lambda v1, v2: _LtenOp(v1, v2),
    '<=': lambda v1, v2: _LeqOp(v1, v2),
    '[': lambda v1, v2: _UnarySub(v1, v2),
}


class HoilExprLexeme:
    def __init__(self, spelling:str, value= None, isVar= False, isLiteral= False, isOp= False, isUnary= False, isFunc= False, isArr= False):
        self.spelling = spelling
        self.value = value
        self.isVar = isVar
        self.isLiteral = isLiteral
        self.isOp = isOp
        self.isUnary = isUnary
        self.isFunc = isFunc
        self.isArr = isArr


class HoilExprLexer:
    def __init__(self, expr:str):
        self._queue = deque()
        strQueue = deque(expr)
        # Tokenise the bytecode
        # If function block is found, extract the whole content within it
        # and let the tokeniser split.
        while len(strQueue) > 0:
            spelling = ''
            if strQueue[0] == '$':
                level = 1
                spelling += '$'
                strQueue.popleft()

                while level > 0:
                    # Special handling for nested function call
                    if strQueue[0] == '$':
                        if len(strQueue) >= 2 and strQueue[1] == '^':
                            level -= 1
                            spelling += '$^'
                            strQueue.popleft()
                            strQueue.popleft()
                        else:
                            level += 1
                            spelling += '$'
                            strQueue.popleft()
                    else:
                        spelling += strQueue.popleft()
                
            else:
                while len(strQueue) > 0 and strQueue[0] != ';':
                    spelling += strQueue.popleft()
            
            if len(strQueue) > 0:   # Remove trailing ';'
                strQueue.popleft()

            self._queue.append(spelling)

    def _HandleFuncLexeme(self, spelling: str) -> typing.Optional[HoilExprLexeme]:
        # Assume the bytecode is a well-formed function representation.
        # Recursively call the function
        queue = deque(spelling)
        # HOIL IL function call expr structure:
        # $,ident,arg1,arg2...$^

        # Remove the preceeding $,
        queue.popleft()
        queue.popleft()

        ident = queue.popleft()
        while queue[0] != ',':
            ident += queue.popleft()

        queue.popleft()
        # Handle args (as string).
        # Manually extract the args due to nested function calls
        args = []
        arg = ''
        level = 0
        while len(queue) > 0:
            if queue[0] == ',' and level == 0:
                queue.popleft()
                args.append(arg)
                arg = ''
            else:
                if queue[0] == '$':
                    if len(queue) >= 2 and queue[1] == '^':
                        
                        if level > 0:
                            arg += '$^'
                        queue.popleft()
                        queue.popleft()
                        level -= 1
                    else:
                        level += 1
                        arg += queue.popleft()
                else:
                    arg += queue.popleft()
                


        
        args.append(arg)
        return HoilExprLexeme(ident, value= args, isFunc= True)

    def _HandleArrLexeme(self, spelling: str):
        # Arr structure:
        # $a,ident,index,expr$^
        queue = deque(spelling)

        # Remove the preceeding $a,
        queue.popleft()
        queue.popleft()
        queue.popleft()

        ident = ''
        while queue[0] != ',':
            ident += queue.popleft()
        queue.popleft()

        index = ''
        while queue[0] != '$':
            index += queue.popleft()

        # Pop $^
        queue.popleft()
        queue.popleft()

        return HoilExprLexeme(ident, value= index, isArr= True)

        




    def GetNextLexeme(self) -> typing.Optional[HoilExprLexeme]:
        if len(self._queue) == 0:
            return None
        spelling = self._queue.popleft()

        # Extract var
        if spelling[0] == '%':
            return HoilExprLexeme(spelling, isVar= True)
        
        if spelling[0] == '"':
            return HoilExprLexeme(spelling, value= spelling, isLiteral= True)
        
        # Extract func ($) or array ($,)

        if spelling[0] == '$' and spelling[1] == 'a':
            return self._HandleArrLexeme(spelling)
        elif spelling[0] == '$':
            return self._HandleFuncLexeme(spelling)
        
        # Extract number
        try:
            v = float(spelling)
            return HoilExprLexeme(spelling, value= v, isLiteral= True)
        except:
            pass
        
        # Extract literal (boolean)
        if spelling.isalpha():
            return HoilExprLexeme(spelling, value= True if spelling == 'true' else False, isLiteral= True)


        # [ is unary - in HOIL
        return HoilExprLexeme(spelling, isOp= True, isUnary= spelling == '[')
    

class VariableTable:

    def __init__(self):
        self._stack = deque()
        self.Push()

    def Push(self):
        self._stack.append(_VarScope())
    
    def Pop(self):
        self._stack.pop()
    
    def Isolate(self):
        """
        Create a new isolated scope containing all previous scopes.
        Use it to create a function
        """
        table = VariableTable()
        for item in self._stack:
            table._stack.append(item)
        
        return table

    def Insert(self, var:str, val):
        self._stack[len(self._stack) - 1].Insert(var, val)

    def Get(self, var:str, topLevelOnly= False):
        if topLevelOnly:
            return self._stack[len(self._stack) - 1].Get(var)
            
        for scope in reversed(self._stack):
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
    

class InstructTable:
    def __init__(self):
        self._func = []
        self._in_stmt = []
        self._out_stmt = []

    def InsertFunction(self, function):
        self._func.append(function)
    
    def Insert(self, bytecode: str) -> int:
        """Insert raw instruct stmt into the array for batch-evaluation.
        Return index id to retrieve execution code."""
        self._in_stmt.append(bytecode)
        return len(self._in_stmt) - 1
    
    def Get(self, index: int) -> str:
        """Get the execution code
        """
        return self._out_stmt[index]
    
    def Evaluate(self):
        """
        Run before execution to evaluate and store instruct stmt into python function
        """
        # Reserve space
        self._out_stmt = [None] * len(self._in_stmt)
        cache = dict()

        # Look at cache and find matching pair
        try:
            with open('cache.json', 'r') as f:
                cache: dict
                cache = json.load(f)
                
                removeList = []
                for i in range(len(self._in_stmt)):
                    if self._in_stmt[i] in cache.keys():
                        self._out_stmt[i] = cache[self._in_stmt[i]]
                        removeList.append(self._in_stmt[i])
                
                # Remove all matched in stmts
                for stmt in removeList:
                    print(f'InstructTable:: remove: {stmt}')
                    self._in_stmt.remove(stmt)
        except Exception as e:
            print('InstructTable:: Error occurred while reading in cache: ')
            print(e)


        if len(self._in_stmt) == 0:
            print('InstructTable:: all hit the cache!')
            return

        # Construct function description
        func_desc = [ {'name': str(function), 'params':  ', '.join(map(str, function.paramNodes)) } for function in self._func ]
        func_desc_json = json.dumps(func_desc)
        #print(prompt + func_desc_json)


        # Convert the remaining list into json and feed it to gpt
        dic =  [ {'id': i, 'stmt': self._in_stmt[i]} for i in range(len(self._in_stmt)) ]
        json_dic = json.dumps(dic)

        client = OpenAI()
        res = client.chat.completions.create(
            model= 'gpt-4',
            messages= [
                { 'role': 'system',
                'content': prompt + func_desc_json
                },
                {
                    'role': 'user',
                    'content': json_dic
                }
            ]
        )

        res_dic = json.loads(res.choices[0].message.content)
        
        # Append the chatgpt-generated responses to the cache
        for obj in res_dic:
            self._out_stmt[obj['id']] = obj['exec']
            cache[self._in_stmt[obj['id']]] = obj['exec']
        
        with open('cache.json', 'w') as f:
            json.dump(cache, f)


    def Warn(self):
        print('InstructTable:: Warn() is called. Check the instruct stmt to make sure it is logical.')


class ExecVarContainer:
    def __init__(self, robot: RobotArm = None, instructTable: InstructTable = None, functionMap: dict = None, noROS= False):
        self.varTable = VariableTable() 
        self.loopStack = deque()
        self.currentFunc = None
        self.noROS = noROS
        self.returnVal = []
        
        if functionMap is None:
            self.functionMap = dict()
        else:
            self.functionMap = functionMap
        if robot is None and not noROS:
            self.robot = RobotArm()
        else:
            self.robot = robot


        if instructTable is None:
            self.instructTable = InstructTable()
        else:
            self.instructTable = instructTable
    
    def NewScope(self):
        return ExecVarContainer(robot= self.robot, instructTable= self.instructTable, functionMap= self.functionMap, noROS= self.noROS)


def EvaluateExpr(expr, container: ExecVarContainer) -> object:
    stack = deque()
    lexer = HoilExprLexer(expr)
    while True:
        lex = lexer.GetNextLexeme()

        if lex is None:
            break

        if lex.isLiteral:
            stack.append(lex.value)
        elif lex.isVar:
            var = container.varTable.Get(lex.spelling)
            if var is None: 
                # TODO: handle use-of-variable before assignment
                raise Exception(f"Use of variable before assignment! ${lex.spelling}")
            
            stack.append(var.Get())
        elif lex.isOp:
            var2 = stack.pop()

            # Handle Unary op
            if lex.isUnary:
                var1 = None
            else:
                var1 = stack.pop()
            val = Ops[lex.spelling](var1, var2)
            
            stack.append(val)
        elif lex.isFunc:
            f = container.functionMap[lex.spelling]
            f.Call(lex.value)
            stack.append(container.returnVal.pop())
        elif lex.isArr:
            arr = container.varTable.Get(lex.spelling).Get()
            val = arr[EvaluateExpr(lex.value, container)]
            stack.append(val)
            
        
    
    val = stack.pop()

    if len(stack) != 0:
        # TODO: Raise error on stack not empty after expr
        raise Exception

    return val