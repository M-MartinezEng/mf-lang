Description:
'mf-lang' is a domain-specific interpreted language, that was designed to be used in automating latency testing and IP monitoring. This page outlines the project, its use, and development.

Installation:
- Needs Python 3.14
- Run the associated shell with `python shell.py`

Current Language Features:
- Data Types: Int, Float, String, Bool, Null
- Operators: Plus, Minus, Multiply, Divide, LParentheses, RParentheses, Equals, NotEquals, And/Or, <> comparators, Block
- Statements: If, If/Else, While (incl. Break, Continue)

Current Language Commands:
-help
-print <expr>
-type <expr>
-clear
-<expr>
-exit
-<id> = <expr> (assignment statement)
-<expr> (expression statement)
