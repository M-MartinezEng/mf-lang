from lexer import Lexer
from parser import Parser, ExpressionStatement, Block
from interpreter import Interpreter

interpreter = Interpreter()


def should_echo_result(tree):
    if isinstance(tree, ExpressionStatement):
        return True
    if isinstance(tree, Block) and tree.statements:
        return isinstance(tree.statements[-1], ExpressionStatement)
    return False

print("mf-lang 1.0 (Interactive Shell)")
while True:
    try:
        text = input("mf-lang >")
        if text.strip() == "": continue
        if text == "exit": break

        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()
        result = interpreter.visit(tree)
        if should_echo_result(tree) and result is not None:
            print(result)
    except Exception as e:
        print(f"Error: {e}")
        continue
