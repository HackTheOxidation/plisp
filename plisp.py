""""""
from enum import Enum
import operator
import re
import sys


class DataType(Enum):
    Number = 0
    String = 1
    Variable = 2
    Function = 3


class UndefinedVariableException(BaseException):
    """
    Thrown whenever a name cannot be resolved to a variable.
    """


class UndefinedFunctionException(BaseException):
    """
    Thrown whenever a name cannot be resolved to a function.
    """


class AlreadyDefinedException(BaseException):
    """
    Thrown when an attempt to redefine a function is made.
    """


var_table = {}


def define_variable(var_name, var_value):
    var_table[var_name] = var_value


def resolve_variable(var_name):
    if var_name in var_table:
        return var_table[var_name]
    else:
        raise UndefinedVariableException


def define_function(func_name):
    if func_name in func_table:
        raise AlreadyDefinedException
    else:
        func_table[func_name] = lambda ast: ast.eval()
        

func_table = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "%": operator.mod,
    "defvar": define_variable,
    "defn": define_function,
    "exit": sys.exit,
}


class AST:
    def __init__(self, data, datatype, *args):
        self._data = data
        self._args = args
        self._datatype = datatype

    def eval(self):
        match self._datatype:
            case DataType.Function if callable(self._data):
                return self._data(*[arg.eval() for arg in self._args])
            case DataType.Variable:
                try:
                    return resolve_variable(self._data)
                except UndefinedVariableException:
                    return self._data
            case _:
                return self._data

    def __str__(self):
        return f"AST(data={self._data}" + (
            ", " + (", ".join(str(arg) for arg in self._args) + ")") if self._args else ")"
        )


def parse(code: str):
    """
    Parses the input code and builds and AST.
    """

    pattern = r"\ |,|\)"

    def _parse_function(data):
        if data in func_table:
            return func_table[data]
        else:
            raise UndefinedFunctionException

    if not code:
        return []

    first = code[0]

    if first == "(":
        data, rest = re.split(pattern, code[1:], maxsplit=1)
        result = parse(rest)
        if isinstance(result, list):
            return AST(_parse_function(data), DataType.Function, *result)
        else:
            return AST(_parse_function(data), DataType.Function, result)
    elif first == ")":
        return []
    elif first == " " or first == ",":
        return parse(code[1:])
    elif first.isnumeric():
        data, rest = re.split(pattern, code, maxsplit=1)
        result = parse(rest)
        if isinstance(result, list):
            return [AST(float(data), DataType.Number), *result]
        else:
            return [AST(float(data), DataType.Number), result]
    elif first == '"':
        data, rest = code[1:].split(maxsplit=1, sep='"')
        result = parse(rest)
        if isinstance(result, list):
            return [AST(str(data), DataType.String), *result]
        else:
            return [AST(str(data), DataType.String), result]
    else:
        data, rest = re.split(pattern, code, maxsplit=1)
        result = parse(rest)
        if isinstance(result, list):
            return [AST(data, DataType.Variable), *result]
        else:
            return [AST(data, DataType.Variable), result]


if __name__ == "__main__":
    while code := input(":> "):
        try:
            ast = parse(code)
            print(f"DEBUG -- ast: {ast}")
            result = ast.eval()
            print(result if result else "")
        except Exception as ex:
            print(f"ERROR: {ex}")
