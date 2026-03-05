from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

interpreter = Interpreter()

print("mf-lang 1.0 (Interactive Shell)")
while True:
    try:
        text = input("mf-lang >")
        if text.strip() == "": continue
        if text == "exit": break

        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()
        interpreter.visit(tree)
    except Exception as e:
        print(f"Error: {e}")
        continue
