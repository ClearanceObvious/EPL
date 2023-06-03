from Parser import *
from Interpreter import Interpreter
import sys

def dump_ast(obj, indent=0, indent_level=0):
    class_name = obj.__class__.__name__

    is_enum = False

    is_nodetype = isinstance(obj, NodeType)
    is_tokentype = isinstance(obj, TokenType)
    
    is_node = issubclass(obj.__class__, Node)

    output = ""

    if is_nodetype or is_tokentype:
        output = obj.name
    else:
        output = f"{class_name}("

        attributes = []
        if isinstance(obj, list):
            for i, item in enumerate(obj):
                attributes.append(f"[{i}]={dump_ast(item, indent + 4, indent_level + 1)}")
        else:
            for attr_name in dir(obj):
                if not attr_name.startswith("__") and not callable(getattr(obj, attr_name)):
                    attr_value = getattr(obj, attr_name)
                    if isinstance(attr_value, (int, float, str)):
                        attributes.append(f"{attr_name}={repr(attr_value)}")
                    else:
                        if is_enum and attr_name == "_name_":
                            attributes.append(f"{obj._name_}")
                        else:
                            attributes.append(f"{attr_name}={dump_ast(attr_value, indent + 4, indent_level + 1)}")

        if len(attributes) > 0:
            output += "\n" + "\n".join([f"{' ' * (indent + 4)}{attr}," for attr in attributes]) + "\n" + " " * (indent_level * 4) + ")"
        else:
            output += ")"

    return output

def display_environment(env, full : bool = False):
    symbol = env.symbolTable
    print('-------- ENV --------')
    for idx, val in symbol.items():
        if full and idx in env.globals: continue

        if val.type in [NodeType.StringNode, NodeType.BooleanNode, NodeType.NullNode, NodeType.NumberNode]:
            if val.type == NodeType.StringNode:
                val = f'"{val.value}"'
            else:
                val = val.value
        else:
            val = val.type.name
        
        print(f'{idx} = {val}')


sysargs = sys.argv[1:]
__type__ = sysargs[0]
filename = sysargs[1]

if filename.split('.')[1] == 'epl':
    file = open(filename, 'r')
    contents = file.read()

    ## LEXING
    lexer = Lexer(contents)
    tokens = lexer.lex()

    ## PARSING
    parser = Parser(tokens)
    ast = parser.parse()

    if __type__ == '-i':
        ## INTERPRETING
        interpreter = Interpreter(ast)
        interpreter.evaluate()

        if sysargs[-1] == '-d' or sysargs[-1] == '-fd':
            print('\n\n')
            display_environment(interpreter.current_env, False if sysargs[-1] == '-fd' else True)

    elif __type__ == '-c':
        print('Compilation coming soon.')
    
    file.close()
else:
    print(f'Invalid File Name {filename}')
