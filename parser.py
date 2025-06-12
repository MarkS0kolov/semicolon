from lexer import main_lexer
from pidigit import PiDigit 
import bullshit # exceptions
#* improved annotations
from typing import Any, Literal, NoReturn
from __future__ import annotations

class ASTNode:
    '''
    Making AST nodes

    Methods:
        __init__ - magic method for initialization
        add_child - adding child's ASTNode to children list
        __repr__ - magic method for easy representation
    '''
    def __init__(self, type: str, value: Any = None) -> NoReturn:
        self.type: str = type
        self.value: Any = value
        self.children: list[ASTNode] = []

    def add_child(self, child: ASTNode) -> NoReturn:
        self.children.append(child)

    def __repr__(self, level: int = 0) -> str:
        indent = "  " * level
        value_str = f": {self.value}" if self.value is not None else ""
        result = f"{indent}{self.type}{value_str}"
        for child in self.children:
            result += "\n" + child.__repr__(level + 1)
        return result

class Parser:
    '''
    Class for parsing tokens into AST node
    '''
    def __init__(self, tokens: list[tuple[str, str]]):
        self.tokens = tokens
        self.current_token_index: int = 0
        self.count: int = 1
    
    def get_current_token(self) -> None | tuple[str, str]:
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None
    
    def consume(self) -> NoReturn:
        self.current_token_index += 1
    
    def parse(self) -> ASTNode | bullshit.Bullshit:
        '''
        Main function in Parser
        '''
        node: ASTNode = []
        while self.get_current_token():
            result = self.parse_statements()
            if isinstance(result, bullshit.Bullshit):
                return result
            node.append(result)
        return node
    
    def parse_statements(self, stop: str = 'ISP') -> ASTNode | bullshit.Bullshit:
        '''
        Spreading by first token
        '''
        statement: ASTNode | None = None
        if self.get_current_token() and self.get_current_token()[0] == 'ISP':
            self.consume()
            match self.get_current_token()[0]:
                case 'DSC':
                    self.consume()
                    result = self.data_parser()
                    if isinstance(result, bullshit.Bullshit):
                        return result
                    statement = result
                case 'ISC':
                    self.consume()
                    result = self.instruction_parser(stop)
                    if isinstance(result, bullshit.Bullshit):
                        return result
                    statement = result
                case 'ISP':
                    self.consume()
                    statement = (ASTNode(""))
                case _:
                    return bullshit.SyntaxFailure("Unknown instruction: " + self.get_current_token()[1])
            return statement
        return bullshit.SyntaxFailure( "any instruction should start and end with a instruction splitter (',,'). Maybe you forgot one?")
    
    def instruction_parser(self, stop: str) -> ASTNode | bullshit.Bullshit:
        if self.get_current_token():
            instruction = self.get_current_token()[0]
            self.consume()
            args: list = []
            while self.get_current_token() and self.get_current_token()[0] != stop:
                if self.get_current_token()[0] == 'DSC':
                    self.consume()
                    result = self.data_parser()
                    if isinstance(result, bullshit.Bullshit):
                        return result
                    args.append(result)
                else:
                    return bullshit.SyntaxFailure("expected data section or instruction splitter")
            instructionNode = ASTNode(instruction)
            for arg in args:
                instructionNode.add_child(arg)
            return instructionNode
        return bullshit.SyntaxFailure("expected an instruction's name")

    def data_parser(self) -> ASTNode | bullshit.Bullshit:
        if self.get_current_token():
            match self.get_current_token()[0]:
                case 'NUM':
                    self.consume()
                    if self.get_current_token() and self.get_current_token()[0] == 'DEFAULT':
                        smc_value = self.get_current_token()[1]
                        pid_num = PiDigit(smc_value.count('.'), smc_value.count(','))
                        resNode = ASTNode("NUM", int(pid_num))
                        self.consume()
                    elif not self.get_current_token():
                        return bullshit.SyntaxFailure("expected data after datatype")
                    return bullshit.TypeFailure("invalid data representation")
                case 'BUL':
                    self.consume()
                    if self.get_current_token() and self.get_current_token()[0] == 'DEFAULT':
                        real_value = self.get_current_token()[1] == '.'
                        resNode = ASTNode("BUL", real_value)
                        self.consume()
                case "ISP":
                    result = self.parse_statements('DSP')
                    if isinstance(result, bullshit.Bullshit):
                        return result
                    resNode = result
                case "ARR":
                    self.consume()
                    resList: list = []
                    while self.get_current_token() and self.get_current_token()[0] != 'DSP':
                        if self.get_current_token()[0] == 'DSC':
                            self.consume()
                            result = self.data_parser()
                            if isinstance(result, bullshit.Bullshit):
                                return result
                            resList.append(result)
                        else:
                            return bullshit.SyntaxFailure("expected data section in array")
                    resNode = ASTNode("ARR", resList)
                case _:
                    return bullshit.TypeFailure(f"invalid datatype '{self.get_current_token()[1]}'")
            if self.get_current_token() and self.get_current_token()[0] == 'DSP':
                self.consume()
                return resNode
            return bullshit.SyntaxFailure("expected data splitter (',.') after data")
        return bullshit.SyntaxFailure("expected datatype first in data section")

if __name__ == '__main__':
    code = input('>>> ')

    tokens = main_lexer(code)
    if isinstance(tokens, bullshit.Bullshit):
        print("Lexer error:")
        print(tokens)
    else:
        print("Tokens:")
        print(tokens[0])

        parser = Parser(tokens[0])
        
        ast = parser.parse()
        if isinstance(ast, bullshit.Bullshit):
            print("\033[31mParser error:")
            print(ast)
        else:
            print("\nAST:")
            print(ast)
