# CSE307
# Deron Ghimire

import sys
from sbml_parser import parser
from sbml_ast import SemanticError, print_ast


def main():
    if len(sys.argv) != 3:
        print("SYNTAX ERROR")
        return

    mode = sys.argv[1]
    filename = sys.argv[2]

    try:
        with open(filename, encoding="utf-8") as file:
            program = file.read()
    except (OSError, UnicodeError):
        print("SYNTAX ERROR")
        return

    try:
        ast = parser.parse(program)
    except SystemExit:
        return
    except Exception:
        print("SYNTAX ERROR")
        return

    if ast is None:
        print("SYNTAX ERROR")
        return

    if mode == "-P":
        print_ast(ast)
        return

    if mode == "-E":
        try:
            ast.evaluate()
        except SemanticError:
            print("SEMANTIC ERROR")
        except Exception:
            print("SEMANTIC ERROR")
        return

    print("SYNTAX ERROR")


if __name__ == "__main__":
    main()
