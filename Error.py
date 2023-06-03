from enum import Enum

class ErrorType(Enum):
    InvalidCharacterError = 0   # Lexing Error
    InvalidSyntaxError = 1      # Parsing Error

    # Interpreter Errors
    DivisionByZeroError = 2
    InvalidConditionOperatorError = 3
    VariableError = 4
    FunctionArgumentError = 5
    TypeError = 6
    

class BaseError:
    def __init__(self, type: ErrorType, message: str = 'Base Unknown Error Case', line: int=1):
        raise Exception(f'{type.name} LINE {line}: {message}')

class InvalidCharacterError(BaseError):
    def __init__(self, character: str, line: int):
        message = f'Unexpected Character "{character}" appeared.'

        super().__init__(ErrorType.InvalidCharacterError, message, line)

class InvalidSyntaxError(BaseError):
    def __init__(self, Token: object, line: int=1, extraMessage: str=''):
        message = f'Illegal Syntax Occured "{Token.type.name} : {Token.value}". {extraMessage}'

        super().__init__(ErrorType.InvalidSyntaxError, message, line)

class DivisionByZeroError(BaseError):
    def __init__(self, line: int=1):
        message = 'Cannot divide by 0, result undefined.'

        super().__init__(ErrorType.DivisionByZeroError, message, line)

class InvalidConditionOperatorError(BaseError):
    def __init__(self, tokenType: object, line: int=1):
        message = f'Invalid Operator in Condition detected "{tokenType.name}".'

        super().__init__(ErrorType.InvalidConditionOperatorError, message, line)

class VariableError(BaseError):
    def __init__(self, varName: str, line: int=1):
        message = f'Variable {varName} already exists.'

        super().__init__(ErrorType.VariableError, message, line)

class VariableUnexistentError(BaseError):
    def __init__(self, varName: str, line: int=1):
        message = f'Variable {varName} does not exist.'

        super().__init__(ErrorType.VariableError, message, line)

class FunctionArgumentError(BaseError):
    def __init__(self, numOfArguments, numOfParamaters, line: int=1):
        message = f'Number of Arguments {numOfArguments} does not match with number of paramaters {numOfParamaters}.'

        super().__init__(ErrorType.FunctionArgumentError, message, line)

class TypeError(BaseError):
    def __init__(self, type: Enum, expectedType: Enum, line: int = 1):
        message = f'Wrong Type {type.name}, expected {expectedType.name}.'

        super().__init__(ErrorType.TypeError, message, line)
