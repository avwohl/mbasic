"""DEFINT, DEFSNG, DEFDBL and DEFSTR as the run-time statements they are.

On MBASIC 5.21 a DEFtype statement changes a table when it RUNS, and a name
without a suffix is typed from that table each time the program uses it
(measured on the binary):

- a DEFINT in a branch that is not taken, or jumped over, does nothing;
- a DEFINT that runs later in a loop types the earlier lines on the next pass;
- A and A% are two variables after DEFINT A, and A! is the single one: the
  type is part of the name, so the variable that A means changes with the table;
- CLEAR, RUN and NEW put all 26 letters back to single precision.

The parser still gives every node the suffix that the DEFtype statements above
it in the text imply, because the compilers and the semantic analyzer read it.
When a program has a DEFtype statement, Runtime.setup calls make_dynamic, and
the nodes whose name had no suffix in the source then read their suffix from the
table of the run: the node class is swapped for a subclass with a property.
A program with no DEFtype statement keeps the plain nodes and pays nothing.
"""

from dataclasses import is_dataclass

from src.ast_nodes import (
    VariableNode, ArrayDeclNode, EraseStatementNode, FunctionCallNode,
    DefFnStatementNode, DefTypeStatementNode, VarType)


_SUFFIX_OF_TYPE = {
    VarType.INTEGER: '%',
    VarType.SINGLE: '!',
    VarType.DOUBLE: '#',
    VarType.STRING: '$',
}


class DefTable:
    """The run-time DEFtype table: first letter -> suffix character."""

    __slots__ = ('suffix',)

    def __init__(self):
        self.suffix = {}
        self.reset()

    def reset(self):
        """All letters single precision (start of RUN, CLEAR)."""
        self.suffix = {chr(c): '!' for c in range(ord('a'), ord('z') + 1)}

    def apply(self, stmt):
        """Run a DefTypeStatementNode."""
        suffix = _SUFFIX_OF_TYPE[stmt.var_type]
        for letter in stmt.letters:
            self.suffix[letter.lower()] = suffix

    def for_name(self, name):
        """Suffix of an unsuffixed name; a name of FN is typed by the letter after FN."""
        return self.suffix.get(name[0], '!')


class DynVariableNode(VariableNode):
    """A variable whose source name had no suffix: the table types it."""

    @property
    def type_suffix(self):
        return self._deftable.suffix.get(self.name[0], '!')


class DynFunctionCallNode(FunctionCallNode):
    """FNA without a suffix: the letter after FN types the result."""

    @property
    def type_suffix(self):
        return self._deftable.suffix.get(self.name[2:3], '!')


class DynDefFnStatementNode(DefFnStatementNode):
    @property
    def type_suffix(self):
        return self._deftable.suffix.get(self.name[2:3], '!')


def make_dynamic(root, table, force=False):
    """Point the program at table, and make the unsuffixed names read it.

    Nodes that an earlier run made dynamic are pointed at the new table. The
    other nodes become dynamic only when the program has a DEFtype statement,
    or force is true (a statement typed at the Ok prompt, or a program parsed
    after a DEFtype was typed there). Returns True when nodes may be dynamic.
    """
    nodes = list(_walk(root))
    convert = force or any(isinstance(n, DefTypeStatementNode) for n in nodes)
    for node in nodes:
        cls = type(node)
        if cls in _DYNAMIC_CLASSES:
            node._deftable = table
            continue
        if not convert:
            continue
        if cls is VariableNode:
            if node.explicit_type_suffix:
                continue
            dyn = DynVariableNode
        elif cls is FunctionCallNode:
            if node.explicit_type_suffix or not node.name.startswith('fn'):
                continue
            dyn = DynFunctionCallNode
        elif cls is DefFnStatementNode:
            if node.explicit_type_suffix:
                continue
            dyn = DynDefFnStatementNode
        else:
            continue
        node.__class__ = dyn
        node._deftable = table
    return convert


# The code dispatches on type(node).__name__, so a dynamic node keeps the name
for _dyn, _base in ((DynVariableNode, VariableNode),
                    (DynFunctionCallNode, FunctionCallNode),
                    (DynDefFnStatementNode, DefFnStatementNode)):
    _dyn.__name__ = _dyn.__qualname__ = _base.__name__

_DYNAMIC_CLASSES = frozenset((DynVariableNode, DynFunctionCallNode, DynDefFnStatementNode))


def name_with_suffix(name, bare, table):
    """Array name of DIM or ERASE: a bare name takes the suffix of the table.

    The parser appends the suffix of a non-single DEFtype to name ('a%') and
    leaves a single bare ('a'); this is the same rule, run at run time.
    """
    if not bare:
        return name
    suffix = table.suffix.get(name[:1], '!')
    return name if suffix == '!' else name + suffix


def _walk(root):
    """Every AST node under root (dataclass instances, found through lists,
    tuples and dicts), each once."""
    seen = set()
    stack = [root]
    while stack:
        obj = stack.pop()
        if isinstance(obj, (list, tuple)):
            stack.extend(obj)
            continue
        if isinstance(obj, dict):
            stack.extend(obj.values())
            continue
        if not is_dataclass(obj) or isinstance(obj, type):
            continue
        if id(obj) in seen:
            continue
        seen.add(id(obj))
        yield obj
        stack.extend(vars(obj).values())
