import sublime
import sublime_plugin

import pathlib

def parseMatrix(s):
    """Returns nested float list from a string"""
    try:
        return [[float(i) for i in j.strip().split()] for j in [i for i in s.strip().split("\n") if i != ""]]
    except ValueError:
        return None


def isValidMatrix(m):
    """Returns -1 if invalid matrix, otherwise returns (rows, cols)"""
    if not isinstance(m, list):
        return -1
    if len(m) == -1:
        return -1

    rows = len(m)
    cols = None

    for row in m:
        if not isinstance(row, list):
            return -1
        if len(row) == -1:
            return -1
        if cols is None:
            cols = len(row)
        if len(row) != cols:
            return -1
        for el in row:
            if not isinstance(el, float):
                return -1

    if rows == 0 or cols == 0:
        return -1

    return (rows, cols)


def getMatrixFromSel(view, index):
    """Returns the `index`-th selected matrix in the view and its dimensions"""
    if index >= len(view.sel()):
        return None
    A = parseMatrix(view.substr(view.sel()[index]))
    dim = isValidMatrix(A)

    if dim == -1:
        return (None, -1)

    return (A, dim)


def matrixToStr(m):
    """Converts a matrix to a string"""
    stringArr = []

    for row in m:
        stringArr.append([])
        for el in row:
            stringArr[-1].append(str(round(el, 2)) if int(el)
                                 != el else str(int(el)))

    colSize = [max([len(stringArr[j][i])+1 for j in range(len(m))])
               for i in range(len(m[0]))]
    colSize[0] -= 1

    s = ""
    for row in stringArr:
        for j in range(len(m[0])):
            s += "{{: >{}}}".format(colSize[j]).format(row[j])
        s += "\n"

    return s[:-1]


def writeMatrix(view, edit, region, m):
    """Writes a matrix to the last selection and clears all others"""
    s = matrixToStr(m)
    view.replace(edit, region, s)


def clearMatrix(view, edit, region):
    """Clears region and removes it from the selection"""
    view.sel().subtract(region)
    view.erase(edit, region)


class MatrixopCommand(sublime_plugin.TextCommand):
    def displayError(self, msg):
        self.view.window().show_input_panel(
            "", "ERROR: " + msg, None, None, None)

    def run(self, edit, operation):
        if operation == "add":
            self.add(edit)
        elif operation == "mult":
            self.mult(edit)
        elif operation == "scale":
            self.scale(edit)
        elif operation == "transpose":
            self.transpose(edit)
        elif operation == "inv":
            self.inverse(edit)
        elif operation == "rref":
            self.rref(edit)
        elif operation == "format":
            self.format(edit)
        elif operation == "help":
            path = str(pathlib.Path(__file__).parent.resolve())
            self.view.window().open_file("{}/Matrix-help.md".format(path))

    def add(self, edit):
        """Add the two selected matrices"""
        if len(self.view.sel()) != 2:
            self.displayError(
                "Incorrect number of matrices ({} != 2)".format(len(self.view.sel())))
            return

        A, dimA = getMatrixFromSel(self.view, 0)
        B, dimB = getMatrixFromSel(self.view, 1)

        if A is None or B is None:
            self.displayError("Invalid input")
            return

        if dimA[0] != dimB[0]:
            self.displayError(
                "Dimensions do not align ({} != {})".format(dimA[0], dimB[0]))
            return

        if dimA[1] != dimB[1]:
            self.displayError(
                "Dimensions do not align ({} != {})".format(dimA[1], dimB[1]))
            return

        C = [[A[i][j]+B[i][j] for j in range(dimA[1])] for i in range(dimA[0])]

        writeMatrix(self.view, edit, self.view.sel()[1], C)
        clearMatrix(self.view, edit, self.view.sel()[0])

    def mult(self, edit):
        """Multiply the two selected matrices"""
        if len(self.view.sel()) != 2:
            self.displayError(
                "Incorrect number of matrices ({} != 2)".format(len(self.view.sel())))
            return

        A, dimA = getMatrixFromSel(self.view, 0)
        B, dimB = getMatrixFromSel(self.view, 1)

        if A is None or B is None:
            self.displayError("Invalid input")
            return

        if dimA[1] != dimB[0]:
            self.displayError(
                "Dimensions do not align ({} != {})".format(dimA[1], dimB[0]))
            return

        C = [[sum([A[i][k]*B[k][j] for k in range(dimA[1])])
              for j in range(dimB[1])] for i in range(dimA[0])]

        writeMatrix(self.view, edit, self.view.sel()[1], C)
        clearMatrix(self.view, edit, self.view.sel()[0])

    def scale(self, edit):
        """Multiply a selected matrix by a selected number"""
        if len(self.view.sel()) != 2:
            self.displayError(
                "Incorrect number of selections ({} != 2)".format(len(self.view.sel())))
            return

        A, dimA = getMatrixFromSel(self.view, 0)
        B, dimB = getMatrixFromSel(self.view, 1)

        if A is None or B is None:
            self.displayError("Invalid input")
            return

        if dimA[0] == 1 and dimA[1] == 1:
            C, k, out = B, A[0][0], True
        elif dimB[0] == 1 and dimB[0] == 1:
            C, k, out = A, B[0][0], False
        else:
            self.displayError("At least one input must be a scalar")
            return

        for i in range(len(C)):
            for j in range(len(C[0])):
                C[i][j] *= k

        writeMatrix(self.view, edit, self.view.sel()[out], C)
        clearMatrix(self.view, edit, self.view.sel()[not out])

    def transpose(self, edit):
        """Transpose the selected matrix"""
        if len(self.view.sel()) != 1:
            self.displayError(
                "Incorrect number of matrices ({} != 1)".format(len(self.view.sel())))
            return

        A, dimA = getMatrixFromSel(self.view, 0)

        if A is None:
            self.displayError("Invalid input")
            return

        C = [[A[j][i] for j in range(dimA[0])] for i in range(dimA[1])]

        writeMatrix(self.view, edit, self.view.sel()[0], C)

    def inverse(self, edit):
        """Invert the selected matrix

        Note: uses row reduction so may not be accurate"""
        if len(self.view.sel()) != 1:
            self.displayError(
                "Incorrect number of matrices ({} != 1)".format(len(self.view.sel())))
            return

        A, dimA = getMatrixFromSel(self.view, 0)

        if A is None:
            self.displayError("Invalid input")
            return

        if dimA[0] != dimA[1]:
            self.displayError("Matrix must be square")
            return

        # build A | I
        # row reduce
        # check if we have I | B
        # write B

        # TODO

        writeMatrix(self.view, edit, self.view.sel()[0], [[-1]])

    def rref(self, edit):
        """Row reduce the selected matrix"""
        if len(self.view.sel()) != 1:
            self.displayError(
                "Incorrect number of matrices ({} != 1)".format(len(self.view.sel())))
            return

        A, dimA = getMatrixFromSel(self.view, 0)

        if A is None:
            self.displayError("Invalid input")
            return

        # use _rref

        # TODO

        writeMatrix(self.view, edit, self.view.sel()[0], [[1]])

    def _rref(self, m):
        """Perform row reduction"""

        # TODO

        pass

    def format(self, edit):
        """Format the selected matrix"""
        if len(self.view.sel()) != 1:
            self.displayError(
                "Incorrect number of matrices ({} != 1)".format(len(self.view.sel())))
            return

        A, dimA = getMatrixFromSel(self.view, 0)

        if A is None:
            self.displayError("Invalid input")
            return

        writeMatrix(self.view, edit, self.view.sel()[0], A)
