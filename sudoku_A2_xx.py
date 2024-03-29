import sys
import copy
import heapq
import time

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists
        self.csp = self.CSP(puzzle)

    # variable choice heuristic: find variable with min of min{related R,C,B} size
    # value choice range: intersection of domain of R, C, B sets
    # value choice: TODO

    def solve(self):
        #TODO: Your code here
        print "With variable ordering heuristic"
        start = time.time()
        self.csp.preParse()
        print "time for preParse = {}".format(time.time()-start)
        start = time.time()
        self.csp.backTrackSearch()
        print "time for back track search = {}".format(time.time()-start)
        self.ans = self.csp.solution
        # don't print anything here. just resturn the answer
        # self.ans is a list of lists
        return self.ans

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY

    class CSP(object):
        
        def __init__(self, puzzle):
            self.counter = 0
            self.puzzle = puzzle
            self.solution = copy.deepcopy(self.puzzle)
            # fill up R, C, B domains
            temp = [i for i in range(1,10)]
            self.R = [set(temp) for _ in xrange(9)]
            self.C = [set(temp) for _ in xrange(9)]
            self.B = [set(temp) for _ in xrange(9)]
            self.orderedUnassignedVars = []
            self.unorderedUnassignedVars = []
            self.varChoiceHeuristicMatrix = [[0 for _ in range(9)] for _ in range(9)]


        def preParse(self):

            # constrict domains
            for i in range(9):
                for j in range(9):
                    num = self.puzzle[i][j]
                    if num != 0:
                        self.R[i].discard(num)
                        self.C[j].discard(num)
                        self.B[self.computeBoxNumberWithRowAndColumn(i,j)].discard(num)

            for i in range(9):
                for j in range(9):
                    num = self.puzzle[i][j]
                    if num == 0:
                        self.varChoiceHeuristicMatrix[i][j] = self.computeEmptySpaceTriplet(i,j)                        
                        var = self.Variable(i,j,0)
                        var.setVarPriority(self.varChoiceHeuristic(i,j))
                        self.unorderedUnassignedVars.append(var)
                        

            # print "*****************************************"
            # determine variable assignment sequence

            while len(self.unorderedUnassignedVars) != 0:
                chosenVar = self.findVarWithLowestH()
                self.orderedUnassignedVars.append(chosenVar)
                self.unorderedUnassignedVars.remove(chosenVar)
                self.updateUnorderedUnassignedVars(chosenVar)
            '''
            self.assignmentSequenceMatrix = copy.deepcopy(self.puzzle)
            for p in self.orderedUnassignedVars:
                print p
                self.printMatrix(p)

        def printMatrix(self, p):
            r = p.getRow()
            c = p.getColumn()
            self.assignmentSequenceMatrix[r][c] = "X"
            print "   0  1  2  3  4  5  6  7  8"
            for i in range(9):
                print "{} ".format(i),
                for j in range(9):
                    print "{} ".format(self.assignmentSequenceMatrix[i][j]),
                print
            self.assignmentSequenceMatrix[r][c] = "-"        
        '''    

        def computeEmptySpaceTriplet(self, i, j):
            rSize = len(self.R[i])
            cSize = len(self.C[j])
            bIdx = self.computeBoxNumberWithRowAndColumn(i,j)
            bSize = len(self.B[bIdx])
            return [rSize, cSize, bSize]

        def varChoiceHeuristic(self, i,j):
            # too unreadable in one line
            rSize = self.varChoiceHeuristicMatrix[i][j][0]
            cSize = self.varChoiceHeuristicMatrix[i][j][1]
            bSize = self.varChoiceHeuristicMatrix[i][j][2]
            return min(rSize, cSize, bSize)

        def findVarWithLowestH(self):
            return min(self.unorderedUnassignedVars, key=self.Variable.getVarPriority)   

        def updateUnorderedUnassignedVars(self, chosenVar):
            # TODO: how to update the H efficiently
            row = chosenVar.getRow()
            column = chosenVar.getColumn()
            box = self.computeBoxNumberWithRowAndColumn(row, column)
            for var in self.unorderedUnassignedVars:
                varRow = var.getRow()
                varColumn = var.getColumn()
                varBox = self.computeBoxNumberWithRowAndColumn(varRow, varColumn)
                if varRow == row:
                    self.varChoiceHeuristicMatrix[varRow][varColumn][0] -= 1
                elif varColumn == column:
                    self.varChoiceHeuristicMatrix[varRow][varColumn][1] -= 1

                if varBox == box:
                    self.varChoiceHeuristicMatrix[varRow][varColumn][2] -= 1

                var.setVarPriority(self.varChoiceHeuristic(varRow, varColumn))
                      
            pass       

        def computeBoxNumberWithRowAndColumn(self, i, j):
            return i//3*3 + j//3
                
        def backTrackSearch(self):
            #print("****New layer of back track search****")
            self.counter += 1
            if self.assignmentComplete():
                print "total number of back track search = {}".format(self.counter)
                return True
            var = self.selectVariable()
            #print("selected variable: ", var.getRow(), var.getColumn())

            consistentValues = self.getValidValues(var)

            #print("domain: ", consistentValues)
            while len(consistentValues) != 0:
                selection = self.valueSelection(var, consistentValues)
                #print("selected Value: ", selection)
                if self.forwardCheck(var, selection):
                    self.addSelection(var, selection)
                    self.removeFromRCBDomains(var, selection)
                    if self.backTrackSearch():
                        return True
                    self.removeSelection(var)
                    self.insertIntoRCBDomains(var, selection)
            # run out of consistent values
            # put selected var back so that this variable will have new domain
            self.orderedUnassignedVars.insert(0, var)
            return False

        def assignmentComplete(self):
            return len(self.orderedUnassignedVars) == 0

        def selectVariable(self):
            return self.orderedUnassignedVars.pop(0)

        def getValidValues(self, var):
            row = var.getRow()
            column = var.getColumn()
            box = self.computeBoxNumberWithRowAndColumn(row, column)

            rDomainSet = self.R[row]
            cDomainSet = self.C[column]
            bDomainSet = self.B[box]
            return list(rDomainSet.intersection(cDomainSet, bDomainSet))

        def valueSelection(self, var, consistentValues):
            # ordering values causes a severe performance hit
            '''
            row = var.getRow()
            clm = var.getColumn()
            box = self.computeBoxNumberWithRowAndColumn(row, clm)

            valueAffectedList = []
            
            for value in consistentValues:
                # variables affected
                affected = 0
                for i in range(9):
                    if not self.positionAssigned(row, i):
                        valueSetForAffectedVar = set(self.getValidValues(self.Variable(row, i, 0)))
                        if value in valueSetForAffectedVar:
                            affected += 1
                    if not self.positionAssigned(i, clm):
                        valueSetForAffectedVar = set(self.getValidValues(self.Variable(i, clm, 0)))
                        if value in valueSetForAffectedVar:
                            affected += 1

                    boxR = box//3*3 + i//3
                    boxC = box%3*3 + i%3
                    if not self.positionAssigned(boxR, boxC):
                        valueSetForAffectedVar = set(self.getValidValues(self.Variable(boxR, boxC, 0)))
                        if value in valueSetForAffectedVar:
                            affected += 1 
                
                valueAffectedList.append((value, affected))

            # sort values according to their affected number of variables in ascending order
            valueAffectedList.sort(key = lambda x: x[1])
            for i in range(len(consistentValues)):
                consistentValues[i] = valueAffectedList[i][0]                   
            '''
            return consistentValues.pop(0)            

        def positionAssigned(self, i, j):
            return self.solution[i][j] != 0

        def forwardCheck(self, var, selection):
            # TODO
            return True

        def addSelection(self, var, selection):
            row = var.getRow()
            column = var.getColumn()
            self.solution[row][column] = selection

        def removeFromRCBDomains(self, var, selection):
            row = var.getRow()
            column = var.getColumn()
            box = self.computeBoxNumberWithRowAndColumn(row, column)

            self.R[row].remove(selection)
            self.C[column].remove(selection)
            self.B[box].remove(selection)

        def removeSelection(self, var):
            row = var.getRow()
            column = var.getColumn()
            self.solution[row][column] = 0

        def insertIntoRCBDomains(self, var, selection):
            row = var.getRow()
            column = var.getColumn()
            box = self.computeBoxNumberWithRowAndColumn(row, column)
            self.R[row].add(selection)
            self.C[column].add(selection)
            self.B[box].add(selection)


        class Variable(object):
            def __init__(self, i, j, p):
                self.i = i
                self.j = j
                self.priority = p
            
            def getRow(self):
                return self.i
            
            def getColumn(self):
                return self.j

            def setVarPriority(self, p):
                self.priority = p

            def getVarPriority(self):
                return self.priority
            
            def __str__(self):
                return "Index: {},{}, Priority: {}\n".format(self.i, self.j, self.priority)

                    



if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python sudoku_A2_xx.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")
    
    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python sudoku_A2_xx.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    start = time.time()
    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()
    end = time.time()
    print "Total computation time = {}".format(end-start)

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")

