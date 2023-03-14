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
            stringArr[-1].append(str(round(el, 4)) if int(el)
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
        elif operation == "insert":
            self.insert(edit)
        elif operation == "make_insert":
            self.makeInsert(edit)
        elif operation == "help":
            with open(str(pathlib.Path(__file__).parent.resolve()) + "help.html", "r") as f:
                self.view.window().new_html_sheet("Matrix Calculator Help", f.read())

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

        I = [[1 if i == j else 0 for j in range(
            dimA[0])] for i in range(dimA[0])]
        B = [A[i] + I[i] for i in range(dimA[0])]
        self._rref(B, [dimA[0], dimA[0]*2])

        newI = [B[i][:dimA[0]] for i in range(dimA[0])]
        A_inv = [B[i][dimA[0]:] for i in range(dimA[0])]

        for i in range(dimA[0]):
            for j in range(dimA[0]):
                if newI[i][j] != (1 if i == j else 0):
                    self.displayError("Matrix is not invertible")
                    return

        writeMatrix(self.view, edit, self.view.sel()[0], A_inv)

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

        self._rref(A, dimA)

        writeMatrix(self.view, edit, self.view.sel()[0], A)

    def _rref(self, A, dim):
        """Perform row reduction"""

        h = 0
        k = 0
        while h < dim[0] and k < dim[1]:
            pivot_row = 0
            pivot_val = -1
            for i in range(h, dim[0]):
                if abs(A[i][k]) > pivot_val:
                    pivot_row = i
                    pivot_val = A[i][k]

            if pivot_val == 0:
                k += 1
                continue

            A[h], A[pivot_row] = A[pivot_row], A[h]
            A[h] = [i/pivot_val for i in A[h]]

            for i in range(dim[0]):
                if i == h:
                    continue
                f = A[i][k]
                A[i][k] = 0
                for j in range(k+1, dim[1]):
                    A[i][j] = A[i][j] - A[h][j]*f

            h += 1
            k += 1

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

    def insert(self, edit):
        """Insert a new matrix

        Assumes the current line only contains &lt;rows&gt;x&lt;cols&gt; with the cursor at the end
        """
        if len(self.view.sel()) > 1:
            self.displayError("Too many cursors")
            return
        sel = self.view.sel()[0]
        span = sublime.Region(self.view.line(sel.begin()).begin(), sel.end())
        text = self.view.substr(span)
        rows, cols = [int(i) for i in text.split("x")]
        snippet = ""
        for i in range(rows):
            for j in range(cols):
                snippet += "${{{}:0}} ".format(i*cols + j + 1)
            snippet += "\n"
        snippet += "$0"
        self.view.erase(edit, span)
        self.view.run_command("insert_snippet", {"contents": snippet})

    def makeInsert(self, edit):
        """Insert a new matrix

        Make a new line if needed and ask for user input
        """

        if len(self.view.sel()) > 1:
            self.displayError("Too many cursors")
            return
        sel = self.view.sel()[0]
        if len(self.view.sel()[0]) > 0:
            self.displayError("Nothing should be selected")
            return
        if self.view.lines(sel)[0].begin() != sel.begin():
            self.view.insert(edit, self.view.sel()[0].begin(), "\n")
        self._getInputAndInsert(edit)

    def _getInputAndInsert(self, edit):
        """Helper method for `makeInsert`"""
        self._editStore = edit
        self.view.window().show_input_panel("Rows", "", self._getCols, None, None)

    def _getCols(self, rows):
        """Helper method for `makeInsert`"""
        self._rowsStore = rows
        self.view.window().show_input_panel("Cols", "", self._andInsert, None, None)

    def _andInsert(self, cols):
        """Helper method for `makeInsert`"""
        edit = self._editStore
        try:
            rows = int(self._rowsStore)
            cols = int(cols)
        except ValueError:
            self.displayError("Invalid input")
        snippet = ""
        for i in range(rows):
            for j in range(cols):
                snippet += "${{{}:0}} ".format(i*cols + j + 1)
            snippet += "\n"
        snippet += "$0"
        self.view.run_command("insert_snippet", {"contents": snippet})
 

