import os
import platform
import re
import socket
import subprocess
import time
from typing import Any, Callable, cast

from lexer import TokenType


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class Interpreter:

    def __init__(self):
        self.variables: dict[str, Any] = {}  # The Symbol Table / Memory
        self.loop_depth = 0

    @staticmethod
    def _to_snake(name: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def visit(self, node: Any) -> Any:
        """Dynamic dispatcher: looks for a method based on the node type."""
        method_name = f"visit_{self._to_snake(type(node).__name__)}"
        visitor = cast(Callable[[Any], Any], getattr(self, method_name, self.generic_visit))
        try:
            return visitor(node)
        except (BreakSignal, ContinueSignal):
            if self.loop_depth == 0:
                raise RuntimeError("break/continue can only be used inside loops")
            raise

    def generic_visit(self, node: Any) -> Any:
        raise NotImplementedError(f'No visit_{type(node).__name__} method defined')

    @staticmethod
    def visit_number(node: Any) -> Any:
        return node.value

    @staticmethod
    def visit_float_node(node: Any) -> Any:
        return node.value

    @staticmethod
    def visit_bool_node(node: Any) -> Any:
        return node.value

    @staticmethod
    def visit_null_node(node: Any) -> Any:
        return node.value

    @staticmethod
    def visit_string_node(node: Any) -> Any:
        return node.value

    def visit_unary_op(self, node: Any) -> Any:
        if node.op.type == TokenType.NOT:
            return not bool(self.visit(node.node))
        if node.op.type == TokenType.MINUS:
            return -self.visit(node.node)
        raise ValueError(f"Unsupported unary operator: {node.op.type}")

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
        if node.op.type == TokenType.LT:
            return self.visit(node.left) < self.visit(node.right)
        if node.op.type == TokenType.GT:
            return self.visit(node.left) > self.visit(node.right)
        if node.op.type == TokenType.LTE:
            return self.visit(node.left) <= self.visit(node.right)
        if node.op.type == TokenType.GTE:
            return self.visit(node.left) >= self.visit(node.right)
        if node.op.type == TokenType.AND:
            left_value = self.visit(node.left)
            if not bool(left_value):
                return False
            return bool(self.visit(node.right))
        if node.op.type == TokenType.OR:
            left_value = self.visit(node.left)
            if bool(left_value):
                return True
            return bool(self.visit(node.right))
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

    def visit_sleep_statement(self, node: Any) -> float:
        duration = self.visit(node.duration_node)
        if not isinstance(duration, (int, float)):
            raise RuntimeError("sleep expects a numeric duration in seconds")
        if duration < 0:
            raise RuntimeError("sleep duration cannot be negative")
        time.sleep(float(duration))
        return float(duration)

    def visit_sleep_ms_statement(self, node: Any) -> float:
        duration_ms = self.visit(node.duration_ms_node)
        if not isinstance(duration_ms, (int, float)):
            raise RuntimeError("sleep_ms expects a numeric duration in milliseconds")
        if duration_ms < 0:
            raise RuntimeError("sleep_ms duration cannot be negative")
        duration_seconds = float(duration_ms) / 1000.0
        time.sleep(duration_seconds)
        return float(duration_ms)

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

    def visit_resolve_statement(self, node):
        hostname = self.visit(node.hostname_node)
        try:
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except socket.gaierror:
            return f"Error: Could not resolve {hostname}"
        except Exception as e: return f"Error: {e}"

    def visit_expression_statement(self, node: Any) -> Any:
        return self.visit(node.expr_node)

    def visit_block(self, node: Any) -> Any:
        last_value = None
        for statement in node.statements:
            last_value = self.visit(statement)
        return last_value

    def visit_if_statement(self, node: Any) -> Any:
        if self.visit(node.condition_node):
            return self.visit(node.then_node)
        if node.else_node is not None:
            return self.visit(node.else_node)
        return None

    def visit_while_statement(self, node: Any) -> Any:
        last_value = None
        self.loop_depth += 1
        try:
            while self.visit(node.condition_node):
                try:
                    last_value = self.visit(node.body_node)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
        finally:
            self.loop_depth -= 1
        return last_value

    def visit_for_statement(self, node: Any) -> Any:
        if node.init_node is not None:
            self.visit(node.init_node)

        last_value = None
        self.loop_depth += 1
        try:
            while True:
                if node.condition_node is not None and not self.visit(node.condition_node):
                    break
                try:
                    last_value = self.visit(node.body_node)
                except ContinueSignal:
                    if node.update_node is not None:
                        self.visit(node.update_node)
                    continue
                except BreakSignal:
                    break

                if node.update_node is not None:
                    self.visit(node.update_node)
        finally:
            self.loop_depth -= 1
        return last_value

    def visit_do_while_statement(self, node: Any) -> Any:
        last_value = None
        self.loop_depth += 1
        try:
            while True:
                try:
                    last_value = self.visit(node.body_node)
                except ContinueSignal:
                    pass
                except BreakSignal:
                    break

                if not self.visit(node.condition_node):
                    break
        finally:
            self.loop_depth -= 1
        return last_value

    @staticmethod
    def visit_break_statement(node: Any) -> None:
        _ = node
        raise BreakSignal

    @staticmethod
    def visit_continue_statement(node: Any) -> None:
        _ = node
        raise ContinueSignal

    @staticmethod
    def visit_help_statement(node: Any) -> int:
        _ = node
        print("Available commands: print, ping, sleep, sleep_ms, resolve, latency, if/else, while, for, do-while, break, continue, help, clear, type, exit")
        print("Sleep syntax: sleep <seconds_expr>")
        print("Sleep-ms syntax: sleep_ms <milliseconds_expr>")
        print("Latency syntax: latency <target_expr> = <variable_name> OR <variable_name> = latency <target_expr>")
        print("Resolve syntax: resolve <hostname_expr>")
        print("Block syntax: { stmt1; stmt2; ... }")
        print("If syntax: if <condition> <statement-or-block> [else <statement-or-block>]")
        print("While syntax: while <condition> <statement-or-block>")
        print("For syntax: for (<init>; <condition>; <update>) <statement-or-block>")
        print("Do-while syntax: do <statement-or-block> while <condition>")
        print("Loop control: break; continue;")
        print("Logical operators: and, or, not")
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
        type_name = "null" if value is None else type(value).__name__
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
