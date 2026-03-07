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
        TokenType.EQUALS: "==",
        TokenType.NOT_EQ: "!=",
        TokenType.LT: "<",
        TokenType.GT: ">",
        TokenType.LTE: "<=",
        TokenType.GTE: ">=",
        TokenType.AND: "and",
        TokenType.OR: "or",
    }

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        op_symbol = self.OP_SYMBOLS.get(self.op.type, str(self.op))
        return f"({self.left} {op_symbol} {self.right})"


class Number(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return str(self.value)


class FloatNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return str(self.value)


class BoolNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return str(self.value)


class NullNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return "null"


class StringNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f'"{self.value}"'


class VarAssign(ASTNode):
    def __init__(self, name, value_node):
        self.name = name
        self.value_node = value_node


class VarAccess(ASTNode):
    def __init__(self, token):
        self.token = token
        self.name = token.value


class PrintStatement(ASTNode):
    def __init__(self, value_node):
        self.value_node = value_node


class PingStatement(ASTNode):
    def __init__(self, target_node):
        self.target_node = target_node


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


class ExpressionStatement(ASTNode):
    def __init__(self, expr_node):
        self.expr_node = expr_node


class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements


class IfStatement(ASTNode):
    def __init__(self, condition_node, then_node, else_node=None):
        self.condition_node = condition_node
        self.then_node = then_node
        self.else_node = else_node


class WhileStatement(ASTNode):
    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node

class BreakStatement(ASTNode):
    pass

class ContinueStatement(ASTNode):
    pass

class ResolveStatement(ASTNode):
    def __init__(self, hostname_node):
        self.hostname_node = hostname_node


class UnaryOp(ASTNode):
    def __init__(self, op, node):
        self.op = op
        self.node = node


class ForStatement(ASTNode):
    def __init__(self, init_node, condition_node, update_node, body_node):
        self.init_node = init_node
        self.condition_node = condition_node
        self.update_node = update_node
        self.body_node = body_node


class DoWhileStatement(ASTNode):
    def __init__(self, body_node, condition_node):
        self.body_node = body_node
        self.condition_node = condition_node


class SleepStatement(ASTNode):
    def __init__(self, duration_node):
        self.duration_node = duration_node


class SleepMsStatement(ASTNode):
    def __init__(self, duration_ms_node):
        self.duration_ms_node = duration_ms_node


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f"Invalid syntax: Expected {token_type}, got {self.current_token.type}")

    def peek_token(self):
        saved_pos = self.lexer.pos
        saved_char = self.lexer.current_char
        token = self.lexer.get_next_token()
        self.lexer.pos = saved_pos
        self.lexer.current_char = saved_char
        return token

    def factor(self):
        token = self.current_token
        if token.type == TokenType.NOT:
            self.eat(TokenType.NOT)
            return UnaryOp(token, self.factor())
        if token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOp(token, self.factor())
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return Number(token)
        if token.type == TokenType.FLOAT:
            self.eat(TokenType.FLOAT)
            return FloatNode(token)
        if token.type == TokenType.BOOL:
            self.eat(TokenType.BOOL)
            return BoolNode(token)
        if token.type == TokenType.NULL:
            self.eat(TokenType.NULL)
            return NullNode(token)
        if token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return StringNode(token)
        if token.type == TokenType.RESOLVE:
            self.eat(TokenType.RESOLVE)
            hostname = self.factor()
            return ResolveStatement(hostname)
        if token.type == TokenType.ID:
            self.eat(TokenType.ID)
            return VarAccess(token)
        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.logical()
            self.eat(TokenType.RPAREN)
            return node
        raise Exception(f"Invalid syntax: Unexpected token {token.type}")

    def term(self):
        node = self.factor()
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            self.eat(token.type)
            node = BinOP(left=node, op=token, right=self.factor())
        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOP(left=node, op=token, right=self.term())
        return node

    def comparison(self):
        node = self.expr()
        while self.current_token.type in (
            TokenType.EQUALS,
            TokenType.NOT_EQ,
            TokenType.LT,
            TokenType.GT,
            TokenType.LTE,
            TokenType.GTE,
        ):
            token = self.current_token
            self.eat(token.type)
            node = BinOP(left=node, op=token, right=self.expr())
        return node

    def logical(self):
        node = self.comparison()
        while self.current_token.type in (TokenType.AND, TokenType.OR):
            token = self.current_token
            self.eat(token.type)
            node = BinOP(left=node, op=token, right=self.comparison())
        return node

    def parse_block(self):
        self.eat(TokenType.LBRACE)
        statements = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise Exception("Invalid syntax: Unclosed block")
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
                continue

            statements.append(self.statement())
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
            elif self.current_token.type != TokenType.RBRACE:
                raise Exception("Invalid syntax: Expected ';' or '}' in block")

        self.eat(TokenType.RBRACE)
        return Block(statements)

    def parse_block_or_statement(self):
        if self.current_token.type == TokenType.LBRACE:
            return self.parse_block()
        return self.statement()

    def parse_assignment_or_expression(self):
        if self.current_token.type == TokenType.ID and self.peek_token().type == TokenType.ASSIGN:
            id_token = self.current_token
            self.eat(TokenType.ID)
            self.eat(TokenType.ASSIGN)
            if self.current_token.type == TokenType.LATENCY:
                self.eat(TokenType.LATENCY)
                target = self.logical()
                return LatencyStatement(target, id_token.value)
            value = self.logical()
            return VarAssign(id_token.value, value)
        return ExpressionStatement(self.logical())

    def statement(self):
        if self.current_token.type == TokenType.IF:
            self.eat(TokenType.IF)
            condition = self.logical()
            then_node = self.parse_block_or_statement()
            else_node = None
            if self.current_token.type == TokenType.ELSE:
                self.eat(TokenType.ELSE)
                else_node = self.parse_block_or_statement()
            return IfStatement(condition, then_node, else_node)

        if self.current_token.type == TokenType.WHILE:
            self.eat(TokenType.WHILE)
            condition = self.logical()
            body = self.parse_block_or_statement()
            return WhileStatement(condition, body)

        if self.current_token.type == TokenType.FOR:
            self.eat(TokenType.FOR)
            self.eat(TokenType.LPAREN)

            init_node = None
            if self.current_token.type != TokenType.SEMICOLON:
                init_node = self.parse_assignment_or_expression()
            self.eat(TokenType.SEMICOLON)

            condition_node = None
            if self.current_token.type != TokenType.SEMICOLON:
                condition_node = self.logical()
            self.eat(TokenType.SEMICOLON)

            update_node = None
            if self.current_token.type != TokenType.RPAREN:
                update_node = self.parse_assignment_or_expression()
            self.eat(TokenType.RPAREN)

            body_node = self.parse_block_or_statement()
            return ForStatement(init_node, condition_node, update_node, body_node)

        if self.current_token.type == TokenType.DO:
            self.eat(TokenType.DO)
            body_node = self.parse_block_or_statement()
            self.eat(TokenType.WHILE)
            condition_node = self.logical()
            return DoWhileStatement(body_node, condition_node)

        if self.current_token.type == TokenType.BREAK:
            self.eat(TokenType.BREAK)
            return BreakStatement()

        if self.current_token.type == TokenType.CONTINUE:
            self.eat(TokenType.CONTINUE)
            return ContinueStatement()

        if self.current_token.type == TokenType.PRINT:
            self.eat(TokenType.PRINT)
            return PrintStatement(self.logical())

        if self.current_token.type == TokenType.PING:
            self.eat(TokenType.PING)
            return PingStatement(self.logical())

        if self.current_token.type == TokenType.SLEEP:
            self.eat(TokenType.SLEEP)
            return SleepStatement(self.logical())

        if self.current_token.type == TokenType.SLEEP_MS:
            self.eat(TokenType.SLEEP_MS)
            return SleepMsStatement(self.logical())

        if self.current_token.type == TokenType.LATENCY:
            self.eat(TokenType.LATENCY)
            target = self.logical()
            self.eat(TokenType.ASSIGN)
            var_token = self.current_token
            self.eat(TokenType.ID)
            return LatencyStatement(target, var_token.value)

        if self.current_token.type == TokenType.HELP:
            self.eat(TokenType.HELP)
            return HelpStatement()

        if self.current_token.type == TokenType.CLEAR:
            self.eat(TokenType.CLEAR)
            return ClearStatement()

        if self.current_token.type == TokenType.TYPE:
            self.eat(TokenType.TYPE)
            value = None
            if self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                if self.current_token.type != TokenType.RPAREN:
                    value = self.logical()
                self.eat(TokenType.RPAREN)
            elif self.current_token.type != TokenType.EOF:
                value = self.logical()
            return TypeStatement(value)

        if self.current_token.type == TokenType.EXIT:
            self.eat(TokenType.EXIT)
            return ExitStatement()

        if self.current_token.type == TokenType.LBRACE:
            return self.parse_block()

        return self.parse_assignment_or_expression()

    def parse_program(self):
        statements = []
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
                continue

            statements.append(self.statement())
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
            elif self.current_token.type != TokenType.EOF:
                raise Exception("Invalid syntax: Expected ';' between statements")

        if len(statements) == 1:
            return statements[0]
        return Block(statements)

    def parse(self):
        return self.parse_program()


if __name__ == "__main__":
    from lexer import Lexer

    code = "if 1 == 1 { print \"ok\"; x = 2 }"
    lexer = Lexer(code)
    parser = Parser(lexer)
    tree = parser.parse()
    print(f"Resulting AST: {tree}")
