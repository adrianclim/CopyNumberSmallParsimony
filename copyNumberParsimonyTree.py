import itertools
import newick

class CopyNumberNode(newick.Node):
    def __init__(self, copyNumber=None, **kw):
        self.copyNumber = [copyNumber]
        self.backtrackstate = []
        self.bootstrapValue = None
        super(CopyNumberNode, self).__init__()

    @property
    def newick(self):
        """The representation of the Node in Newick format."""
        label = self.name or ''
        if self.bootstrapValue is not None:
            label += str(self.bootstrapValue)
        if self._length:
            label += ':' + self._length
        descendants = ','.join([n.newick for n in self.descendants])
        if descendants:
            descendants = '(' + descendants + ')'
        return descendants + label

def calculateParsimonyScore(rootNode):
    parsimonyScore = 0

    # Do post order traversal of the tree
    # Check if there is a left child
    for i in rootNode.descendants:
        parsimonyScore += calculateParsimonyScore(i)

    # Assume that the states of the leaves are already set
    # and find the state of a node if it is not a leaf

    if len(rootNode.descendants) == 2:
        # If any states intersect between the 2 children of a node
        if len(list(set(rootNode.descendants[0].copyNumber) & set(rootNode.descendants[1].copyNumber))) > 0 :
            rootNode.copyNumber = set(rootNode.descendants[0].copyNumber) & set(rootNode.descendants[1].copyNumber)

        else:
            rootNode.copyNumber = rootNode.descendants[0].copyNumber + rootNode.descendants[1].copyNumber

            # Find the minimum score of 2 distances in the internal node's state
            minimumScore = None
            for leftState in rootNode.descendants[0].copyNumber:
                for rightState in rootNode.descendants[1].copyNumber:
                    if minimumScore is None or abs(leftState - rightState) < minimumScore:
                        minimumScore = abs(leftState - rightState)

            parsimonyScore += minimumScore

    return parsimonyScore

def backtrack(rootNode):
    if rootNode.ancestor is None:
        rootNode.backtrackstate = rootNode.copyNumber[0]

    else:
        if rootNode.ancestor.backtrackstate in rootNode.copyNumber:
            rootNode.copyNumber = rootNode.ancestor.backtrackstate

        else:
            rootNode.backtrackstate = rootNode.copyNumber[0]

    for i in rootNode.descendants:
        backtrack(i)

    return rootNode

def setupNewickTree(leafNodeList):
    rootNode = CopyNumberNode()
    pointerQueue = [rootNode]

    while len(pointerQueue) != len(leafNodeList):
        pointer = pointerQueue.pop(0)
        leftNode = CopyNumberNode()
        rightNode = CopyNumberNode()

        pointer.add_descendant(leftNode)
        pointer.add_descendant(rightNode)
        pointerQueue.append(leftNode)
        pointerQueue.append(rightNode)

    for i in range(len(leafNodeList)):
        pointerQueue[i].name = leafNodeList[i]['name']
        pointerQueue[i].copyNumber = [leafNodeList[i]['state']]

    return rootNode


def printTreeWrapper(rootNode, newickOutput=False, outputFile = None):
    if newickOutput:
        if outputFile is None:
            print(newick.dumps(rootNode))
        else:
            with open(outputFile, 'a') as out:
                out.write(newick.dumps(rootNode) + "\n")

    else:
        print("Begin printing tree.")
        printTree(rootNode)
        print("End printing tree.")

def printTree(rootNode):
    #Prints the tree in postorder
    for i in rootNode.descendants:
        printTree(i)

    if rootNode.name is not None:
        print("Name: " + rootNode.name + " \tBacktrackState: " + str(rootNode.backtrackstate))

    else:
        print("BacktrackState: " + str(rootNode.backtrackstate))

def bootstrapAnalysis(masterRootNode, treeSpace):
    totalBootStrapValue = 0

    if len(masterRootNode.descendants) > 0:
        firstchildSet = set([i.name for i in masterRootNode.descendants[0].get_leaves()])
        secondChildSet = set([j.name for j in masterRootNode.descendants[1].get_leaves()])

        for tree in [k[0] for k in treeSpace]:
            if searchForNodeWithChildren(tree, firstchildSet, secondChildSet):
                totalBootStrapValue += 1

        masterRootNode.bootstrapValue = totalBootStrapValue

    for l in masterRootNode.descendants:
        bootstrapAnalysis(l, treeSpace)

def searchForNodeWithChildren(currentNode, firstChildSet, secondChildSet):
    if currentNode.descendants is None or len(currentNode.descendants) == 0:
        return False

    leftCurrentNodeLeaves = set([i.name for i in currentNode.descendants[0].get_leaves()])
    rightcurrentNodeLeaves = set([j.name for j in currentNode.descendants[1].get_leaves()])

    print(firstChildSet)
    print(secondChildSet)
    print(leftCurrentNodeLeaves)
    print(rightcurrentNodeLeaves)
    print("space")

    if leftCurrentNodeLeaves == firstChildSet and rightcurrentNodeLeaves == secondChildSet:
        print("match")
        return True

    elif leftCurrentNodeLeaves == secondChildSet and rightcurrentNodeLeaves == firstChildSet:
        print("match")
        return True

    elif len(currentNode.descendants)>0:
        for i in currentNode.descendants:
            if searchForNodeWithChildren(i, firstChildSet, secondChildSet):
                return True

def runAnalysis(species, storeAllTrees=False, percentDifference=0.01, newickOutput=False, outputFile = None):
    minScore = 9999
    minTree = None
    allTrees = []
    allTreesCount = 0

    for permutation in itertools.permutations(species):
        tree = setupNewickTree(permutation)
        score = calculateParsimonyScore(tree)
        print("Score for this run: " + str(score))
        if storeAllTrees:
            allTreesCount += 1

            # Gotta save some memory to prevent thrashing
            if abs(score - minScore) <= (minScore*percentDifference):
                allTrees.append([tree, score])

        if score < minScore:
            minScore = score
            minTree = tree

    if storeAllTrees:
        treesToPrint = [i for i in allTrees if abs(i[1] - minScore) <= (minScore*percentDifference)]

        for i in treesToPrint:
            print("Score for this tree: " + str(i[1]))
            backtrack(i[0])

        bootstrapAnalysis(minTree, treesToPrint)
        printTreeWrapper(minTree, newickOutput, outputFile=outputFile)

        print("Smallest score: " + str(minScore))
        print(str.format("Printing trees with score within {} of smallest score", str(minScore*percentDifference)))

        print(str.format("Number of trees within threshold value: " + str(len(treesToPrint))))
        print(str.format("Total number of trees generated: " + str(allTreesCount)))
        print(str.format("Printing all trees within {}% of minimum parsimony score found.", str(percentDifference)))

    else:
        print("Backtracking and printing on tree with lowest score: " + str(minScore))
        rootNode = backtrack(minTree)
        printTreeWrapper(rootNode, newickOutput, outputFile=outputFile)

## TESTS

#TODO rewrite these tests for new tree structure
def testCalculateParsimonyScore():
    rootNode = {}
    rootNode['left'] = {'state': [4], 'parent':rootNode}
    rootNode['right'] = {'state': [5], 'parent': rootNode}
    print(calculateParsimonyScore(rootNode))
    return rootNode

#TODO rewrite these tests for new tree structure
def testCalculateParsimonyScore3Levels():
    rootNode = {}
    rootNode['left'] = {'parent':rootNode}
    rootNode['right'] = {'parent':rootNode}

    rootNode['left']['left'] = {'state': [6], 'parent':rootNode['left']}
    rootNode['left']['right'] = {'state': [7], 'parent':rootNode['left']}
    rootNode['right']['left'] = {'state': [7], 'parent':rootNode['right']}
    rootNode['right']['right'] = {'state': [8], 'parent':rootNode['right']}

    print(calculateParsimonyScore(rootNode))
    return rootNode

def testTreeSetup():
    leaves = [{'name': "FIRST", 'state':1},{'name': "SECOND", 'state':2},{'name': "THIRD", 'state':3}]
    rootNode = setupNewickTree(leaves)
    return rootNode

## ANALYSIS

def nineSpecieAnalysis():
    species = [
        {'name': "Evasterias troschelii", 'state': 14.83},
        {'name': "Dermasterias imbricata", 'state': 58.42},
        {'name': "Meridiastra calcar", 'state': 49.42},
        {'name': "Patiria pectinifera", 'state': 0},
        {'name': "Cryptasterina hystera", 'state': 7.66},
        {'name': "Cryptasterina pentagona", 'state': 47.33},
        {'name': "Parvulastra parvivipara", 'state': 55.33},
        {'name': "Parvulastra vivipara", 'state': 52.3},
        {'name': "Parvulastra exigua", 'state': 60.84},
    ]

    runAnalysis(species, percentDifference= 0.005, storeAllTrees=True, newickOutput=True, outputFile=None) #"copyNumberTrees.tree")

if __name__ == "__main__":
    nineSpecieAnalysis()


