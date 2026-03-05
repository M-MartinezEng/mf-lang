import os
import platform
import re
import subprocess
import time
from typing import Any, Callable, cast

from lexer import TokenType


class Interpreter:

    def __init__(self):
        self.variables: dict[str, Any] = {}  # The Symbol Table / Memory

    @staticmethod
    def _to_snake(name: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def visit(self, node: Any) -> Any:
        """Dynamic dispatcher: looks for a method based on the node type."""
        method_name = f"visit_{self._to_snake(type(node).__name__)}"
        visitor = cast(Callable[[Any], Any], getattr(self, method_name, self.generic_visit))
        return visitor(node)

    def generic_visit(self, node: Any) -> Any:
        raise NotImplementedError(f'No visit_{type(node).__name__} method defined')

    @staticmethod
    def visit_number(node: Any) -> Any:
        return node.value

    @staticmethod
    def visit_float_node(node: Any) -> Any:
        return node.value

    @staticmethod
    def visit_string_node(node: Any) -> Any:
        return node.value

    def visit_bin_o_p(self, node: Any) -> Any:
        if node.op.type == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        if node.op.type == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        if node.op.type == TokenType.MULTIPLY:
            return self.visit(node.left) * self.visit(node.right)
        if node.op.type == TokenType.DIVIDE:
            return self.visit(node.left) / self.visit(node.right)
        if node.op.type == TokenType.EQUALS:
            return self.visit(node.left) == self.visit(node.right)
        if node.op.type == TokenType.NOT_EQ:
            return self.visit(node.left) != self.visit(node.right)
        raise ValueError(f"Unsupported binary operator: {node.op.type}")

    def visit_var_assign(self, node: Any) -> Any:
        # Calculate the value and store it in our dictionary
        value = self.visit(node.value_node)
        self.variables[node.name] = value
        return value

    def visit_var_access(self, node: Any) -> Any:
        # Look up the value in the dictionary
        var_name = node.name
        if var_name in self.variables:
            return self.variables[var_name]
        raise NameError(f"Undefined variable: {var_name}")

    def visit_print_statement(self, node: Any) -> Any:
        value = self.visit(node.value_node)
        print(value)
        return value

    def visit_ping_statement(self, node: Any) -> int:
        target = self.visit(node.target_node)
        print(f"--- mf-lang: Pinging {target} ---")

        # determine the ping command based on OS (-n for windows, -c for unix-like systems)
        param = '-n' if platform.system().lower() == "windows" else '-c'
        command = ['ping', param, '1', str(target)]

        # execute the real system ping command
        ping_result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        print(ping_result.stdout if ping_result.stdout else ping_result.stderr)
        return 0

    def visit_latency_statement(self, node: Any) -> float:
        target = self.visit(node.target_node)
        param = '-n' if platform.system().lower() == "windows" else '-c'
        command = ['ping', param, '1', str(target)]

        started = time.perf_counter()
        ping_result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000.0

        if ping_result.returncode != 0:
            message = ping_result.stderr.strip() or ping_result.stdout.strip() or "Ping failed"
            raise RuntimeError(message)

        self.variables[node.variable_name] = elapsed_ms
        print(f"{node.variable_name} = {elapsed_ms:.3f} ms")
        return elapsed_ms

    @staticmethod
    def visit_help_statement(node: Any) -> int:
        _ = node
        print("Available commands: print, ping, latency, help, clear, type, exit")
        print("Latency syntax: latency <target_expr> = <variable_name>")
        return 0

    @staticmethod
    def visit_clear_statement(node: Any) -> int:
        _ = node
        os.system("cls" if platform.system().lower() == "windows" else "clear")
        return 0

    @staticmethod
    def visit_exit_statement(node: Any) -> None:
        _ = node
        raise SystemExit

    def visit_type_statement(self, node: Any) -> Any:
        if node.value_node is None:
            print("Usage: type <expr> or type(<expr>)")
            return None

        value = self.visit(node.value_node)
        type_name = type(value).__name__
        print(type_name)
        return type_name

if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser

    code = "(10 + 5) * 2"
    lexer = Lexer(code)
    parser = Parser(lexer)
    tree = parser.parse()

    interpreter = Interpreter()
    demo_result = interpreter.visit(tree)

    print(f"Code: {code}")
    print(f"Result: {demo_result}")
