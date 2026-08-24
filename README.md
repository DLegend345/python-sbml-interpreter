# python-sbml-interpreter
A complete programming language interpreter and AST evaluator for SBML built with Python and PLY (Lex/Yacc). Supports LALR(1) parsing, variable scoping, recursive function call stacks, and dynamic type evaluation.  

# SBML Interpreter & AST Evaluator

A fully functional interpreter and Abstract Syntax Tree (AST) evaluator for **SBML** (SBU Modeling Language), built using **Python 3** and **PLY (Python Lex & Yacc)**.

This project implements a complete language execution environment featuring lexing, bottom-up LALR(1) parsing, AST construction, dynamic symbol-table stack management, lexical scoping, function definitions, and recursive evaluation.

---

## Key Features

- **Lexical Analysis & Parsing (`PLY`):** Tokenization and context-free grammar parsing for custom language expressions, control structures, and function definitions.
- **Abstract Syntax Tree (AST) Engine:** Object-oriented AST nodes representing values, binary/unary operators, statements, blocks, and call structures.
- **Scoped Call-Stack Management:** Environment stack implementation handling local frame bindings, parameter passing, and recursive stack frame destruction upon function termination.
- **Control Flow & Imperative Statements:** Support for conditional branching (`if`, `if-else`), conditional loops (`while`), block statements, and print output commands.
- **Dynamic Type & Expression Evaluation:** Evaluates primitive types (Integers, Reals, Booleans, Strings), complex data structures (Lists, Tuples), membership operators, indexing, and overloaded standard arithmetic/logical operators.

---

## SBML Syntax & Feature Overview

### Data Types & Literals
- **Integers & Reals:** Base-10 whole numbers (`42`), floating-point values (`3.14159`), and scientific notation (`6.02e-23`).
- **Strings:** Double-quoted or single-quoted character sequences (`"Hello World"`).
- **Booleans:** `True` and `False`.
- **Lists & Tuples:** Dynamic heterogeneous lists (`[1, "two", [3]]`) and fixed tuples (`("a", 10)`).

### Language Constructs & Functions
- **Function Definition:** Declared using `fun name(param1, param2) = { ... block ... } expression;`
- **Scoping & Call-by-Value:** Parameters and local variables created during function invocation are isolated to that frame and pop off upon expression return.
- **Statements:** Block structures enclosed in `{ ... }`, variable assignment (`x = 10;`), indexing mutation (`arr[0] = 5;`), conditional execution (`if (cond) { ... } else { ... }`), and looping (`while (cond) { ... }`).

---

## Project Structure

```text
.
├── sbml_ast.py      # Class definitions for AST nodes and evaluate() logic
├── sbml_parser.py   # PLY grammar rules, token definitions, and AST action routines
├── sbml_main.py     # Command-line driver for printing AST or evaluating scripts
└── README.md        # Project documentation
```

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/sbml-interpreter.git
   cd sbml-interpreter
   ```

2. **Install Dependencies:**
   This interpreter requires Python 3 and PLY (Python Lex-Yacc).
   ```bash
   pip install ply
   ```

---

## Usage

The interpreter driver `sbml_main.py` supports two primary execution modes: **Print AST Mode (`-P`)** and **Evaluation Mode (`-E`)**.

### 1. Execute & Evaluate SBML Scripts (`-E`)
To run and execute an SBML program:
```bash
python3 sbml_main.py -E program.sbml
```

### 2. Print Abstract Syntax Tree (`-P`)
To inspect the constructed AST nodes before evaluation:
```bash
python3 sbml_main.py -P program.sbml
```

---

## Example SBML Code

### Recursive Factorial (`factorial.sbml`)
```sbml
fun factorial(n) = 
{
    if (n < 1) {
        output = 1;
    } else {
        output = n * factorial(n - 1);
    }
}
output;

{
    print(factorial(5));
}
```

**Output:**
```bash
$ python3 sbml_main.py -E factorial.sbml
120
```

### Greatest Common Divisor (`gcd.sbml`)
```sbml
fun gcd(a, b) = 
{
    t = b;
    b = a mod b;
    if (b == 0) {
        output = t;
    } else {
        output = gcd(t, b);
    }
}
output;

{
    print(gcd(32, 18));
}
```

**Output:**
```bash
$ python3 sbml_main.py -E gcd.sbml
2
```

---

## Error Handling

- **`SYNTAX ERROR`**: Issued when the input program fails parsing rules defined in `sbml_parser.py`.
- **`SEMANTIC ERROR`**: Issued during runtime evaluation (e.g., undeclared variable access, index out of bounds, type mismatches, or invalid function argument counts).
