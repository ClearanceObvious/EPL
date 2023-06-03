from Lexer import Token, TokenType, Lexer
from Parser import Parser, Node, NodeType, Global, FunctionNode, VarGetNode, GlobalNode, AttachNode, ReturnNode, FunctionCallNode, VarNode

from time import sleep, time
from random import randint

from Error import *


def copy(obj):
    return type(obj)(obj)

def convert(val: Node):
    if val.type == NodeType.NumberNode:
        return float(val.value)
    elif val.type == NodeType.StringNode:
        return str(val.value)
    elif val.type == NodeType.BooleanNode:
        return bool(val.value)
    elif val.type == NodeType.NullNode:
        return 0

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value):
        self.stack.append(value)
        return value
    
    def pop(self):
        return self.stack.pop()

    def size(self):
        return len(self.stack)

class Environment:
    def __init__(self, interpreter, globals: dict = {}, stack: Stack = Stack(), loop: Stack = Stack()):
        self.symbolTable = globals.copy()
        self.globals = globals.copy()
        self.interpreter = interpreter
        self.fstack = stack
        self.lstack = loop
    
    def get(self, name):
        if name == 'self':
            return SELF
        if name in self.symbolTable:
            node = self.symbolTable[name]
            return node
        else:
            VariableUnexistentError(name, self.interpreter.current_line)
    
    def set(self, name, value):
        self.symbolTable[name] = value
    
    def index(self, name, path):
        global SELF
        var = None
        if isinstance(name, Node):
            var = self.interpreter.visitExpression(name)
        else:
            var = self.get(name)

        obj = None
        lastObj = var

        if var.type == NodeType.StringNode:
            if len(path) > 1:
                return Node(NodeType.NullNode)
            else:
                return Node(NodeType.StringNode, var.value[int(self.interpreter.visitExpression(path[0]).value)])
    
        for node in path:
            if obj == None:
                obj = var.value[self.interpreter.visitExpression(node)]
            else:
                obj = obj.value[self.interpreter.visitExpression(node)]
                if obj.type == NodeType.ObjectNode:
                    lastObj = obj
        
        obj = self.interpreter.visitExpression(obj)
        if (obj.type == NodeType.FunctionNode and lastObj.type == NodeType.ObjectNode):
            SELF = lastObj

        return obj
    
    def dso(self, name, path, value):
        obj = None
        if isinstance(name, Node):
            obj = self.interpreter.visitExpression(name)
        else:
            obj = self.get(name)

        if len(path) > 1:
            obj = obj.value[self.interpreter.visitExpression(path[0])]
            if len(path) > 2:
                for node in path[1:-1]:
                    obj = obj.value[self.interpreter.visitExpression(node)]

        obj.value[self.interpreter.visitExpression(path[-1])] = self.interpreter.visitExpression(value)
    
    def funarg(self, args, val):
        idx = 0
        for arg in args:
            self.set(arg.value, self.interpreter.visitExpression(val[idx]))
            idx += 1
        
    def copy(self):
        return Environment(self.interpreter, self.symbolTable.copy(), self.fstack, self.lstack)

    def differ(self, env2):
        resEnv = {}

        for name, node in self.symbolTable.items():
            if name in env2.symbolTable:
                resEnv[name] = self.interpreter.visitExpression(node)
        
        self.symbolTable = resEnv
    
    def diffimport(self, env2):
        resEnv = self.symbolTable

        for name, node in env2.symbolTable.items():
            if not (name in resEnv):
                resEnv[name] = self.interpreter.visitExpression(node)
        
        self.symbolTable = resEnv
    
    def remglobals(self, obj):
        resEnv = {}

        for i, v in obj.value.items():
            if not (i.value in self.globals):
                resEnv[i] = v
        
        obj.value = resEnv

class Interpreter:
    def __init__(self, ast):
        self.nodes = ast

        self.current_line = 1
        self.current_env = Environment(self)
        self.globals = {
            'log': self.visitExpression(GlobalNode(Global.Log)),
            'sleep': self.visitExpression(GlobalNode(Global.Sleep)),
            'time': self.visitExpression(GlobalNode(Global.Time)),
            'input': self.visitExpression(GlobalNode(Global.Input)),
            'random': self.visitExpression(GlobalNode(Global.Random)),
            'tonumber': self.visitExpression(GlobalNode(Global.ToNumber)),
            'tostring': self.visitExpression(GlobalNode(Global.ToString))
        }
        self.current_env.symbolTable = self.globals.copy()
        self.current_env.globals = self.globals.copy()
    
    def evaluate(self):
        self.visitBlock(self.nodes, True)
    
    def visitBlock(self, block, main: bool = False):
        for stmt in block:
            if self.current_env.fstack.size() != 0:
                break
            if self.current_env.lstack.size() != 0:
                break

            self.visitStatement(stmt, main)
    
    def visitStatement(self, statement: Node, main: bool = False):
        if statement.type == NodeType.VarNode:
            self.visitVarCreateNode(statement)
        
        elif statement.type == NodeType.DSONode:
            self.current_env.dso(statement.name, statement.path, statement.value)
    
        elif statement.type == NodeType.ReturnNode:
            self.current_env.fstack.push(self.visitExpression(statement.returnValue))
        elif statement.type == NodeType.BreakNode:
            self.current_env.lstack.push(0)

        elif statement.type == NodeType.AttachNode:
            statement.function()
        
        elif statement.type == NodeType.NewLineNode:
            self.current_line += 1
        
        elif statement.type == NodeType.ImportNode:
            self.visitImportNode(statement)

        elif statement.type == NodeType.FunctionCallNode:
            return self.visitFunctionCallNode(statement)
        elif statement.type == NodeType.IfStatementNode:
            return self.visitIfStatementNode(statement)
        elif statement.type == NodeType.WhileLoopNode:
            return self.visitWhileLoopNode(statement)
        elif statement.type == NodeType.ForLoopNode:
            return self.visitForLoopNode(statement)
    
    def visitGlobalNode(self, node: Node):
        func = None

        if node.gType == Global.Log:
            def attach(name):
                def func():
                    arg = self.visitExpression(name).value
                    print(arg)
                
                return func

            func = FunctionNode([Node(NodeType.StringNode, '!')], [
                AttachNode(attach((VarGetNode('!'))))
            ])
        elif node.gType == Global.Sleep:
            def attach(value):
                def func():
                    arg = self.visitExpression(value).value
                    sleep(arg)
            
                return func

            func = FunctionNode([Node(NodeType.NumberNode, '!')], [
                AttachNode(attach(VarGetNode('!')))
            ])
        elif node.gType == Global.Time:
            def attach():
                def func():
                    return Node(NodeType.NumberNode, time())

                return func

            func = FunctionNode([], [
                ReturnNode(AttachNode(attach()))
            ])
        elif node.gType == Global.Input:
            def attach(value):
                def func():
                    arg = self.visitExpression(value).value
                    print(arg, end='')
                    return Node(NodeType.StringNode, input(''))
                
                return func
            func = FunctionNode([Node(NodeType.StringNode, '!')], [
                ReturnNode(AttachNode(attach(VarGetNode('!'))))
            ])
        elif node.gType == Global.Random:
            def attach(ax, bx):
                def func():
                    a = self.visitExpression(ax).value
                    b = self.visitExpression(bx).value

                    return Node(NodeType.NumberNode, randint(int(a), int(b)))

                return func

            func = FunctionNode([Node(NodeType.StringNode, '!'), Node(NodeType.StringNode, '!!')], [
                ReturnNode(AttachNode(attach(VarGetNode('!'), VarGetNode('!!'))))
            ])
        
        elif node.gType == Global.ToNumber:
            def attach(value):
                def func():
                    arg = self.visitExpression(value).value
                    return Node(NodeType.NumberNode, float(arg))
                
                return func

            func = FunctionNode([Node(NodeType.StringNode, '!')], [
                ReturnNode(AttachNode(attach(VarGetNode('!'))))
            ])
        elif node.gType == Global.ToString:
            def attach(value):
                def func():
                    arg = self.visitExpression(value).value
                    return Node(NodeType.StringNode, str(arg))
                
                return func

            func = FunctionNode([Node(NodeType.NumberNode, '!')], [
                ReturnNode(AttachNode(attach(VarGetNode('!'))))
            ])
    
        return func

    def visitExpression(self, expression: Node):
        default = [NodeType.NumberNode, NodeType.NullNode, NodeType.BooleanNode, NodeType.StringNode, NodeType.FunctionNode, NodeType.ClassNode]

        if expression.type in default:
            xp = expression
            return xp
        elif expression.type in [NodeType.ObjectNode, NodeType.ArrayNode]:
            return self.visitDSExpression(expression)
        elif expression.type == NodeType.BinOpNode:
            return self.visitBinOpNode(expression)
        elif expression.type == NodeType.UnOpNode:
            return self.visitUnOpNode(expression)
        elif expression.type == NodeType.CondNode:
            return self.visitCondNode(expression)
        elif expression.type == NodeType.FunctionCallNode:
            return self.visitFunctionCallNode(expression)
        elif expression.type == NodeType.VarGetNode:
            return self.current_env.get(expression.name)
        elif expression.type == NodeType.IndexNode:
            return self.current_env.index(expression.name, expression.path)

        elif expression.type == NodeType.GlobalNode:
            return self.visitGlobalNode(expression)
        elif expression.type == NodeType.AttachNode:
            return expression.function()
        
        elif expression.type == NodeType.LengthOpNode:
            lop = self.visitLengthOpNode(expression)
            return lop
    
    def visitUnOpNode(self, node: Node):
        val = self.visitExpression(node.node)

        if val.type == NodeType.BooleanNode:
            return Node(NodeType.BooleanNode, not val.value)

        return Node(NodeType.NumberNode, -val.value)
    
    def visitBinOpNode(self, node: Node):
        left = self.visitExpression(node.left)
        op = node.op
        right = self.visitExpression(node.right)
        result = Node(NodeType.NumberNode, 0)

        if left.type == NodeType.StringNode or right.type == NodeType.StringNode:
            if op == TokenType.PLUS:
                
                if left.type == NodeType.NumberNode and str(left.value).endswith('.0'):
                    left.value = str(left.value)[:-2]
                elif right.type == NodeType.NumberNode and str(right.value).endswith('.0'):
                    right.value = str(right.value)[:-2]

                result.type = NodeType.StringNode
                result.value = str(left.value) + str(right.value)
        else:
            if op == TokenType.PLUS:
                result.value = left.value + right.value
            elif op == TokenType.MINUS:
                result.value = left.value - right.value
            elif op == TokenType.MULTIPLY:
                result.value = left.value * right.value
            elif op == TokenType.DIVIDE:
                if right.value == 0:
                    DivisionByZeroError(self.current_line)
                result.value = left.value / right.value
            elif op == TokenType.POWER:
                result.value = left.value ** right.value
        
        return result

    def visitCondNode(self, node: Node):
        left = self.visitExpression(node.left)
        right = self.visitExpression(node.right)
        op = node.op
        resultNode = Node(NodeType.BooleanNode, 0)

        if not (op in [TokenType.AND, TokenType.OR]):
            left = convert(left)
            right = convert(right)
            if op == TokenType.EEQ:
                if left == right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            elif op == TokenType.NQ:
                if left != right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            elif op == TokenType.LT:
                if left < right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            elif op == TokenType.LTE:
                if left <= right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            elif op == TokenType.GT:
                if left > right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            elif op == TokenType.GTE:
                if left >= right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            else:
                InvalidConditionOperatorError(op, self.current_line)
        else:
            if left.type != NodeType.BooleanNode or right.type != NodeType.BooleanNode:
                InvalidConditionOperatorError(op, self.current_line)
            
            left = left.value
            right = right.value

            if op == TokenType.AND:
                if left and right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            else:
                if left or right:
                    resultNode.value = True
                else:
                    resultNode.value = False
        
        return resultNode

    def visitVarCreateNode(self, node: Node):
        identifier = node.name
        value = self.visitExpression(node.value)
        self.current_env.set(identifier, value)
    
    def visitFunctionCallNode(self, node: Node):
        funNode = self.visitExpression(node.name)
        last_enviroment = self.current_env.copy()
        targetArgs = funNode.args

        if len(targetArgs) != len(node.args):
            FunctionArgumentError(len(targetArgs), len(node.args))

        self.current_env.funarg(targetArgs, node.args)

        if len(funNode.block) > 0:
            self.visitBlock(funNode.block)
        
        if self.current_env.fstack.size() == 0:
            retVal = Node(NodeType.NullNode, 0)
        else:
            retVal = self.current_env.fstack.pop()
        

        retVal = self.visitExpression(retVal)

        self.current_env.differ(last_enviroment)

        return retVal

    def visitIfStatementNode(self, ifst: Node):
        condition = self.visitExpression(ifst.condition)

        elifs = []
        _else = None

        ranElif = False

        lastEnv = self.current_env.copy()

        if len(ifst.elifs) != 0:
            for elf in ifst.elifs:
                elifs.append(elf)
        
        if ifst._else != None:
            _else = ifst._else

        if condition.value:
            self.visitBlock(ifst.body)
        else:
            if len(elifs) > 0:
                for elf in elifs:
                    if self.visitExpression(elf.condition).value:
                        self.visitStatement(elf)
                        ranElif = True
            
            if not ranElif:
                if _else != None:
                    self.visitStatement(_else)
                    return
    

        self.current_env.differ(lastEnv)
    
    def visitWhileLoopNode(self, whln: Node):
        last_env = self.current_env.copy()

        last_lsize = self.current_env.lstack.size()

        while self.visitExpression(whln.condition).value:
            self.visitBlock(whln.body)

            if self.current_env.lstack.size() > last_lsize:
                self.current_env.lstack.pop()
                break
        
        self.current_env.differ(last_env)
    
    def visitLengthOpNode(self, node: Node):
        value = self.visitExpression(node.val)

        if value.type == NodeType.NumberNode:
            return Node(NodeType.NumberNode, value.value)
        elif value.type in [NodeType.ArrayNode, NodeType.ObjectNode, NodeType.StringNode]:
            node = Node(NodeType.NumberNode, len(value.value))
            return node
        else:
            return Node(NodeType.NullNode)
    
    def visitForLoopNode(self, node: Node):
        if node.end != None:
            # Normal Traditional For Loop
            start = self.visitExpression(node.start)
            end = self.visitExpression(node.end)

            if start.type != NodeType.NumberNode or end.type != NodeType.NumberNode:
                TypeError(start.type if start.type != NodeType.NumberNode else end.type, NodeType.NumberNode, self.current_line)
            
            if start.value >= end.value:
                return
            
            last_env = self.current_env.copy()
            last_lsize = self.current_env.lstack.size()

            for num in range(int(start.value), int(end.value) + 1):
                self.current_env.set(node.identifier, Node(NodeType.NumberNode, float(num)))
                self.visitBlock(node.body)

                if self.current_env.lstack.size() > last_lsize:
                    self.current_env.lstack.pop()
                    break 

            self.current_env.differ(last_env)
        else:
            # DS For Loop
            dstruct = self.visitExpression(node.start)

            if not (dstruct.type in [NodeType.ObjectNode, NodeType.ArrayNode]):
                TypeError(dstruct.type, NodeType.ArrayNode, self.current_line)

            last_env = self.current_env.copy()
            last_lsize = self.current_env.lstack.size()

            for key, value in dstruct.value.items():
                data = Node(NodeType.ObjectNode, {
                    Node(NodeType.StringNode, "key"): self.visitExpression(key),
                    Node(NodeType.StringNode, "value"): self.visitExpression(value)
                })

                self.current_env.set(node.identifier, data)
                self.visitBlock(node.body)

                if self.current_env.lstack.size() > last_lsize:
                    self.current_env.lstack.pop()
                    break
            
            self.current_env.differ(last_env)
    
    
    def visitDSExpression(self, expression):
        newValue = {}

        for k, v in expression.value.items():
            newValue[k] = self.visitExpression(v)
        
        return Node(expression.type, newValue)

    def visitImportNode(self, node: Node):
        file = open(self.visitExpression(node.path).value, 'r')
        
        contents = file.read()

        file.close()

        ast = Parser(Lexer(contents).lex()).parse()
        inter = Interpreter(ast)
        inter.evaluate()

        self.current_env.diffimport(inter.current_env)
