# Matrix

A matrix has columns split by " " and rows split by "\n".

Example:
1 2 0 0
0 1 2 0
0 0 1 2
0 0 0 1

## Usage
  - Use multiple selections to choose matrices and perform an operation.
  - To quickly insert a matrix, type `<rows>x<cols>` and press `tab`

## Operations (using command palette)
  - Add (+)
  - Multiply (\*)
  - Scale
  - Transpose (T)
  - Inverse (-1)
  - RREF
  - Format
  - Insert
  - Help (open this document)

Note: When two matrices are used in an operation, the matrix with lower line number is put first.
Note: Inverse and RREF may not be accurate due to floating point precision.


## Helpful shortcuts
  - Hold ⌘ for multiple selections
  - Hold ⌥ for rectangular selections (will make operations fail, but useful for copy/paste)
