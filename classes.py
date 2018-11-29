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
        return NOT(copy(self.literal))

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

    # You can't just deep copy all the literals, you need to make a new copy shared across the new AND
    def smart_copy(self, new_literals_by_old):
        return OR(*[
                NOT(new_literals_by_old[literal.literal]) if isinstance(literal, NOT) else new_literals_by_old[literal]
                    for literal in self.literals])

    def __iter__(self):
        return self.literals.__iter__()

    # True if all literals have assignments
    # otherwise False
    @property
    def is_complete(self):
        for lit in self.literals:
            if lit.assignment is None:
                return False
        return True

    # True if there is a true literal in the ORs,
    # otherwise False
    @property
    def has_true(self):
        for lit in self.literals:
            if lit.assignment is True:
                return True
        return False

class AND:
    def __init__(self, *clauses: [OR]):
        self.clauses: [OR] = clauses

    def __str__(self):
        if len(self.clauses) is 0:
            return ""
        return "( " + " & ".join([str(clause) for clause in self.clauses]) + " )"

    def __copy__(self):
        old_to_new_literals = dict([(literal, copy(literal)) for (name, literal) in self.literals_by_name.items()])
        return AND(*[clause.smart_copy(old_to_new_literals) for clause in self.clauses])

    def __iter__(self):
        return self.clauses.__iter__()

    # Calls into the unit_prop library code
    def unit_propagate(self):
        string = self.cnf_string()
        (clauses, true_exps) = unit_propagation(string)
        unique_literals = self.literals_by_name
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

    # for one-line convenience
    def print(self):
        print(self)

    def cnf_string(self):
        unique_literals = list(AND.get_unique_literals(self))
        assignment_strings = [literal.name if literal.assignment is True else "~" + literal.name
                   for literal in unique_literals if literal.assignment is not None]

        unassigned_self = copy(self)
        for literal in AND.get_unique_literals(unassigned_self):
            literal.assign(None)

        our_string = str(unassigned_self)
        out = "&".join([our_string] + assignment_strings)
        return out

    # If every OR has a true and is complete
    @property
    def is_satisfied(self):
        for clause in self.clauses:
            if not clause.is_complete or not clause.has_true:
                return False
        return True

    @property
    def is_complete(self):
        for clause in self.clauses:
            if not clause.is_complete:
                return False
        return True

    # returns a dict of the unique literals by name
    @property
    def literals_by_name(self):
        return dict([(literal.name, literal) for literal in list(AND.get_unique_literals(self))])

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

