import ast

# using the NodeTransformer, you can also modify the nodes in the tree,
# however in this example NodeVisitor could do as we are raising exceptions
# only.
class Transformer(ast.NodeTransformer):
    ALLOWED_NAMES = {'None', 'False', 'True'}
    ALLOWED_NODE_TYPES = {
        'Expression', # a top node for an expression
        'Tuple',      # makes a tuple
        'Call',       # a function call (hint, Decimal())
        'Name',       # an identifier...
        'Load',       # loads a value of a variable with given identifier
        'Str',        # a string literal

        'Num',        # allow numbers too
        'List',       # and list literals
        'Dict',       # and dicts...

        'keyword',    # Keyword arguments
    }

    def __init__(self, allowed):
        self._allowed_names = allowed | self.ALLOWED_NAMES

    def visit_Name(self, node):
        if node.id not in self._allowed_names:
            raise RuntimeError("Name access to {} is not allowed".format(node.id))

        # traverse to child nodes
        return self.generic_visit(node)

    def generic_visit(self, node):
        nodetype = type(node).__name__
        if nodetype not in self.ALLOWED_NODE_TYPES:
            raise RuntimeError("Invalid expression: {} not allowed".format(nodetype))

        return super(Transformer, self).generic_visit(node)

# From: https://stackoverflow.com/questions/14611352/malformed-string-valueerror-ast-literal-eval-with-string-representation-of-tup
def restricted_eval(source, available):
    """Similar to ast.literal_eval, but slightly more permissive. This can evaluate class constructors."""

    allowed = {cls.__name__ for cls in available}
    restricted_globals = {cls.__name__: cls for cls in available}

    tree = ast.parse(source, mode='eval')

    transformer = Transformer(allowed)

    # Check validity of tree
    try:
        transformer.visit(tree)
    except RuntimeError as ex:
        raise RuntimeError("Failed to evaluate '{}' (allowed={}) due to '{}'".format(source, allowed, ex))

    # compile the ast into a code object
    clause = compile(tree, '<AST>', 'eval')

    # make the globals contain only the Decimal class,
    # and eval the compiled object
    return eval(clause, restricted_globals)
