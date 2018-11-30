from utils import *
from logic import *
from copy import *

def unit_propagation(s):
    # This implementation of unit propagation works but doesn't record support for each clause; will update

    clauses = check_input(s)

    repeat = True
    false_exp = []  # List of literals known to be false
    true_exp = []  # List of literals known to be true (inverse of false_exp, created here for convenience)
    while repeat:  # Repeat the unit propagation steps until the clauses can't be reduced further
        repeat = False
        for c in clauses:  # For each clause in the sentance
            if len(c.args) <= 1 and len(
                    clauses) > 0:  # Check if the clause contains a single literal/the list isn't empty
                cc = copy(c)  # Create a copy of that literal
                if cc not in true_exp:  # Check that the literal hasn't already been saved
                    true_exp.append(cc)  # Add that literal to the list of true literals
                    false_exp.append(to_cnf(~cc))  # Add the negation of that literal to the list of false literals
                    repeat = True  # Repeat the entire loop; since a new literal has been proven we may be able to
                    # propagate more

        for e in true_exp:  # For every literal we know to be true...
            if e in clauses: clauses.remove(e)  # Remove that literal from clauses where it appears.

        for c in clauses:  # For each clause in the sentance
            for fe in false_exp:  # For each literal we know to be false
                if fe in copy(c.args):  # If that literal is in the clause
                    if c.op != "~":  # (Syntatic check)
                        c.args.remove(fe)  # Remove that literal from the clause
        clauses = trim_or(clauses)  # Clean up syntax
    return clauses, true_exp

def update_kernel_diagnoses(kernel_diagnoses, conflict):
    new_kernel_diagnoses = []
    if len(kernel_diagnoses) == 0:
        for component in conflict:
            new_kernel_diagnoses.append({(component[0], 0)})
    else:
        for k in kernel_diagnoses:
            for c in conflict:
                k_new = copy(k)
                k_new.add((c[0], 0))
                if k_new not in new_kernel_diagnoses:
                    new_kernel_diagnoses.append(k_new)
        for i in range(len(new_kernel_diagnoses)):
            nk = new_kernel_diagnoses.pop(0)
            for ok in copy(new_kernel_diagnoses):
                if nk.issubset(ok):
                    new_kernel_diagnoses.remove(ok)
            new_kernel_diagnoses.append(nk)
    return new_kernel_diagnoses
