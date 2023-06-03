from enum import Enum
from dataclasses import dataclass

from Error import *

SYMBOLS = '-!@#$%^&*()+]}|\\ \';[{:><,/?.~`'
NUMBERS = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyz' + 'abcdefghijklmnopqrstuvwxyz'.upper() + '_'
IDENTIFIER_LETTERS = LETTERS + NUMBERS
STRING = IDENTIFIER_LETTERS + SYMBOLS

KEYWORDS = ['and', 'or', 'return', 'if', 'else', 'while', 'for', 'in', 'break', 'import']
BOOL_VAL = ['true', 'false']
NULL_VAL = 'null'

class TokenType(Enum):
    NEWLINE = 0

    PLUS = 1
    MINUS = 2
    MULTIPLY = 3
    DIVIDE = 4

    NULL = 5
    NUMBER = 6
    STRING = 7
    BOOL = 8

    LPAREN = 9
    RPAREN = 10

    POWER = 11

    KEYWORD = 12
    IDENTIFIER = 13

    LBRACKET = 14
    RBRACKET = 15
    FSTRING = 16

    EEQ = 17

    LT = 18
    LTE = 19
    GT = 20
    GTE = 21

    NQ = 22

    AND = 23
    OR = 24

    NEG = 25
    EQ = 26
    
    LSBRACKET = 27
    RSBRACKET = 28

    COMMA = 29
    DOT = 30

    LENGTHOP = 31

@dataclass
class Token:
    type: TokenType
    value: any = 0
    optional: any = 0

class Lexer:
    def __init__(self, content) -> None:
        self.text = content
        self.currentNum = 0

        self.currentChar = self.text[self.currentNum] if self.currentNum < len(self.text) else None
        self.line = 1
    
    def advance(self):
        self.currentNum += 1
        self.currentChar = self.text[self.currentNum] if self.currentNum < len(self.text) else None
    
    def checkNext(self, char: str, get: bool = False):
        baseRet =  (self.text[self.currentNum + 1] if self.currentNum + 1 < len(self.text) else 'NULL')

        if self.currentNum + 1 < len(self.text) and self.text[self.currentNum + 1] == char:
            return True if not get else self.text[self.currentNum + 1]
        return False if not get else baseRet
    
    def lex(self):
        tokens = []

        while self.currentChar != None:
            if self.currentChar in ' \t\b':
                self.advance()
            elif self.currentChar == '\n':
                self.line += 1

                tokens.append(Token(TokenType.NEWLINE))
                self.advance()
            elif self.currentChar == '.':
                tokens.append(Token(TokenType.DOT))
                self.advance()
            elif self.currentChar == ',':
                tokens.append(Token(TokenType.COMMA))
                self.advance()
            elif self.currentChar == '#':
                tokens.append(Token(TokenType.LENGTHOP))
                self.advance()
            elif self.currentChar == '[':
                tokens.append(Token(TokenType.LSBRACKET))
                self.advance()
            elif self.currentChar == ']':
                tokens.append(Token(TokenType.RSBRACKET))
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Token(TokenType.PLUS))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(TokenType.MINUS))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(TokenType.MULTIPLY))
                self.advance()
            elif self.currentChar == '^':
                tokens.append(Token(TokenType.POWER))
                self.advance()
            elif self.currentChar == '/':
                if self.checkNext('/'):
                    while self.currentChar != None and self.currentChar != '\n':
                        self.advance()
                elif self.checkNext('*'):
                    while self.currentChar != None:
                        self.advance()
                        if self.currentChar == '\n':
                            tokens.append(Token(TokenType.NEWLINE))
                        if self.currentChar == '/' and self.checkNext('*'):
                            self.advance()
                            self.advance()
                            break
                else:
                    tokens.append(Token(TokenType.DIVIDE))
                    self.advance()    
            elif self.currentChar == '(':
                tokens.append(Token(TokenType.LPAREN))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Token(TokenType.RPAREN))
                self.advance()
            elif self.currentChar == '{':
                tokens.append(Token(TokenType.LBRACKET))
                self.advance()
            elif self.currentChar == '}':
                tokens.append(Token(TokenType.RBRACKET))
                self.advance()
            elif self.currentChar == '=':
                if self.checkNext('='):
                    tokens.append(Token(TokenType.EEQ, 0))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.EQ, 0))
                    self.advance()
            elif self.currentChar == '!':
                if self.checkNext('='):
                    tokens.append(Token(TokenType.NQ, 0))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.NEG, 0))
                    self.advance()
            elif self.currentChar == '>':
                if self.checkNext('='):
                    tokens.append(Token(TokenType.GTE, 0))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.GT, 0))
                    self.advance()
            elif self.currentChar == '<':
                if self.checkNext('='):
                    tokens.append(Token(TokenType.LTE, 0))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.LT, 0))
                    self.advance()
            elif self.currentChar == '"':
                self.advance()
                tokens.append(self.lex_string())
                if self.currentChar != '"':
                    InvalidCharacterError(self.currentChar, self.line)
                self.advance()
            elif self.currentChar in NUMBERS:
                tokens.append(Token(TokenType.NUMBER, self.lex_number()))
            elif self.currentChar in LETTERS:
                tokens.append(self.lex_id())
            else:
                InvalidCharacterError(self.currentChar, self.line)
        
        return tokens

    def lex_number(self):
        nstr = ''
        dotcount = 0

        while self.currentChar != None and self.currentChar in NUMBERS + '.':
            if self.currentChar == '.':
                if dotcount == 1: InvalidCharacterError(self.currentChar, self.line)
                dotcount += 1
            
            nstr += self.currentChar
            self.advance()
        
        if nstr.endswith('.'): nstr = nstr[:-1]

        return float(nstr)

    def lex_string(self):
        string = ''
        modifiers = {}
        is_f_string = False
        
        idx = 0
        while self.currentChar != None and self.currentChar in STRING:
            # Character Escaping
            if self.currentChar == '\\':
                self.advance()
                if self.currentChar in 'n':
                    string += '\n'
                else:
                    string += self.currentChar
                    
                self.advance()

                idx += 1; continue
            
            # Formatted Strings
            if self.currentChar == '{':
                self.advance()
                inputstream = ''
                while self.currentChar != None and not (self.currentChar in '{}'):
                    inputstream += self.currentChar
                    self.advance()

                idx += 1
                is_f_string = True
                modifiers[str(idx - 1)] = Lexer(inputstream).lex()
                self.advance()
            else:
                string += self.currentChar
                idx += 1
                self.advance()


        type = TokenType.FSTRING if is_f_string else TokenType.STRING
        return Token(type, string, modifiers)
    
    def lex_id(self):
        identifier = ''
        while self.currentChar != None and self.currentChar in IDENTIFIER_LETTERS:
            identifier += self.currentChar
            self.advance()
        
        if identifier == NULL_VAL:
            return Token(TokenType.NULL, 0)
        elif identifier in BOOL_VAL:
            if identifier == BOOL_VAL[0]:
                return Token(TokenType.BOOL, True)
            else:
                return Token(TokenType.BOOL, False)
        elif identifier in KEYWORDS:
            return Token(TokenType.KEYWORD, identifier)
        else:
            return Token(TokenType.IDENTIFIER, identifier)
