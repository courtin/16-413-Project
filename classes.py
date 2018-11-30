from logic import *
from project_library import *
import matplotlib.pyplot as plt

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

    def __repr__(self):
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

    def __repr__(self):
        if self.literal.assignment is not None:
            return self.name + " = " + str(self.assignment)
        return self.name


class OR:
    def __init__(self, *literals: [Literals]):
        self.literals: [Literals] = literals

    def __repr__(self):
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
        self.true_exp = []

    def __repr__(self):
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
        self.true_exp = true_var_names
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

    def cnf_string(self) -> str:
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
    def is_satisfied(self) -> bool:
        for clause in self.clauses:
            if not clause.is_complete or not clause.has_true:
                return False
        return True

    @property
    def is_complete(self) -> bool:
        for clause in self.clauses:
            if not clause.is_complete:
                return False
        return True

    # returns a dict of the unique literals by name
    @property
    def literals_by_name(self) -> dict:
        return dict([(literal.name, literal) for literal in list(AND.get_unique_literals(self))])

    # returns the literals that are true (and ~var for false vars), not including the var if not assigned
    # e.g.: print(AND.from_string_to_cnf("A & B & C & ~D & E").unit_propagate().literals_true)
    @property
    def literals_true(self) -> [str]:
        literals = [literal.name if literal.assignment else "~" + literal.name
                            for literal in AND.get_unique_literals(self) if literal.assignment is not None]
        return literals

    # returns in-order list of inverted and otherwise literals
    @staticmethod
    def get_literals(formula) -> []:  # formula: AND
        literals = []
        for clause in formula:
            for prop in clause:
                literals.append(prop)
        return literals

    # returns a set of unique literals showing up in the formula
    @staticmethod
    def get_unique_literals(formula) -> set:  # formula: AND
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

class Spaceship():
    def create_system(self):
        system = []
        system.append("A1 ==> (X1 <=>(P1&V1))")
        system.append("A2 ==> (X2 <=>(P2&V2))")
        system.append("A3 ==> (T1 <=>(X1&X2))")
        system.append("A4 ==> (X3 <=>(V3&P1))")
        system.append("A5 ==> (X4 <=>(V4&P2))")
        system.append("A6 ==> (T2 <=>(X3&X4))")
        system.append("A7 ==> (S1 <=>((T1&Y3)|(T2&Y3)))")
        system.append("R1 ==> (Y3 <=>((Y1|Y2)))")
        system.append("C1 ==> (Y1 <=>B1)")
        system.append("C2 ==> (Y2 <=>B2)")
        return system
    
    def update_colors(self):
        #Draw good components in blue and unknown components in red
        for c in self.components:
            if self.components[c]._assignment == False:
                self.comp_dict[c] = (*self.comp_dict[c][0:5],'r')
            else:
                self.comp_dict[c] = (*self.comp_dict[c][0:5],'c')

    def __init__(self):
        self.system = self.create_system()
        self.inputs = {"P1":L("P1",None),
                      "P2":L("P2",None),
                      "V1":L("V1",None),
                      "V2":L("V2",None),
                      "V3":L("V3",None),
                      "V4":L("V4",None),
                      "B1":L("B1",None),
                      "B2":L("B2",None),}
        self.components = {"A1":L("A1",None),
                          "A2":L("A2",None),
                          "A3":L("A3",None),
                          "A4":L("A4",None),
                          "A5":L("A5",None),
                          "A6":L("A6",None),
                          "A7":L("O1",None),
                          "R1":L("R1",None),
                          "C1":L("C1",None),
                          "C2":L("C2",None)}
        self.states = {"X1":L("X1",None),
                          "X2":L("X2",None),
                          "X3":L("X3",None),
                          "X4":L("X4",None),
                          "Y1":L("Y1",None),
                          "Y2":L("Y2",None),
                          "Y3":L("Y3",None),
                          "T1":L("T1",None),
                          "T2":L("T2",None),
                          "S1":L("S1",None)}
        
        self.comp_dict = {"A4":(25,50,8,8,'k','c'),
                 "A1":(5,65,8,8,'k','c'),
                 "A3":(7.5,25,10,8,'k','c'),
                 "A2":(10,55,8,8,'k','c'),
                 "A5":(30,40,8,8,'k','c'),
                 "A6":(27.5,25,10,8,'k','c'),
                 "A7":(17.5,10,15,8,'k','c'),
                 "C2":(65,65,8,8,'k','c'),
                 "C1":(55,65,8,8,'k','c'),
                 "R1":(60,40,15,8,'k','c'),
                }
        self.inp_dict = {"P1":(5,75, 'k', 18),
               "P2":(30,75, 'k',18),
               "V1":(-15,65, 'k',18),
               "V2":(-15,55, 'k',18),
               "V3":(-15,48, 'k',18),
               "V4":(-15,40, 'k',18),
               "B2":(65,75, 'k',18),
               "B1":(50,75, 'k',18),
               "X1":(0,44,'g',14),
                "X2":(15,44,'b',14),
                "X3":(20,33,'g',14),
                "X4":(37,32,'b',14),
                "T1":(0,15,'r',14),
                "T2":(35,15,'r',14),
                "Y1":(50,50,'k',14),
                "Y2":(70,50,'k',14),
                "Y3":(65,20,'k',14),
                "S1":(18,-5,'k',14),
               }
        self.line_dict = {"l1":([5,5],[73,68], 'g'),
                "l2":([5,25, 25],[70,70, 53], 'g'),
                "l3":([30,30],[73,43], 'b'),
                "l4":([30,10, 10],[63,63,58], 'b'),
                "l5":([30,30],[36,29], 'b'),
                "l6":([25,25],[46,29], 'g'),
                "l7":([10,10],[51,29], 'b'),
                "l8":([5,5],[61,29], 'g'),
                "l9":([-5,1],[65,65], 'k'),#V1 to A1
                "l10":([-5,6],[55,55], 'k'),#V2 to A2
                "l11":([-5,21],[48,48], 'k'),#V3 to A4
                "l12":([-5,26],[40,40], 'k'),#V4 to A5
                "l13":([7.5, 7.5, 12.5,12.5], [21, 18, 18,14], 'r'),#A3 to A7
                "l14":([27.5, 27.5, 22.5,22.5], [21, 18, 18,14], 'r'),#A3 to A7
                "l15":([65,65],[69,73],'k'),#B2 to C2
                "l16":([55,55],[69,73],'k'),#B1 to C1
                "l17":([65,65],[61,44],'k'),#B1 to C1
                "l18":([55,55],[61,44],'k'),#B1 to C1
                "l19":([60,60,25],[36,10,10],'k'),#R1 to A7
                "l20":([18,18],[5,0],'k')
                }
    
    def change_input(self,inp,new_value):
        #Change the state of an input
        self.inputs[inp] = L(inp,new_value)
        
    def change_component(self,comp,new_value):
        #Change the state of a component
        self.components[comp] = L(comp,new_value)
        self.update_colors()

    def change_state(self,ns,new_value):
        #Change the internal state of a component
        self.states[ns] = L(ns,new_value)

    def all_off(self):
        #Turn off all inputs
        for c in self.inputs:
            self.change_input(c, False)

    def all_unknown(self):
        #Set all components in the ship to unknown
        for c in self.components:
            self.change_component(c, False)
        self.update_colors()

    def all_working(self):
        #Set all components in the ship to good
        for c in self.components:
            self.change_component(c,True)
        self.update_colors()
            
    def initialize(self):
        #Turn on a nominally working set of valves
        self.change_input("B1",True)
        self.change_input("P1",True)
        self.change_input("P2",True)
        self.change_input("V1",True)
        self.change_input("V2",True)
        
    def make_sentance(self,structure):
        #Make sentance specifically for dict data strucutres
        s = ""
        for e in structure:
            a = structure[e]._name
            val = structure[e]._assignment
            if val:
                c = a
            else:
                c = "~"+a
            if s == "":
                s = "("+c+")"
            else:
                s += "&("+c+")"
        return s

    def update_states(self, true_exp):
        #Update states for plotting
        for e in true_exp:
            if e.startswith("~"):
                key = e[1:]
                val = False
            else:
                key = e
                val = True
            if key in self.components:
                self.change_component(key,val)
            elif key in self.inputs:
                self.change_input(key,val)
            elif key in self.states:
                self.change_state(key,val)

    def plot_spaceship(self):
        #Draw the current state of the spaceship
        plt.clf()
        plt.axes()
        ax = plt.gca()

        for i in self.comp_dict:
            t = self.comp_dict[i]
            x = t[0]
            y = t[1]
            lx = t[2]
            ly = t[3]
            col = t[4]
            ax.add_patch(plt.Rectangle((x-lx/2.,y-ly/2.), lx, ly,  fill=True,fc=t[5], ec=col))
            plt.text(x,y,i, fontsize = 18, horizontalalignment = "center",verticalalignment = "center")

        for i in self.inp_dict:
            t = self.inp_dict[i]
            x = t[0]
            y = t[1]
            if i in self.inputs:
                if self.inputs[i]._assignment == None:
                    ps = i
                else:
                    ps = i + "=" + str(int(self.inputs[i]._assignment))
            elif i in self.states:
                if self.states[i]._assignment == None:
                    ps = i
                else:
                    ps = i + "=" + str(int(self.states[i]._assignment))
            else:
                ps = i
                    
            plt.text(x,y,ps,fontsize=t[3],color=t[2], horizontalalignment = "center",verticalalignment = "center")

        for l in self.line_dict:
            t = self.line_dict[l]
            plt.plot(t[0], t[1], color = t[2])


        #plt.axis('scaled')
        plt.xlim(-10,80)
        plt.axis('off')
        plt.show()
    def check_conflicts(self,observations):
        #Check if the current state of the spaceship is in conflict
        #Returns true if a set of inputs, component assignments, and observations is a conflict for a given system
        snt = make_sentance(self.system)+"&"+self.make_sentance(self.components)+"&"+self.make_sentance(self.inputs)
        clauses, true_statements = unit_propagation(snt)
        obs = conjuncts(to_cnf(observations))
        
        not_obs = []

        for o in obs:
            not_obs = (to_cnf(~o))
            if not_obs in true_statements:
                return True

        return False

class AStarNode:
    def __init__(self, variable, decision, probability, parent=None):
        self.parent = parent
        self.probability = probability
        self.decision_variable = variable
        self.decision = decision
        self.children = []
        self.a_star_trimmed = False
    @property
    def total_cost(self):
        ours = (self.probability if self.probability is not None else 1)
        if self.parent is None:
            return ours
        return self.parent.total_cost * ours
    @property
    def assignments(self):
        ours = [(self.decision_variable, self.decision)]
        if self.parent is None:
            if self.decision_variable is None:
                return []
            else:
                return ours
        return self.parent.assignments + ours

    # returns in [(X1, 0),..] format
    @property
    def resolution(self):
        return [(assignment[0], 1 if assignment[1] else 0) for assignment in self.assignments]

    @property
    def assignments_string(self):
        return " & ".join([("~" if not assignment[1] else "") + assignment[0] for assignment in self.assignments])
    @property
    def is_trimmed(self):
        if self.parent is None:
            return self.a_star_trimmed
        return self.a_star_trimmed or self.parent.is_trimmed
    def set_trimmed(self, trim: bool):
        self.a_star_trimmed = trim
        
    def construct_tree(self, remaining_components: [(str, float)]):
        if len(remaining_components) == 0:
            return
        (variable, good_probability) = remaining_components[0]
        remaining = remaining_components[1:]
        works_tree = AStarNode(variable, True, good_probability, self)
        broken_tree = AStarNode(variable, False, 1.0 - good_probability, self)
        self.children = tuple([works_tree, broken_tree])
        works_tree.construct_tree(remaining)
        broken_tree.construct_tree(remaining)
