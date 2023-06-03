from enum import Enum
from dataclasses import dataclass

from Lexer import *

class NodeType(Enum):
    NewLineNode = -1

    NumberNode = 0
    BinOpNode = 1
    UnOpNode = 2

    NullNode = 3
    StringNode = 4
    BooleanNode = 5

    CondNode = 6

    VarNode = 7
    VarGetNode = 8

    IndexNode = 9
    DSONode = 10

    ArrayNode = 11
    ObjectNode = 12

    FunctionNode = 16
    FunctionCallNode = 17
    ReturnNode = 18

    IfStatementNode = 19

    WhileLoopNode = 20
    LengthOpNode = 21

    ForLoopNode = 22
    BreakNode = 23

    GlobalNode = 24
    AttachNode = 25

    ImportNode = 26
    ClassNode = 27

class Global(Enum):
    Log = 0
    Sleep = 1
    Time = 2
    Input = 3
    Random = 4
    ToNumber = 5
    ToString = 6

def getNodeFromToken(type):
    if type == TokenType.NUMBER:
        return NodeType.NumberNode
    elif type == TokenType.STRING:
        return NodeType.StringNode
    elif type == TokenType.BOOL:
        return NodeType.BooleanNode
    elif type == TokenType.NULL:
        return NodeType.NullNode
    else:
        raise Exception(f'PARSER METHOD "getNodeFromToken": Unable to cast TokenType to NodeType "{type.name}"')

@dataclass
class Node:
    type: NodeType
    value: any = 0

    def __hash__(self):
        return self.type.value

class BinOpNode(Node):
    def __init__(self, left: Node, op: TokenType, right: Node):
        super().__init__(NodeType.BinOpNode, 0)
        self.left = left
        self.op = op
        self.right = right

class UnOpNode(Node):
    def __init__(self, node: Node):
        super().__init__(NodeType.UnOpNode, 0)
        self.node = node

class CondNode(Node):
    def __init__(self, left: Node, op: TokenType, right: Node):
        super().__init__(NodeType.CondNode, 0)
        self.left = left
        self.right = right
        self.op = op

class VarNode(Node):
    def __init__(self, name: str, value: Node):
        super().__init__(NodeType.VarNode, 0)
        self.name = name
        self.value = value

class VarGetNode(Node):
    def __init__(self, name: str):
        super().__init__(NodeType.VarGetNode, 0)
        self.name = name

class IndexNode(Node):
    def __init__(self, name: str, path: list):
        super().__init__(NodeType.IndexNode, 0)
        self.name = name
        self.path = path

class DSONode(Node):
    def __init__(self, name: str, path: list, val: Node):
        super().__init__(NodeType.DSONode, 0)
        self.name = name
        self.path = path
        self.value = val

class ArrayNode(Node):
    def __init__(self, value: dict):
        super().__init__(NodeType.ArrayNode, 0)
        self.value = value

class ObjectNode(Node):
    def __init__(self, value: dict):
        super().__init__(NodeType.ObjectNode, 0)
        self.value = value

class ReturnNode(Node):
    def __init__(self, returnValue: Node = Node(NodeType.NullNode, 0)):
        super().__init__(NodeType.ReturnNode, 0)
        self.returnValue = returnValue

class FunctionNode(Node):
    def __init__(self, args: list, block: list):
        super().__init__(NodeType.FunctionNode, 0)
        self.args = args
        self.block = block

class FunctionCallNode(Node):
    def __init__(self, args: list, name: str or FunctionNode, path: IndexNode = None):
        super().__init__(NodeType.FunctionCallNode, 0)
        self.args = args
        self.name = name
        self.path = path

class IfStatementNode(Node):
    def __init__(self, condition: CondNode, body: list = [], elifs: list = [], _else: Node = None):
        super().__init__(NodeType.IfStatementNode, 0)
        self.condition = condition
        self.body = body
        self.elifs = elifs
        self._else = _else

class WhileLoopNode(Node):
    def __init__(self, condition: CondNode, body: list = []):
        super().__init__(NodeType.WhileLoopNode, 0)
        self.condition = condition
        self.body = body

class LengthOpNode(Node):
    def __init__(self, val: Node):
        super().__init__(NodeType.LengthOpNode, 0)
        self.val = val

class ForLoopNode(Node):
    def __init__(self, body, identifier, start: Node = None, end: Node = None):
        super().__init__(NodeType.ForLoopNode, 0)
        self.body = body
        self.identifier = identifier
        self.start = start
        self.end = end

class GlobalNode(Node):
    def __init__(self, gType: Global):
        super().__init__(NodeType.GlobalNode, 0)
        self.gType = gType

class AttachNode(Node):
    def __init__(self, func):
        super().__init__(NodeType.AttachNode, 0)
        self.function = func

class ImportNode(Node):
    def __init__(self, path):
        super().__init__(NodeType.ImportNode, 0)
        self.path = path

class ClassNode(Node):
    def __init__(self, body: list):
        super().__init__(NodeType.ClassNode, 0)
        self.body = body

class Parser:
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.currentNum = 0
        self.currentToken = self.tokens[0] if self.currentNum < len(self.tokens) else None

        self.current_line = 1
        self.ast = []
    
    def check(self, tokenType: TokenType or list):
        while self.currentToken != None and self.currentToken.type == TokenType.NEWLINE:
            self.advance()

        if self.currentToken == None or self.currentToken.type != tokenType:
            tt = self.currentToken if self.currentToken else Token(TokenType.NULL)
            InvalidSyntaxError(tt, self.current_line, f'Expected {tokenType.name}.')
        
        val = self.currentToken.value
        self.advance()

        return val

    def bcheck(self, tokenType: TokenType or list):
        found = False

        if self.currentToken != None and self.currentToken.type == TokenType.NEWLINE:
            self.advance()
        
        if self.currentToken == None: return False
        
        if isinstance(tokenType, TokenType):
            if self.currentToken.type != tokenType:
                return False
        else:
            for tt in tokenType:
                if self.currentToken.type == tt:
                    found = True
            
            return found
        
        return True
    
    def checkNext(self, tokenType: TokenType, next: int = 0):
        idx = 1
        cond1 = self.currentNum + idx < len(self.tokens)
        try:
            cond2 = self.tokens[self.currentNum + idx] == TokenType.NEWLINE
        except:
            cond2 = False

        while cond1 and cond2:
            idx += 1
        
        idx += next

        try:
            cond1 = self.tokens[self.currentNum + idx] != None
            cond2 = self.tokens[self.currentNum + idx].type == tokenType
        except:
            cond1 = False
            cond2 = False

        if cond1 and cond2:
            return True
        
        return False
    
    def fstring(self):
         # Formatting String Interpolation
        if len(self.currentToken.optional) == 0:
            return Node(NodeType.StringNode, self.currentToken.value)

        fstr = self.currentToken.value
        string = None
        keys = []
        idx = 0

        # Setting up the keys
        for key in self.currentToken.optional.keys():
            keys.append(key)

        # String Interpolation
        while idx < len(self.currentToken.optional):
            key = keys[idx]
            value = self.currentToken.optional[key]

            tval = None
            if idx + 1 >= len(self.currentToken.optional):
                tval = fstr[int(key) - idx:]
            else:
                tval = fstr[int(key) - idx : int(keys[idx + 1]) - idx - 1]

            expr = Parser(value).expression()
            cstring = string or Node(NodeType.StringNode, fstr[:int(key)])
            string = BinOpNode(cstring, TokenType.PLUS, expr)
            string = BinOpNode(string, TokenType.PLUS, Node(NodeType.StringNode, tval))

            idx += 1
        
        self.advance()
        return string
    
    def advance(self):
        nl = TokenType.NEWLINE
        self.currentNum += 1
        if self.currentNum < len(self.tokens):
            while self.currentNum < len(self.tokens) and self.tokens[self.currentNum].type == nl:
                self.currentNum += 1
                self.current_line += 1
                self.ast.append(Node(NodeType.NewLineNode, 0))

            self.currentToken = self.tokens[self.currentNum] if self.currentNum < len(self.tokens) else None
        else:
            self.currentToken = None
    
    def parse(self):
        if self.currentToken == None:
            return Node(NodeType.NullNode)

        self.block()
        return self.ast

    def block(self, ret :bool = False):
        lst = []

        while self.currentToken != None and not self.bcheck(TokenType.RBRACKET):
            if ret == True:
                lst.append(self.statement())
            else:
                self.ast.append(self.statement())
        
        return lst

    def statement(self):
        COMP = False
        COMP_OP = None
        compound_ops = [TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.POWER]

        cond = self.checkNext(compound_ops[0]) or self.checkNext(compound_ops[1]) or self.checkNext(compound_ops[2])
        cond2 = self.checkNext(compound_ops[3]) or self.checkNext(compound_ops[4])

        if self.bcheck(TokenType.IDENTIFIER) and (self.checkNext(TokenType.EQ) or cond or cond2):
            id = self.check(TokenType.IDENTIFIER)

            # Compound Operators
            if self.bcheck(compound_ops):
                COMP = True
                COMP_OP = self.currentToken.type
                self.advance()

            self.check(TokenType.EQ)
            val = self.expression()

            if COMP:
                return VarNode(id, BinOpNode(VarGetNode(id), COMP_OP, val))
            else:
                return VarNode(id, val)

        elif self.bcheck(TokenType.IDENTIFIER) and (self.checkNext(TokenType.LSBRACKET) or self.checkNext(TokenType.DOT)):
            path = []
            id = self.check(TokenType.IDENTIFIER)
            while self.bcheck(TokenType.LSBRACKET) or self.bcheck(TokenType.DOT):
                last_type = self.currentToken.type
                self.advance()

                if last_type == TokenType.DOT:
                    path.append(Node(NodeType.StringNode, self.check(TokenType.IDENTIFIER)))
                else:
                    path.append(self.expression())
                    self.check(TokenType.RSBRACKET)

            # Compound Operators
            if self.bcheck(compound_ops):
                COMP = True
                COMP_OP = self.currentToken.type
                self.advance()
            
            # Modifier
            left = IndexNode(id, path)        
            left = self.modifier(left)
            if left.type == NodeType.FunctionCallNode:
                return left


            self.check(TokenType.EQ)
            val = self.expression()

            if COMP:
                return DSONode(id, path, BinOpNode(IndexNode(id, path), COMP_OP, val))
            else:
                return DSONode(id, path, val)
        elif self.bcheck(TokenType.KEYWORD):
            kw = self.check(TokenType.KEYWORD)
            if kw == KEYWORDS[2]:
                # Return statement
                if self.bcheck(TokenType.RBRACKET):
                    return ReturnNode()
                else:
                    return ReturnNode(self.expression())
            elif kw == KEYWORDS[3]:
                # If statement
                return self.ifstatement()
            elif kw == KEYWORDS[5]:
                # While Loop
                return self.whileloop()
            elif kw == KEYWORDS[6]:
                # For Loop
                return self.forloop()
            elif kw == KEYWORDS[8]:
                # Break
                return Node(NodeType.BreakNode)
            elif kw == KEYWORDS[9]:
                # Import
                return ImportNode(self.expression())
        else:
            expr = self.expression()

            if expr.type != NodeType.FunctionCallNode:
                InvalidSyntaxError(expr, self.current_line, 'Expected Function call')
            
            return expr

    def expression(self):
        left = self.cexpr()
        
        andval = KEYWORDS[0]
        orval = KEYWORDS[1]

        while self.currentToken != None and self.currentToken.type == TokenType.KEYWORD:
            op = self.currentToken.value

            if op == andval:    op = TokenType.AND
            elif op == orval:   op = TokenType.OR
            else:               break

            self.advance()
            left = CondNode(left, op, self.cexpr())

        return left

    def cexpr(self):
        left = self.expr()
        valid =  [TokenType.EEQ, TokenType.NQ, TokenType.LTE, TokenType.LT, TokenType.GT, TokenType.GTE]

        while self.currentToken != None and self.currentToken.type in valid:
            op = self.currentToken.type
            self.advance()
            left = CondNode(left, op, self.expr())

        return left

    def expr(self):
        left = self.term()

        while self.currentToken != None and self.currentToken.type in [TokenType.PLUS, TokenType.MINUS] and not self.checkNext(TokenType.EQ):
            op = self.currentToken.type
            self.advance()
            left = BinOpNode(left, op, self.term())
        

        return left

    def term(self):
        left = self.factor()

        while self.currentToken != None and self.currentToken.type in [TokenType.MULTIPLY, TokenType.DIVIDE] and not self.checkNext(TokenType.EQ):
            op = self.currentToken.type
            self.advance()
            left = BinOpNode(left, op, self.factor())
        
        return left
    

    def factor(self):
        left = self.modifier()

        while self.currentToken != None and self.bcheck(TokenType.POWER) and not self.checkNext(TokenType.EQ):
            self.advance()
            left = BinOpNode(left, TokenType.POWER, self.modifier())
        
        return left

    def modifier(self, left: any = None):
        left = left or self.atom()

        modifierTokens = [TokenType.LPAREN, TokenType.LSBRACKET, TokenType.DOT]
        
        while self.currentToken != None and self.currentToken.type in modifierTokens:
            tok = self.currentToken.type

            if tok == TokenType.LPAREN:
                # Function Call
                arglist = []
                self.check(TokenType.LPAREN) 
                while not self.bcheck(TokenType.RPAREN):
                    arglist.append(self.expression())
                    if self.bcheck(TokenType.RPAREN):
                        break
                    self.check(TokenType.COMMA)
                
                self.check(TokenType.RPAREN)
                left = FunctionCallNode(arglist, left)
            else:
                # Index
                path = []
                while self.bcheck(TokenType.LSBRACKET) or self.bcheck(TokenType.DOT):
                    last_type = self.currentToken.type
                    self.advance()

                    if last_type == TokenType.DOT:
                        path.append(Node(NodeType.StringNode, self.check(TokenType.IDENTIFIER)))
                    else:
                        path.append(self.expression())
                        self.check(TokenType.RSBRACKET)
                
                left = IndexNode(left, path)

        return left
    
    def atom(self):
        if self.currentToken != None:
            if self.currentToken.type == TokenType.FSTRING:
                return self.fstring()
            elif self.currentToken.type in [TokenType.NUMBER, TokenType.BOOL, TokenType.NULL, TokenType.STRING]:
                type = self.currentToken.type
                value = self.currentToken.value
                self.advance()
                return Node(getNodeFromToken(type), value)
            elif self.currentToken.type == TokenType.LENGTHOP:
                self.advance()
                return LengthOpNode(self.atom())
            elif self.currentToken.type == TokenType.LPAREN:
                # Functions or simple change of operations
                arglist = []
                body = []
                func = False
                expr = None

                self.check(TokenType.LPAREN)
                if not self.bcheck(TokenType.RPAREN):
                    expr = self.expression()

                node = None if not isinstance(expr, VarGetNode) else expr.name
                if self.bcheck(TokenType.COMMA) and node != None:
                    # We're dealing with a function
                    func = True
                    arglist.append(Token(TokenType.IDENTIFIER, expr.name))
                    while self.bcheck(TokenType.COMMA):
                        self.advance()
                        arglist.append(Token(TokenType.IDENTIFIER, self.check(TokenType.IDENTIFIER)))
                
                self.check(TokenType.RPAREN)

                if self.bcheck(TokenType.EQ) and self.checkNext(TokenType.GT) and len(arglist) == 0:
                    if node != None:
                        arglist.append(Token(TokenType.IDENTIFIER, expr.name))
                    func = True
                    

                if not func:
                    return expr or Node(NodeType.NullNode)

                # Checking for the rest of the syntax
                self.check(TokenType.EQ); self.check(TokenType.GT)  # "=>"

                # Checking if there's a body
                if self.bcheck(TokenType.LBRACKET):
                    self.advance()
                    body = self.block(True)
                    self.check(TokenType.RBRACKET)
                else:
                    body = [ReturnNode(self.expression())]
                

                return FunctionNode(arglist, body)
    
            elif self.currentToken.type in [TokenType.MINUS, TokenType.NEG]:
                self.advance()
                return UnOpNode(self.atom())
            elif self.currentToken.type == TokenType.IDENTIFIER:
                path = []
                
                id = self.currentToken.value
                self.advance()

                return VarGetNode(id)

            elif self.currentToken.type == TokenType.LSBRACKET:
                return self.datastructure()
            else:
                InvalidSyntaxError(self.currentToken, self.current_line, 'Expected Literal.')
        else:
            InvalidSyntaxError(self.currentToken, self.current_line, 'Expected Literal, got null.')

    def datastructure(self):
        self.check(TokenType.LSBRACKET)
        
        valueList = {}
        idx = 0

        if self.bcheck(TokenType.IDENTIFIER) and self.checkNext(TokenType.EQ):
            while not self.bcheck(TokenType.RSBRACKET):
                id = Node(NodeType.StringNode, self.check(TokenType.IDENTIFIER))
                self.check(TokenType.EQ)
                valueList[id] = self.expression()
            
            self.check(TokenType.RSBRACKET)
            return ObjectNode(valueList)
        else:
            while not self.bcheck(TokenType.RSBRACKET):
                valueList[Node(NodeType.NumberNode, idx)] = self.expression()
                idx += 1

                if not (self.currentToken.type == TokenType.COMMA):
                    break

                self.check(TokenType.COMMA)

            self.check(TokenType.RSBRACKET)
            return ArrayNode(valueList)
    
    def ifstatement(self, check_elifs: bool = True):
        condition = self.expression()
        elifs = []
        els = None
        
        IFKW = KEYWORDS[3]
        ELSEKW = KEYWORDS[4]

        self.check(TokenType.LBRACKET)
        body = self.block(True)
        self.check(TokenType.RBRACKET)

        if check_elifs == False:
            return IfStatementNode(condition, body)

        while self.bcheck(TokenType.KEYWORD) and self.currentToken.value == ELSEKW:
            self.advance()
            if self.bcheck(TokenType.KEYWORD) and self.currentToken.value == IFKW:
                self.advance()
                elifs.append(self.ifstatement(False))
            else:
                self.check(TokenType.LBRACKET)
                els = IfStatementNode(CondNode(Node(NodeType.NullNode), TokenType.EEQ, Node(NodeType.NullNode)), self.block(True))
                self.check(TokenType.RBRACKET)
                break
        
        return IfStatementNode(condition, body, elifs, els)

    def whileloop(self):
        condition = self.expression()

        self.check(TokenType.LBRACKET)
        body = self.block(True)
        self.check(TokenType.RBRACKET)

        return WhileLoopNode(condition, body)
    
    def forloop(self):
        id = self.check(TokenType.IDENTIFIER)
        kw = self.check(TokenType.KEYWORD)
        if kw != KEYWORDS[7]:
            # "in"
            InvalidSyntaxError(Token(TokenType.KEYWORD, kw), self.current_line, 'Expected "in"')
        
        expr1 = self.expression()

        if not self.bcheck(TokenType.COMMA):
            self.check(TokenType.LBRACKET)
            body = self.block(True)
            self.check(TokenType.RBRACKET)
            return ForLoopNode(body, id, expr1)
        else:
            self.advance()
            expr2 = self.expression()
            self.check(TokenType.LBRACKET)
            body = self.block(True)
            self.check(TokenType.RBRACKET)
            return ForLoopNode(body, id, expr1, expr2)
