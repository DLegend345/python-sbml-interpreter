# CSE307
# Deron Ghimire

env_stack = []
function_table = {}


class SemanticError(Exception):
    pass


class Node:
    def evaluate(self):
        raise NotImplementedError

    def children(self):
        return []

    def __str__(self):
        return self.__class__.__name__


class NumberNode(Node):
    def __init__(self, x):
        self.x = x

    def evaluate(self):
        return self.x

    def __str__(self):
        return "Number(%s)" % self.x


class StringNode(Node):
    def __init__(self, s):
        self.s = s

    def evaluate(self):
        return self.s

    def __str__(self):
        return "String(%r)" % self.s


class BooleanNode(Node):
    def __init__(self, b):
        self.b = b

    def evaluate(self):
        return self.b

    def __str__(self):
        return "Boolean(%s)" % self.b


class ListNode(Node):
    def __init__(self, items):
        self.items = items

    def evaluate(self):
        return [item.evaluate() for item in self.items]

    def children(self):
        return list(self.items)

    def __str__(self):
        return "List(%d elts)" % len(self.items)


def current_env():
    if not env_stack:
        env_stack.append({})
    return env_stack[-1]


def lookup_variable(name):
    env = current_env()
    if name not in env:
        raise SemanticError("uninitialized variable %s" % name)
    return env[name]


def assign_variable(name, value):
    current_env()[name] = value


class VarNode(Node):
    def __init__(self, name):
        self.name = name

    def evaluate(self):
        return lookup_variable(self.name)

    def __str__(self):
        return "Var(%s)" % self.name


class IndexNode(Node):
    def __init__(self, base, idx):
        self.base = base
        self.idx = idx

    def evaluate(self):
        base = self.base.evaluate()
        index = self.idx.evaluate()

        if not isinstance(index, int):
            raise SemanticError("non-integer index")
        if not isinstance(base, (list, str)):
            raise SemanticError("indexed non-list/non-string")
        if index < 0 or index >= len(base):
            raise SemanticError("index out of bounds")

        return base[index]

    def children(self):
        return [self.base, self.idx]

    def __str__(self):
        return "Index"


class UnaryNode(Node):
    def __init__(self, op, val):
        self.op = op
        self.val = val

    def evaluate(self):
        value = self.val.evaluate()

        if self.op == "not":
            if not isinstance(value, bool):
                raise SemanticError("not on non-bool")
            return not value

        if self.op == "neg":
            if not isinstance(value, int):
                raise SemanticError("neg on non-int")
            return -value

        raise SemanticError("unknown unary op %s" % self.op)

    def children(self):
        return [self.val]

    def __str__(self):
        return "Unary(%s)" % self.op


class BinaryNode(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.l = left
        self.r = right

    def evaluate(self):
        # Short-circuit boolean operators.
        if self.op == "andalso":
            left = self.l.evaluate()
            if not isinstance(left, bool):
                raise SemanticError("andalso on non-bool")
            if not left:
                return False

            right = self.r.evaluate()
            if not isinstance(right, bool):
                raise SemanticError("andalso on non-bool")
            return right

        if self.op == "orelse":
            left = self.l.evaluate()
            if not isinstance(left, bool):
                raise SemanticError("orelse on non-bool")
            if left:
                return True

            right = self.r.evaluate()
            if not isinstance(right, bool):
                raise SemanticError("orelse on non-bool")
            return right

        left = self.l.evaluate()
        right = self.r.evaluate()

        if self.op == "+":
            if isinstance(left, int) and isinstance(right, int):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            if isinstance(left, list) and isinstance(right, list):
                return left + right
            raise SemanticError("type error for +")

        if self.op == "-":
            if isinstance(left, int) and isinstance(right, int):
                return left - right
            raise SemanticError("type error for -")

        if self.op == "*":
            if isinstance(left, int) and isinstance(right, int):
                return left * right
            if isinstance(left, str) and isinstance(right, int):
                return left * right
            if isinstance(left, list) and isinstance(right, int):
                return left * right
            raise SemanticError("type error for *")

        if self.op in ("/", "div"):
            if not (isinstance(left, int) and isinstance(right, int)):
                raise SemanticError("type error for div")
            if right == 0:
                raise SemanticError("divide by zero")
            return left // right

        if self.op == "mod":
            if not (isinstance(left, int) and isinstance(right, int)):
                raise SemanticError("type error for mod")
            if right == 0:
                raise SemanticError("divide by zero")
            return left % right

        if self.op == "^":
            if not (isinstance(left, int) and isinstance(right, int)):
                raise SemanticError("type error for ^")
            return left ** right

        if self.op == "<":
            return left < right
        if self.op == "<=":
            return left <= right
        if self.op == "==":
            return left == right
        if self.op == "!=":
            return left != right
        if self.op == ">=":
            return left >= right
        if self.op == ">":
            return left > right

        raise SemanticError("unknown op %s" % self.op)

    def children(self):
        return [self.l, self.r]

    def __str__(self):
        return "Binary(%s)" % self.op


class BlockNode(Node):
    def __init__(self, stmts):
        self.stmts = stmts

    def evaluate(self):
        for stmt in self.stmts:
            stmt.evaluate()

    def children(self):
        return list(self.stmts)

    def __str__(self):
        return "Block(%d stmts)" % len(self.stmts)


class AssignNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        value = self.right.evaluate()

        if isinstance(self.left, VarNode):
            assign_variable(self.left.name, value)
            return

        if isinstance(self.left, IndexNode):
            base = self.left.base.evaluate()
            index = self.left.idx.evaluate()

            if not isinstance(base, list):
                raise SemanticError("cannot assign through non-list index")
            if not isinstance(index, int):
                raise SemanticError("bad assignment index")
            if index < 0 or index >= len(base):
                raise SemanticError("index out of bounds")

            base[index] = value
            return

        raise SemanticError("invalid assignment")

    def children(self):
        return [self.left, self.right]

    def __str__(self):
        return "Assign"


class PrintNode(Node):
    def __init__(self, expr):
        self.expr = expr

    def evaluate(self):
        print(self.expr.evaluate())

    def children(self):
        return [self.expr]

    def __str__(self):
        return "Print"


class IfNode(Node):
    def __init__(self, cond, tblock, eblock=None):
        self.cond = cond
        self.tblock = tblock
        self.eblock = eblock

    def evaluate(self):
        condition = self.cond.evaluate()
        if not isinstance(condition, bool):
            raise SemanticError("non-boolean condition in if")

        if condition:
            self.tblock.evaluate()
        elif self.eblock is not None:
            self.eblock.evaluate()

    def children(self):
        children = [self.cond, self.tblock]
        if self.eblock is not None:
            children.append(self.eblock)
        return children

    def __str__(self):
        return "If"


class WhileNode(Node):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def evaluate(self):
        while True:
            condition = self.cond.evaluate()
            if not isinstance(condition, bool):
                raise SemanticError("non-boolean condition in while")
            if not condition:
                break
            self.body.evaluate()

    def children(self):
        return [self.cond, self.body]

    def __str__(self):
        return "While"


class FunctionDefNode(Node):
    def __init__(self, name, params, body, ret):
        self.name = name
        self.params = params
        self.body = body
        self.ret = ret

    def evaluate(self):
        function_table[self.name] = self

    def children(self):
        return [self.body, self.ret]

    def __str__(self):
        return "FunctionDef(%s/%d)" % (self.name, len(self.params))


class FunctionCallNode(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def evaluate(self):
        if self.name not in function_table:
            raise SemanticError("undefined function %s" % self.name)

        function = function_table[self.name]

        if len(self.args) != len(function.params):
            raise SemanticError(
                "wrong number of arguments to %s" % self.name
            )

        # Evaluate arguments in the caller's environment first.
        values = [arg.evaluate() for arg in self.args]

        # Each invocation receives a fresh local frame. This provides
        # call-by-value parameters and supports recursive calls.
        frame = {}
        for param, value in zip(function.params, values):
            frame[param] = value

        env_stack.append(frame)
        try:
            function.body.evaluate()
            return function.ret.evaluate()
        finally:
            env_stack.pop()

    def children(self):
        return list(self.args)

    def __str__(self):
        return "Call(%s)" % self.name


class ProgramNode(Node):
    def __init__(self, fdefs, main_block, main_expr):
        self.fdefs = fdefs
        self.main_block = main_block
        self.main_expr = main_expr

    def evaluate(self):
        function_table.clear()

        # Register all functions before executing main so that functions
        # can call one another regardless of definition order.
        for function in self.fdefs:
            if function.name in function_table:
                raise SemanticError(
                    "duplicate function %s" % function.name
                )
            function_table[function.name] = function

        env_stack.clear()
        env_stack.append({})

        self.main_block.evaluate()
        return self.main_expr.evaluate()

    def children(self):
        return list(self.fdefs) + [self.main_block, self.main_expr]

    def __str__(self):
        return "Program(%d functions)" % len(self.fdefs)


def print_ast(node, indent=0):
    padding = "  " * indent
    print(padding + str(node))
    for child in node.children():
        print_ast(child, indent + 1)
