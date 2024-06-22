import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz-11.0.0-win64/bin/'

from graphviz import Digraph
from typing import Type, List

pos = 0
print_eps_nodes = True


class Node:
    def __init__(self, data):
        self.value = data
        self.children = []

    def _is_empty_node(self):
        if len(self.children) == 1 and self.children[0].value == 'ε':
            return True
        return False

    def print(self, tree=None, parent_value="", id="main"):
        if not tree:
            tree = Digraph()
            tree.node_attr["shape"] = "plain"

        if not print_eps_nodes and self._is_empty_node():
            return tree

        if self.value == '<>':
            tree.node(id, str('\<\>'))
        else:
            tree.node(id, str(self.value))
        if parent_value:
            tree.edge(parent_value, id)

        for i, child in enumerate(self.children):
            child.print(tree, id, id + "." + str(i))

        return tree

def parse_relation_oper(tree: Node, lexemes: List[str]) -> bool:
    global pos
    if pos >= len(lexemes):
        return False

    if lexemes[pos] in ['=', '<>', '<', '<=', '>', '>=']:
        new_node = Node("\<знак операции отношения\>")
        new_node.children.append(Node(lexemes[pos]))
        tree.children.append(new_node)
        pos += 1
        return True
    return False

def parse_mult_oper_type(tree: Node, lexemes: List[str]) -> bool:
    global pos
    if pos >= len(lexemes):
        return False

    if lexemes[pos] in ['*', '/', '%']:
        new_node = Node('\<знак операции типа умножения\>')
        new_node.children.append(Node(lexemes[pos]))
        tree.children.append(new_node)
        pos += 1
        return True
    return False


def parse_addition_oper_type(tree: Node, lexemes: List[str]) -> bool:
    global pos
    if pos >= len(lexemes):
        return False

    if lexemes[pos] in ['+', '-']:
        new_node = Node("\<знак операции типа сложения\>")
        new_node.children.append(Node(lexemes[pos]))
        tree.children.append(new_node)
        pos += 1
        return True
    return False

def parse_identifier(tree: Node, lexemes: List[str]) -> bool:
    global pos
    if pos >= len(lexemes):
        return False

    if lexemes[pos].isalpha() and lexemes[pos] not in ['begin', 'end']:
        new_node = Node("\<идентификатор\>")
        new_node.children.append(Node(lexemes[pos]))
        tree.children.append(new_node)
        pos += 1
        return True
    return False


def parse_num(tree: Node, lexemes: List[str]) -> bool:
    global pos
    if pos >= len(lexemes):
        return False

    try:
        value = int(lexemes[pos])
    except:
        try:
            value = float(lexemes[pos])
        except:
            return False

    new_node = Node("\<число\>")
    new_node.children.append(Node(value))
    tree.children.append(new_node)
    pos += 1
    return True


def parse_primary_expression(tree: Node, lexemes: List[str]) -> bool:
    new_node = Node("\<первичное выражение\>")
    if parse_identifier(new_node, lexemes) or parse_num(new_node, lexemes):
        tree.children.append(new_node)
        return True
    elif parse_lex(new_node, lexemes, '('):
        if parse_math_expr(new_node, lexemes):
            if parse_lex(new_node, lexemes, ')'):
                tree.children.append(new_node)
                return True
    return False


def parse_multiplier_stroke(tree: Node, lexemes: List[str]) -> bool:
    new_node = Node("\<множитель’\>")
    if parse_lex(new_node, lexemes, '^'):
        if parse_primary_expression(new_node, lexemes):
            if parse_multiplier_stroke(new_node, lexemes):
                tree.children.append(new_node)
                return True
        return False

    # new_node.children.append(Node("ε"))
    # tree.children.append(new_node)
    return True

def parse_multiplier(tree: Node, lexemes: List[str]) -> bool:
    new_node = Node("\<множитель\>")
    if parse_primary_expression(new_node, lexemes):
        if parse_multiplier_stroke(new_node, lexemes):
            tree.children.append(new_node)
            return True

    return False

def parse_therm_stroke(tree: Node, lexemes: List[str]) -> bool:
    new_node = Node("\<терм’\>")
    if parse_mult_oper_type(new_node, lexemes):
        if parse_multiplier(new_node, lexemes):
            if parse_therm_stroke(new_node, lexemes):
                tree.children.append(new_node)
                return True
        return False

    # new_node.children.append(Node("ε"))
    # tree.children.append(new_node)
    return True


def parse_therm(tree: Node, lexemes: List[str]) -> bool:
    new_node = Node("\<терм\>")
    if parse_multiplier(new_node, lexemes):
        if parse_therm_stroke(new_node, lexemes):
            tree.children.append(new_node)
            return True

    return False


def parse_math_expr_stroke(tree: Node, lexemes: List[str]) -> bool:
    new_node = Node("\<арифметическое выражение’\>")
    if parse_addition_oper_type(new_node, lexemes):
        if parse_therm(new_node, lexemes):
            if parse_math_expr_stroke(new_node, lexemes):
                tree.children.append(new_node)
                return True
        return False

    # new_node.children.append(Node("ε"))
    # tree.children.append(new_node)
    return True


def parse_math_expr(tree: Node, lexemes: List[str]) -> bool:
    new_node = Node("\<арифметическое выражение\>")
    if parse_therm(new_node, lexemes):
        if parse_math_expr_stroke(new_node, lexemes):
            tree.children.append(new_node)
            return True
    elif parse_addition_oper_type(new_node, lexemes):
        if parse_therm(new_node, lexemes):
            if parse_math_expr_stroke(new_node, lexemes):
                tree.children.append(new_node)
                return True

    return False


def parse_expr(tree: Node, lexemes: List[str]) -> bool:
    new_node = Node("\<выражение\>")
    if parse_math_expr(new_node, lexemes):
        if parse_relation_oper(new_node, lexemes):
            if parse_math_expr(new_node, lexemes):
                tree.children.append(new_node)
                return True
            
    return False


def parse_operator(tree: Node, lexemes: List[str]) -> bool:
    new_node = Node("\<оператор\>")
    if parse_identifier(new_node, lexemes):
        if parse_lex(new_node, lexemes, ':='):
            if parse_expr(new_node, lexemes):
                tree.children.append(new_node)
                return True

    return False


def parse_operator_list_stroke(tree: Node, lexemes: List[str]) -> bool:
    new_node = Node("\<список операторов’\>")
    if parse_operator(new_node, lexemes):
        if parse_lex(new_node, lexemes, ';'):
            if parse_operator_list_stroke(new_node, lexemes):
                tree.children.append(new_node)
                return True
        return False

    # new_node.children.append(Node("ε"))
    # tree.children.append(new_node)
    return True


def parse_operator_list(tree: Node, lexemes: List[str]) -> bool:
    new_node = Node("\<список операторов\>")
    if parse_operator(new_node, lexemes):
        if parse_lex(new_node, lexemes, ';'):
            if parse_operator_list_stroke(new_node, lexemes):
                tree.children.append(new_node)
                return True

    return False


def parse_block(tree: Node, lexemes: List[str]) -> bool:
    new_node = Node("\<блок\>")
    if parse_lex(new_node, lexemes, 'begin'):
        if parse_operator_list(new_node, lexemes):
            if parse_lex(new_node, lexemes, 'end'):
                tree.children.append(new_node)
                return True
    return False


def parse_program(tree: Node, lexemes: List[str]) -> bool:
    new_node = Node("\<программа\>")
    if parse_block(new_node, lexemes):
        tree.children.append(new_node)
        return True

    return False


def parse_lex(tree: Node, lexemes: List[str], lex: str) -> bool:
    global pos
    if pos >= len(lexemes):
        return False

    if lexemes[pos] == lex:
        tree.children.append(Node(lex))
        pos += 1
        return True

    return False


def tokenize(inp: str) -> List[str]:
    tokens = []
    curr_pos = 0
    while curr_pos < len(inp):
        if inp[curr_pos: min(curr_pos + 5, len(inp))] in ['begin']:
            tokens += [inp[curr_pos: min(curr_pos + 5, len(inp))]]
            curr_pos += 5
        elif inp[curr_pos: min(curr_pos + 3, len(inp))] in ['end']:
            tokens += [inp[curr_pos: min(curr_pos + 3, len(inp))]]
            curr_pos += 3
        elif inp[curr_pos: min(curr_pos + 2, len(inp))] in ['<>', '<=', '>=', ':=']:
            tokens += [inp[curr_pos: min(curr_pos + 2, len(inp))]]
            curr_pos += 2
        elif inp[curr_pos] in ['=', '<', '>', '+', '-', '*', '/', '(', ')', ';', "%", "^"]:
            tokens += [inp[curr_pos]]
            curr_pos += 1
        elif inp[curr_pos] in ['\n', '\t', ' ', '\r']:
            curr_pos += 1
        else:
            start_pos = curr_pos
            while curr_pos < len(inp) and (inp[curr_pos].isalpha() or inp[curr_pos].isnumeric() or inp[curr_pos] in ["_", '.']):
                curr_pos += 1
            tokens += [inp[start_pos: curr_pos]]
            if start_pos == curr_pos:
                print("ERROR")
                break
    return tokens


def parse(mode: str, lexems: List[str]):
    tree = Node("head")
    res = False

    if mode == "parse_expression":
        res = parse_expr(tree, lexems)
    elif mode == "parse_program":
        res = parse_program(tree, lexems)

    if not res or pos != len(lexems):
        print("Syntax error!")
        return

    tree.children[0].print().render("tree", view=True)
