from lexer import main_lexer, INSTRUCTIONS
from parser import Parser, ASTNode
import bullshit
#* improved annotations
from typing import Any, Literal, NoReturn
from __future__ import annotations

variables = {}

class Interpreter:    
    def interpret(self, node: ASTNode) -> None | bullshit.Bullshit | Any:
        match node.type:
            case "LOG":
                if node.children:
                    s: str = ""
                    value = self.evaluate(node.children[0]) 
                    if type(value) == list:
                        for element in value:
                            s += str(element) + ', '
                        s = s[:-2]
                    else:
                        return bullshit.TypeFailure("any instruction or function must" \
                        " contain an\033[4m array\033[0m (even an empty one) of arguments after it")
                    print(s)
                    return None
                return bullshit.SyntaxFailure("any instruction or function must" \
                        " contain an array (even an empty one) of arguments after it")
            case "TYP":
                if node.children:
                    return node.children[0].type if node.children else "NOT"
                return bullshit.TypeFailure("TYP (type) expects maximum 1 argument, got {len(node.children)}")
            case "TBL":
                if node.children:
                    value = self.evaluate(node.children[0])
                    if node.children[0].type in ["NUM", "BUL", "ARR", "STR", "NOT"]:
                        return bool(node.children[0])
                    else:
                        return False
                return bullshit.TypeFailure(f"TBL (to bool) expects maximum 1 argument, got {len(node.children)}")
    def evaluate(self, node: ASTNode) -> Any:       
        match node.type:
            case instruction if instruction in INSTRUCTIONS:
                return self.interpret(node)
            case "ARR":
                return [self.evaluate(element) for element in node.value]
            case _:
                return node.value

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
            interpreter = Interpreter()
            print("\n\033[34mOutput:\033[0m\n")
            for statement in ast:
                res = interpreter.interpret(statement)
                if isinstance(res, bullshit.Bullshit):
                    print(res)