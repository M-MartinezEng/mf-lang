from enum import Enum

class TokenType(Enum):
    # make sure to start with defining new TokenType when creating a new statement
    NUMBER = "NUMBER"
    FLOAT = "FLOAT"
    BOOL = "BOOL"
    NULL = "NULL"
    STRING = "STRING"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    LT = "LT"
    GT = "GT"
    LTE = "LTE"
    GTE = "GTE"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    SEMICOLON = "SEMICOLON"
    EOF = "EOF" # end of file, tells the parser to stop
    ID = "ID"
    ASSIGN = "ASSIGN" # =
    EQUALS= "EQUALS"  # ==
    NOT_EQ = "NOT_EQ" # !=
    AND = "AND"
    OR = "OR"
    PRINT = "PRINT"
    HELP = "HELP"
    CLEAR = "CLEAR"
    TYPE = "TYPE"
    EXIT = "EXIT"
    PING = "PING"
    LATENCY = "LATENCY"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    RESOLVE = "RESOLVE"
    FOR = "FOR"
    DO = "DO"
    NOT = "NOT"
    SLEEP = "SLEEP"
    SLEEP_MS = "SLEEP_MS"

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0 # current position in the text
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        """Move to the next character in the text."""
        self.pos += 1
        if self.pos <len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def peek(self):
        """Look ahead at the next character in the text."""
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        """Consumes characters until the end of the line."""
        # skip the first '/' and the second '/'
        self.advance()
        self.advance()

        # keep advancing until we hit a new line or the end of the file
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        if self.current_char == '\n':
            self.advance()

    def get_number(self):
        """Get a multi-digit number from the text."""
        result = ""
        decimal_count = 0
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                decimal_count += 1
                if decimal_count > 1: break
            result += self.current_char
            self.advance()

        if decimal_count > 0:
            return Token(TokenType.FLOAT, float(result))
        return Token(TokenType.NUMBER, int(result))

    def get_string(self):
        """Consumes characters until the closing quote."""
        result = ""
        self.advance() # skip the opening "
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()
        if self.current_char == '"':
            self.advance() # skip the closing "
            return Token(TokenType.STRING, result)
        else:
            raise Exception("Unterminated string literal")

    def get_next_token(self):
        """Core of the lexer: finds the next token"""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.get_number()

            if self.current_char == '"':
                return self.get_string()

            if self.current_char.isalpha():
                return self.get_identifier()

            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance() # consume the first '='
                    self.advance() # consume the second '='
                    return Token(TokenType.EQUALS, '==')
                self.advance()
                return Token(TokenType.ASSIGN, '=')

            if self.current_char == '!':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.NOT_EQ, '!=')
                raise Exception("Expected '=' after '!'")

            if self.current_char == '<':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.LTE, '<=')
                self.advance()
                return Token(TokenType.LT, '<')

            if self.current_char == '>':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.GTE, '>=')
                self.advance()
                return Token(TokenType.GT, '>')

            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS)

            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS)

            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MULTIPLY)

            if self.current_char == '/':
                # peek to see if the NEXT character is a '/'
                if self.peek() == '/':
                    # skip the comment
                    self.skip_comment()
                    continue # after skipping, look for the next valid token
                self.advance()
                return Token(TokenType.DIVIDE)

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN)

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN)

            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE)

            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE)

            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON)

            # Raise an error if we find a character we don't recognize
            raise Exception(f"Invalid character: {self.current_char}")
        return Token(TokenType.EOF)

    def get_identifier(self):
        """Handles variables and keywords"""
        result = ""
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        # check if the word is a reserved keyword, this is where commands like "if", "else", or "while, can be added
        keywords = {
            "print": TokenType.PRINT,
            "help" : TokenType.HELP,
            "clear": TokenType.CLEAR,
            "type": TokenType.TYPE,
            "exit":  TokenType.EXIT,
            "ping": TokenType.PING,
            "latency": TokenType.LATENCY,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "while": TokenType.WHILE,
            "break": TokenType.BREAK,
            "continue": TokenType.CONTINUE,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "resolve": TokenType.RESOLVE,
            "for": TokenType.FOR,
            "do": TokenType.DO,
            "not": TokenType.NOT,
            "sleep": TokenType.SLEEP,
            "sleep_ms": TokenType.SLEEP_MS,
        }

        # if it's in the keyword dictionary, return that type; otherwise it's an ID
        token_type = keywords.get(result.lower(), TokenType.ID)
        lowered = result.lower()
        if lowered == "true":
            return Token(TokenType.BOOL, True)
        if lowered == "false":
            return Token(TokenType.BOOL, False)
        if lowered == "null":
            return Token(TokenType.NULL, None)
        return Token(token_type, result)



if __name__ == "__main__":
    text = """
    let x = 10 // This is a comment
    print x    // This is another comment
    """
    lexer = Lexer(text)

    token = lexer.get_next_token()
    while token.type != TokenType.EOF:
        print(token)
        token = lexer.get_next_token()
