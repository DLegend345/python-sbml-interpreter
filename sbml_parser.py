# CSE307
# Deron Ghimire

import sys
import ply.lex as lex
import ply.yacc as yacc
from sbml_ast import *

reserved = {
    "True": "BOOL_T",
    "False": "BOOL_F",
    "div": "DIV",
    "mod": "MOD",
    "andalso": "ANDALSO",
    "orelse": "ORELSE",
    "not": "NOT",
    "print": "PRINT",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "fun": "FUN",
}

tokens = (
    "NUMBER", "STRING", "ID",
    "PLUS", "MINUS", "TIMES", "DIVIDE", "POW",
    "LT", "LE", "EQ", "NE", "GE", "GT",
    "LPAREN", "RPAREN",
    "LBRACKET", "RBRACKET",
    "COMMA",
    "LBRACE", "RBRACE",
    "SEMI", "ASSIGN",
) + tuple(reserved.values())

t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_POW = r"\^"
t_LE = r"<="
t_LT = r"<"
t_GE = r">="
t_GT = r">"
t_EQ = r"=="
t_NE = r"!="
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_COMMA = r","
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_SEMI = r";"
t_ASSIGN = r"="


def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'(\"([^\\\n]|(\\.))*?\")|(\'([^\\\n]|(\\.))*?\')'
    value = t.value
    t.value = (
        value[1:-1]
        .replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace('\\"', '"')
        .replace("\\'", "'")
        .replace("\\\\", "\\")
    )
    return t


def t_ID(t):
    r"[A-Za-z][A-Za-z0-9_]*"
    if t.value in reserved:
        t.type = reserved[t.value]
    return t


t_ignore = " \t\r"


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("SYNTAX ERROR")
    sys.exit(0)


lexer = lex.lex()

precedence = (
    ("right", "NOT"),
    ("right", "UMINUS"),
    ("right", "POW"),
    ("left", "TIMES", "DIVIDE", "DIV", "MOD"),
    ("left", "PLUS", "MINUS"),
    ("nonassoc", "LT", "LE", "EQ", "NE", "GE", "GT"),
    ("left", "ANDALSO"),
    ("left", "ORELSE"),
)


def p_program(p):
    "program : function_def_list main_block"
    p[0] = ProgramNode(p[1], p[2][0], p[2][1])


def p_function_def_list_many(p):
    "function_def_list : function_def_list function_def"
    p[1].append(p[2])
    p[0] = p[1]


def p_function_def_list_empty(p):
    "function_def_list :"
    p[0] = []


def p_function_def(p):
    "function_def : FUN ID LPAREN opt_param_list RPAREN ASSIGN LBRACE stmt_list RBRACE expression SEMI"
    p[0] = FunctionDefNode(p[2], p[4], BlockNode(p[8]), p[10])


def p_opt_param_list_empty(p):
    "opt_param_list :"
    p[0] = []


def p_opt_param_list_some(p):
    "opt_param_list : param_list"
    p[0] = p[1]


def p_param_list_one(p):
    "param_list : ID"
    p[0] = [p[1]]


def p_param_list_many(p):
    "param_list : param_list COMMA ID"
    p[1].append(p[3])
    p[0] = p[1]


def p_main_block(p):
    "main_block : LBRACE stmt_list RBRACE expression SEMI"
    p[0] = (BlockNode(p[2]), p[4])


def p_block(p):
    "block : LBRACE stmt_list RBRACE"
    p[0] = BlockNode(p[2])


def p_stmt_list_many(p):
    "stmt_list : stmt_list statement"
    p[1].append(p[2])
    p[0] = p[1]


def p_stmt_list_empty(p):
    "stmt_list :"
    p[0] = []


def p_statement_assign(p):
    "statement : expression ASSIGN expression SEMI"
    p[0] = AssignNode(p[1], p[3])


def p_statement_print(p):
    "statement : PRINT LPAREN expression RPAREN SEMI"
    p[0] = PrintNode(p[3])


def p_statement_if(p):
    "statement : IF LPAREN expression RPAREN block"
    p[0] = IfNode(p[3], p[5], None)


def p_statement_if_else(p):
    "statement : IF LPAREN expression RPAREN block ELSE block"
    p[0] = IfNode(p[3], p[5], p[7])


def p_statement_while(p):
    "statement : WHILE LPAREN expression RPAREN block"
    p[0] = WhileNode(p[3], p[5])


def p_statement_block(p):
    "statement : block"
    p[0] = p[1]


def p_expression_paren(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = NumberNode(p[1])


def p_expression_string(p):
    "expression : STRING"
    p[0] = StringNode(p[1])


def p_expression_true(p):
    "expression : BOOL_T"
    p[0] = BooleanNode(True)


def p_expression_false(p):
    "expression : BOOL_F"
    p[0] = BooleanNode(False)


def p_expression_list(p):
    "expression : LBRACKET elements_opt RBRACKET"
    p[0] = ListNode(p[2])


def p_elements_opt_some(p):
    "elements_opt : elements"
    p[0] = p[1]


def p_elements_opt_empty(p):
    "elements_opt :"
    p[0] = []


def p_elements_many(p):
    "elements : elements COMMA expression"
    p[1].append(p[3])
    p[0] = p[1]


def p_elements_one(p):
    "elements : expression"
    p[0] = [p[1]]


def p_expression_call(p):
    "expression : ID LPAREN opt_arg_list RPAREN"
    p[0] = FunctionCallNode(p[1], p[3])


def p_opt_arg_list_empty(p):
    "opt_arg_list :"
    p[0] = []


def p_opt_arg_list_some(p):
    "opt_arg_list : arg_list"
    p[0] = p[1]


def p_arg_list_one(p):
    "arg_list : expression"
    p[0] = [p[1]]


def p_arg_list_many(p):
    "arg_list : arg_list COMMA expression"
    p[1].append(p[3])
    p[0] = p[1]


def p_expression_id(p):
    "expression : ID"
    p[0] = VarNode(p[1])


def p_expression_index(p):
    "expression : expression LBRACKET expression RBRACKET"
    p[0] = IndexNode(p[1], p[3])


def p_expression_not(p):
    "expression : NOT expression"
    p[0] = UnaryNode("not", p[2])


def p_expression_negate(p):
    "expression : MINUS expression %prec UMINUS"
    p[0] = UnaryNode("neg", p[2])


def p_expression_math(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression POW expression"""
    p[0] = BinaryNode(p[2], p[1], p[3])


def p_expression_divmod_kw(p):
    """expression : expression DIV expression
                  | expression MOD expression"""
    op = "div" if p.slice[2].type == "DIV" else "mod"
    p[0] = BinaryNode(op, p[1], p[3])


def p_expression_cmp(p):
    """expression : expression LT expression
                  | expression LE expression
                  | expression EQ expression
                  | expression NE expression
                  | expression GE expression
                  | expression GT expression"""
    p[0] = BinaryNode(p[2], p[1], p[3])


def p_expression_bool(p):
    """expression : expression ANDALSO expression
                  | expression ORELSE expression"""
    op = "andalso" if p.slice[2].type == "ANDALSO" else "orelse"
    p[0] = BinaryNode(op, p[1], p[3])


def p_error(p):
    print("SYNTAX ERROR")
    sys.exit(0)


parser = yacc.yacc(start="program")
