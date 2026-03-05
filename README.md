# mf-lang

**mf-lang** is a custom, interpreted programming language build from scratch in Python. Icatered it towards **Network Engineering and Telemetry**, allowing users to perform low-latency testing, IP monitoring, and basic logic through a simplified syntax.
---

## Quick Start
To start the interactive shell (REPL), check to have Python 3.14 installed and run:
```bash python shell.py ```
---

## Key Features
- Network Native: Build-in commands like `ping` and `latency` for real-time network diagnostics.
- Dynamic Typing: Supports Integers, Floats, Strings, Bool, and Null. Includes operators, parentheses, equals/notEquals, Break, Continue
- Statements: If-loops, If-else-loops, While-loops, block formats for loops. Related operators apply.
- Variable Memory: Persistent symbol table to store and manipulate data across commands
- Recursive Parsing: Handles nested mathematical expressions using PEMDAS/BOMDAS rules
---

## Language Syntax
Below are some examples of what can be done in `mf-lang`:

### Variables & math
```
x = 10
y = 5.5
print (x + y) * 2
```
Gives an output of `31.0`

### Network Monitoring
```
target = "8.8.8.8"
ms = latency target
print ms
```
Gives an output of `ms = 39.629 ms`

### Comments
```
// This is a single-line comment
ping "google.com"
```
Gives an output of `--- mf-lang: Pinging google.com ---

Pinging google.com [2607:f8b0:4005:80f::200e] with 32 bytes of data:
Reply from 2607:f8b0:4005:80f::200e: time=62ms 

Ping statistics for 2607:f8b0:4005:80f::200e:
    Packets: Sent = 1, Received = 1, Lost = 0 (0% loss),
Approximate round-trip times in milliseconds:
    Minimum = 62ms, Maximum = 62ms, Average = 62ms`
---

## Architecture
For this project, I decided to follow a standard compiler pipeline, which I am documenting as part of my CS studies.
1. Lexer (Tokenizer): Converts raw text into a stream of tokens (IDs, Numbers, Operators). Handles lookahead logic for multi-character symbols, like `==`.
2. Parser: A Recursive Descent Parser that transforms tokens into an Abstract Syntax Tree (AST).
3. Interpreter: Uses the Visitor Pattern to walk the AST and execute logic or interface with the Operating System (via `subprocess`).
---

## About the Project
I am currently developing this language while interning at McKay Brothers, so I could better understand the intersection of software development and network infrastructure. My goal is to better understand the gap between high-level programming and low-level system diagnostics.
