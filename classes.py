class Literals:
    pass


class L(Literals):
    def __init__(self, name, assignment=None):
        self.name = name
        self.assignment: bool = assignment

    def __str__(self):
        if self.assignment is not None:
            return self.name + " = " + str(self.assignment)
        return self.name

    def __copy__(self):
        return L(self.name, self.assignment)


class OR:
    def __init__(self, *literals: [Literals]):
        self.literals: [Literals] = literals

    def __str__(self):
        if len(self.literals) is 0:
            return ""
        return "( " + " OR ".join([str(literal) for literal in self.literals]) + " )"

    def __copy__(self):
        return OR(self.literals.copy())


class AND:
    def __init__(self, *clauses: [OR]):
        self.clauses: [OR] = clauses

    def __str__(self):
        if len(self.clauses) is 0:
            return ""
        return "( " + " AND ".join([str(clause) for clause in self.clauses]) + " )"

    def __copy__(self):
        return AND(self.clauses.copy())

    # def __eq__(self, other):
    #     return self.clauses is other.clauses


class NOT(Literals):
    def __init__(self, literal):
        self.literal = literal

    @property
    def name(self):
        return self.literal.name

    @property
    def assignment(self):
        if self.literal.assignment is not None:
            return not self.literal.assignment
        return None
