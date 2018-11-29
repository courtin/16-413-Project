from logic import *
from project_library import *

class Literals:
    @property
    def assignment(self):
        assert False

    def assign(self, value: bool):
        assert False

    @property
    def name(self):
        assert False


class L(Literals):
    def __init__(self, name, assignment=None):
        self._name = name
        self._assignment: bool = assignment

    def assign(self, value: bool):
        self._assignment = value

    @property
    def assignment(self):
        return self._assignment

    @property
    def name(self):
        return self._name

    def __str__(self):
        if self._assignment is not None:
            return self._name + " = " + str(self._assignment)
        return self._name

    def __copy__(self):
        return L(self._name, self._assignment)


class NOT(Literals):
    def __init__(self, literal: L):
        self.literal: L = literal

    @property
    def name(self):
        return "~" + self.literal.name

    @property
    def assignment(self):
        if self.literal.assignment is not None:
            return not self.literal.assignment
        return None

    def assign(self, value: bool):
        self.literal.assign(not value)

    def __copy__(self):
        return NOT(self.literal.copy())

    def __str__(self):
        if self.literal.assignment is not None:
            return self.name + " = " + str(self.assignment)
        return self.name


class OR:
    def __init__(self, *literals: [Literals]):
        self.literals: [Literals] = literals

    def __str__(self):
        if len(self.literals) is 0:
            return ""
        return "( " + " | ".join([str(literal) for literal in self.literals]) + " )"

    def __copy__(self):
        return OR(*[literal.copy() for literal in self.literals])

    def __iter__(self):
        return self.literals.__iter__()


class AND:
    def __init__(self, *clauses: [OR]):
        self.clauses: [OR] = clauses

    def __str__(self):
        if len(self.clauses) is 0:
            return ""
        return "( " + " & ".join([str(clause) for clause in self.clauses]) + " )"

    def __copy__(self):
        return AND(*[clause.copy() for clause in self.clauses])

    def __iter__(self):
        return self.clauses.__iter__()

    # modifies this instance, calls one round of unit propagation
    def unit_propagate(self):
        for or_clause in self.clauses:
            if len([literal for literal in or_clause.literals if literal.assignment is True]) > 0:
                continue
            unassigned = [literal for literal in or_clause.literals if literal.assignment is None]
            if len(unassigned) >= 2 or len(unassigned) == 0:
                continue
            unassigned[0].assign(True)
            return

    def unit_propagate_chris(self):
        string = self.cnf_string()
        (clauses, true_exps) = unit_propagation(string)
        unique_literals = dict([(literal.name, literal) for literal in list(AND.get_unique_literals(self))])
        true_var_names = [str(exp) for exp in true_exps]
        for var_name in true_var_names:
            if var_name.startswith("~"):
                var_name = var_name[1:]
                literal = unique_literals[var_name]
                literal.assign(False)
            else:
                literal = unique_literals[var_name]
                literal.assign(True)
        return self

    def print(self):
        print(self)

    def cnf_string(self):
        unique_literals = list(AND.get_unique_literals(self))
        assignment_strings = [literal.name if literal.assignment is True else "~" + literal.name
                   for literal in unique_literals if literal.assignment is not None]
        our_string = str(self)
        out = "&".join([our_string] + assignment_strings)
        return out

    # returns in-order list of inverted and otherwise literals
    @staticmethod
    def get_literals(formula): #PASS an AND
        literals = []
        for clause in formula:
            for prop in clause:
                literals.append(prop)
        return literals

    # returns a set of unique literals showing up in the formula
    @staticmethod
    def get_unique_literals(formula): #PASS an AND
        literals = AND.get_literals(formula)
        base_literals = [literal_or_not.literal if isinstance(literal_or_not, NOT) else literal_or_not
                for literal_or_not in literals]
        unique = set(base_literals)
        return unique

    @staticmethod
    def from_string_to_cnf(expression: Expr):
        # flatten the cnf_expr
        if isinstance(expression, str):
            expression = to_cnf(expression)

        or_clauses = []
        variables = {}

        and_op_const = "&"
        or_op_const = "|"
        not_op_const = "~"

        def get_variable_named(name):
            if name not in variables:
                variables[name] = L(name)
            return variables[name]

        # returns a literal
        def break_literal(exp) -> Literals:
            variable = None
            if exp.op is not_op_const:
                name = exp.args[0].op
                variable = NOT(get_variable_named(name))
            else:
                variable = get_variable_named(exp.op)
            return variable

        # returns list of OR'd literals
        def break_or(exp) -> [Literals]:
            assert exp.op is or_op_const
            literals: [Literals] = []

            for arg in exp.args:
                if arg.op is or_op_const:
                    literals.extend(break_or(arg))
                else:
                    variable = break_literal(arg)
                    literals.append(variable)

            return literals

        assert expression.op is and_op_const
        for arg in expression.args:
            if arg.op is or_op_const:
                clause = OR(*break_or(arg))
                or_clauses.append(clause)
            else:
                clause = OR(break_literal(arg))
                or_clauses.append(clause)

        return AND(*or_clauses)

