# I created my own tests suite to check out the other cases
def test_update_kernel_diagnoses_alex(f):
    # Using a modified in-class example...
    kernel_diagnoses = []
    conflict = set([('A1', 1), ('A2', 1), ('X1', 1)])
    kernel_diagnoses = f(kernel_diagnoses, conflict)

    ok_(len(kernel_diagnoses) == 3, msg="Wrong length of kernel_diagnoses.")
    ok_(set([('A1', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")
    ok_(set([('A2', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")
    ok_(set([('X1', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")

    # One new and one old
    conflict = set([('A3', 1), ('X1', 1)])
    kernel_diagnoses = f(kernel_diagnoses, conflict)
    print(kernel_diagnoses)

    ok_(len(kernel_diagnoses) == 3, msg="Wrong length of kernel_diagnoses.")
    ok_(set([('A2', 0), ('A3', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")
    ok_(set([('A1', 0), ('A3', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")
    ok_(set([('X1', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")

    # Using a reduced in-class example with a new second conflict
    kernel_diagnoses = []
    conflict = set([('A1', 1), ('A2', 1), ('X1', 1)])
    kernel_diagnoses = f(kernel_diagnoses, conflict)

    ok_(len(kernel_diagnoses) == 3, msg="Wrong length of kernel_diagnoses.")
    ok_(set([('A1', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")
    ok_(set([('A2', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")
    ok_(set([('X1', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")

    conflict = set([('A3', 1)])
    kernel_diagnoses = f(kernel_diagnoses, conflict)
    print(kernel_diagnoses)

    ok_(len(kernel_diagnoses) == 3, msg="Wrong length of kernel_diagnoses.")
    ok_(set([('A2', 0), ('A3', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")
    ok_(set([('A1', 0), ('A3', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")
    ok_(set([('X1', 0), ('A3', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")

    # Using a reduced in-class example with an old second conflict
    kernel_diagnoses = []
    conflict = set([('A1', 1), ('A2', 1), ('X1', 1)])
    kernel_diagnoses = f(kernel_diagnoses, conflict)

    ok_(len(kernel_diagnoses) == 3, msg="Wrong length of kernel_diagnoses.")
    ok_(set([('A1', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")
    ok_(set([('A2', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")
    ok_(set([('X1', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")

    conflict = set([('X1', 1)])
    kernel_diagnoses = f(kernel_diagnoses, conflict)
    print(kernel_diagnoses)

    ok_(len(kernel_diagnoses) == 1, msg="Wrong length of kernel_diagnoses.")
    ok_(set([('X1', 0)]) in kernel_diagnoses, msg="Missing element of kernel_diagnoses.")

    test_ok()