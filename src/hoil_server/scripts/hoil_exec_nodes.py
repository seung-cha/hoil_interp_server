from hoil_utils import EvaluateExpr, ExecVarContainer
from hoil_dtypes import DType
import typing
from copy import deepcopy


class ExecNode:
    def __init__(self, container: ExecVarContainer):
        self.next = None
        self.container = container

    
    def Run(self):
        """Runtime execution. Override this. 
        Return True or False depending on the success of execution"""
        return True

class NativeNode(ExecNode):
    """ 
    Special node for executing Python functions.
    Receives function that accepts ExecVarContainer
    """
    def __init__(self, container: ExecVarContainer, Func):
        super().__init__(container)
        self.func = Func

    def Run(self):
        self.func(self.container)

class EmptyNode(ExecNode):
    def __init__(self, container: ExecVarContainer):
        super().__init__(container)


class DeclNode(ExecNode):
    def __init__(self, container: ExecVarContainer, spelling: str, type:str, expr: typing.Optional[str], paramDecl= False, directAssignment= False):
        super().__init__(container)
        self.spelling = spelling
        self.type = type
        self.expr = expr
        self.paramDecl = paramDecl

        # If true, assign value with AssignValue() instead of Assign(). Used for param decl in llm-based function calling
        self.directAssignment = directAssignment

    def Run(self):
        # TODO: Create different var types based on the supplied type
        var: DType
        # If paramdecl, it needs to be declared regardless (on the top stack)
        var = self.container.varTable.Get(self.spelling, topLevelOnly= self.paramDecl)
        if var is not None:
            if self.directAssignment:
                var.AssignValue(self.expr)
            else:
                var.Assign(self.expr)
        else:
            dtype = DType(self.container, self.expr, directAssignment= self.directAssignment)

            # If array, initialise dict
            if self.type == '$array' and self.expr is None:
                dtype.AssignValue(dict())

            self.container.varTable.Insert(self.spelling, dtype)
        
        return True
    

class InsertNode(ExecNode):
    """Variant of DeclNode, for inserting values in array."""
    def __init__(self, container: ExecVarContainer, ident: str, index:str, expr:str):
        self.container = container
        self.ident = ident
        self.index = index
        self.expr = expr

    def Run(self):
        index = EvaluateExpr(self.index, self.container)
        expr = EvaluateExpr(self.expr, self.container)

        self.container.varTable.Get(self.ident).Get()[index] = expr


class ExprNode(ExecNode):
    def __init__(self, container: ExecVarContainer, expr: str):
        super().__init__(container)
        self.expr = expr
        self.value = None

    def Run(self):
        self.value = EvaluateExpr(self.expr, self.container)
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
        self.container.varTable.Push()

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
        self.stmt = stmt
        self.id = self.container.instructTable.Insert(stmt)
        self.value = None

    def Run(self):
        python_code = self.container.instructTable.Get(self.id)

        print(f'Executing stmt: {python_code} ({self.stmt})')
        exec(python_code)
        return True
    
    # Used to declare variable
    # TODO: Modulate. current code copied from DeclNode.Run()
    def Decl(self, spelling: str, val= None):
        var: DType
        var = self.container.varTable.Get(f'%{spelling}%', topLevelOnly= False)

        if var is not None:
            var.AssignValue(val)
        else:
            dtype = DType(self.container, expr= None)
            self.container.varTable.Insert(spelling, dtype)

    # Used to set variable
    # Identical to Decl(). Exists for LLM
    def Assign(self, spelling: str, val):
        self.Decl(spelling, val)

    # Used to get value.
    # Assumes variable is declared and is not mangled
    def ValueOf(self, spelling: str):
        return self.container.varTable.Get(f'%{spelling}%').Get()
    
    # Call function (non-mangled spelling) with params
    def Call(self, spelling: str, args):
        self.container.functionMap[f'%spelling%'].Call(args, directAssignment= True)
        ret = None

        # If the function returns something, get the value
        if len(self.container.returnVal) > 0:
            ret = self.container.returnVal.pop()

        return ret


    

    
class FunctionNode(ExecNode):
    def __init__(self, container: ExecVarContainer, ident: str, param: list, body: ExecNode):
        super().__init__(container)
        self.ident = ident
        self.body = body
        self.paramNodes = param

        # Register function
    def Run(self):
        self.container.functionMap[self.ident] = self
        return True
    
    def Call(self, args, directAssignment= False):
        prevFunc = self.container.currentFunc
        self.container.currentFunc = self


        # Push a layer into the table 
        # To make params temporary decls
        self.container.varTable.Push()
        # Set args and run
        for i in range(len(self.paramNodes)):
                self.paramNodes[i].directAssignment = directAssignment
                self.paramNodes[i].expr = args[i]
                self.paramNodes[i].Run()

        self.body.Run()

        self.container.currentFunc = prevFunc
        self.container.varTable.Pop()

    def MakeFunction(container: ExecVarContainer, ident: str, param: list, body: ExecNode):
        """Make function and return pointer, after inserting it to the table. feed list of non-mangled names in param"""
        p = []
        for id in param:
            p.append(DeclNode(container= container, spelling= f'%{id}%', type= '', expr= None))
        f = FunctionNode(container, f'%{ident}%', p, body)
        f.Run()
        return f

    
class ReturnNode(ExecNode):
    def __init__(self, container: ExecVarContainer, expr: str):
        super().__init__(container)
        self.expr = expr
    
    def Run(self):
        if self.expr == '':
            return False
        
        self.container.returnVal.append(EvaluateExpr(self.expr, self.container))
        return False


class CallNode(ExecNode):
    def __init__(self, container: ExecVarContainer, ident: str, args: list):
        super().__init__(container)
        self.ident = ident
        self.args = args
    
    def Run(self):
        func: FunctionNode
        func = self.container.functionMap[self.ident]
        func.Call(self.args)

        if len(self.container.returnVal) > 0:
            self.container.returnVal.pop()
        return True


        
        


