from lexer import TokenType


class ASTNode:
    pass

class BinOP(ASTNode):
    """This represents a binary operation."""
    OP_SYMBOLS = {
        TokenType.PLUS: "+",
        TokenType.MINUS: "-",
        TokenType.MULTIPLY: "*",
        TokenType.DIVIDE: "/",
    }

    def __init__(self, left, op, right):
        self.left = left   # The node on the left
        self.op = op       # The operator token
        self.right = right # The node on the right

    def __repr__(self):
        op_symbol = self.OP_SYMBOLS.get(self.op.type, str(self.op))
        return f"({self.left} {op_symbol} {self.right})"

class Number(ASTNode):
    """This represents a literal number"""
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        # Number nodes only hold a scalar value
        return str(self.value)

class FloatNode(ASTNode):
    """This represents a literal float."""
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return str(self.value)

class StringNode(ASTNode):
    """This represents a string literal"""
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f'"{self.value}"'

class VarAssign(ASTNode):
    """This represents a variable assignment"""
    def __init__(self, name, value_node):
        self.name = name              # The variable name
        self.value_node = value_node  # The AST node representing the value

class VarAccess(ASTNode):
    """This represents variable access"""
    def __init__(self, token):
        self.token = token            # The ID token
        self.name = token.value       # The variable name string

class PrintStatement(ASTNode):
    def __init__(self,value_node):
        self.value_node = value_node

class PingStatement(ASTNode):
    def __init__(self,target_node):
        self.target_node = target_node # will usually be a variable or a string

class LatencyStatement(ASTNode):
    def __init__(self, target_node, variable_name):
        self.target_node = target_node
        self.variable_name = variable_name

class ExitStatement(ASTNode):
    pass

class ClearStatement(ASTNode):
    pass

class TypeStatement(ASTNode):
    def __init__(self, value_node):
        self.value_node = value_node

class HelpStatement(ASTNode):
    pass

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        """Verify the current token and move to the next"""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f"Invalid syntax: Expected {token_type,}, got {self.current_token.type}")

    def peek_token(self):
        """Look ahead one token without consuming input."""
        saved_pos = self.lexer.pos
        saved_char = self.lexer.current_char
        token = self.lexer.get_next_token()
        self.lexer.pos = saved_pos
        self.lexer.current_char = saved_char
        return token

    def factor(self):
        """factor : NUMBER | L PAREN expr R PAREN"""
        token = self.current_token
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return Number(token)
        elif token.type == TokenType.FLOAT:
            self.eat(TokenType.FLOAT)
            return FloatNode(token)
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return StringNode(token)
        elif token.type == TokenType.ID:
            self.eat(TokenType.ID)
            return VarAccess(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            # RECURSION: Start the expression logic again
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        else:
            raise Exception(f"Invalid syntax: Unexpected token {token.type}")

    def statement(self):
        """statement : ID ASSIGN expr | expr"""
        if self.current_token.type == TokenType.PRINT:
            self.eat(TokenType.PRINT)
            value = self.comparison()
            return PrintStatement(value)
        elif self.current_token.type == TokenType.PING:
            self.eat(TokenType.PING) # for now, assume we pass a variable or a string
            target = self.comparison()
            return PingStatement(target)
        elif self.current_token.type == TokenType.LATENCY:
            self.eat(TokenType.LATENCY)
            target = self.comparison()
            self.eat(TokenType.ASSIGN)
            var_token = self.current_token
            self.eat(TokenType.ID)
            return LatencyStatement(target, var_token.value)
        elif self.current_token.type == TokenType.HELP:
            self.eat(TokenType.HELP)
            return HelpStatement()
        elif self.current_token.type == TokenType.CLEAR:
            self.eat(TokenType.CLEAR)
            return ClearStatement()
        elif self.current_token.type == TokenType.TYPE:
            self.eat(TokenType.TYPE)
            value = None
            if self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                if self.current_token.type != TokenType.RPAREN:
                    value = self.comparison()
                self.eat(TokenType.RPAREN)
            elif self.current_token.type != TokenType.EOF:
                value = self.comparison()
            return TypeStatement(value)
        elif self.current_token.type == TokenType.EXIT:
            self.eat(TokenType.EXIT)
            return ExitStatement()
        elif self.current_token.type == TokenType.ID and self.peek_token().type == TokenType.ASSIGN:
            id_token = self.current_token
            self.eat(TokenType.ID)
            self.eat(TokenType.ASSIGN)
            value = self.comparison()
            return VarAssign(id_token.value, value)
        return self.comparison()

    def term(self):
        """term : factor ((MUL | DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            self.eat(token.type)
            node = BinOP(left=node,op = token, right=self.factor())
        return node

    def expr(self):
        """expr : term ((PLUS | MINUS) term)*"""
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOP(left=node,op = token, right=self.term())
        return node

    def comparison(self):
        """comparison : expr ((EQUALS | NOT_EQ) expr)*"""
        node = self.expr()

        while self.current_token.type in (TokenType.EQUALS, TokenType.NOT_EQ):
            token = self.current_token
            self.eat(token.type)
            node = BinOP(left=node, op=token, right=self.expr())
        return node

    def parse(self):
        """Parse the input"""
        node = self.statement()
        if self.current_token.type != TokenType.EOF:
            raise Exception(f"Invalid syntax: Unexpected token {self.current_token.type}")
        return node


if __name__ == "__main__":
    from lexer import Lexer

    code = "(10 + 5) * 2"
    lexer = Lexer(code)
    parser = Parser(lexer)

    tree = parser.parse()
    print(f"Resulting AST: {tree}")
