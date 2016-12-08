import itertools

def calculateParsimonyScore(rootNode):
    parsimonyScore = 0

    # Do post order traversal of the tree
    # Check if there is a left child
    if 'left' in rootNode:
        parsimonyScore += calculateParsimonyScore(rootNode['left'])

    # Check if there is right child
    if 'right' in rootNode:
        parsimonyScore += calculateParsimonyScore(rootNode['right'])

    # Assume that the states of the leaves are already set
    # and find the state of a node if it is not a leaf

    if 'left' in rootNode and 'right' in rootNode:

        # If any states intersect between the 2 children of a node
        if len(list(set(rootNode['left']['state']) & set(rootNode['right']['state']))) > 0 :
            rootNode['state'] = set(rootNode['left']['state']) & set(rootNode['right']['state'])

        else:
            rootNode['state'] = rootNode['left']['state'] + rootNode['right']['state']

            # Find the minimum score of 2 distances in the internal node's state
            minimumScore = None
            for leftState in rootNode['left']['state']:
                for rightState in rootNode['right']['state']:
                    if minimumScore is None or abs(leftState - rightState) < minimumScore:
                        minimumScore = abs(leftState - rightState)

            parsimonyScore += minimumScore

    return parsimonyScore

def backtrack(rootNode):
    if 'parent' not in rootNode:
        rootNode['backtrackState'] = list(rootNode['state'])[0]

    else:
        if rootNode['parent']['backtrackState'] in rootNode['state']:
            rootNode['backtrackState'] = rootNode['parent']['backtrackState']

        else:
            rootNode['backtrackState'] = rootNode['state'][0]

    if 'left' in rootNode:
        backtrack(rootNode['left'])

    if 'right' in rootNode:
        backtrack(rootNode['right'])

    return rootNode

def setupTree(leafNodeList):
    rootNode = {}
    pointerQueue = [rootNode]

    while len(pointerQueue) != len(leafNodeList):
        pointer = pointerQueue.pop(0)
        leftNode = {'parent': pointer}
        rightNode = {'parent': pointer}
        pointer['left'] = leftNode
        pointer['right'] = rightNode
        pointerQueue.append(leftNode)
        pointerQueue.append(rightNode)

    for i in range(len(leafNodeList)):
        pointerQueue[i]['name'] = leafNodeList[i]['name']
        pointerQueue[i]['state'] = [leafNodeList[i]['state']]

    return rootNode

def printTreeWrapper(rootNode):
    print("Begin printing tree.")
    printTree(rootNode)
    print("End printing tree.")

def printTree(rootNode):
    #Prints the tree in postorder
    if 'left' in rootNode:
        printTree(rootNode['left'])

    if 'right' in rootNode:
        printTree(rootNode['right'])

    if 'name' in rootNode:
        print("Name: " + rootNode['name'] + " \tBacktrackState: " + str(rootNode['backtrackState']))

    else:
        print("BacktrackState: " + str(rootNode['backtrackState']))

def runAnalysis(species, storeAllTrees=False, percentDifference=0.025):
    minScore = 9999
    minTree = None
    allTrees = []

    for permutation in itertools.permutations(species):
        tree = setupTree(permutation)
        score = calculateParsimonyScore(tree)
        print("Score for this run: " + str(score))
        if storeAllTrees:
            allTrees.append([tree, score])

        if score < minScore:
            minScore = score
            minTree = tree

    if storeAllTrees:
        treesToPrint = [i for i in allTrees if abs(i[1] - minScore) <= (minScore*percentDifference)]

        for i in treesToPrint:
            print("Score for this tree: " + str(i[1]))
            rootNode = backtrack(i[0])
            printTreeWrapper(rootNode)

        print("Smallest score: " + str(minScore))
        print(str.format("Printing trees with score within {} of smallest score", str(minScore*percentDifference)))

        print(str.format("Number of trees within threshold value: " + str(len(treesToPrint))))
        print(str.format("Total number of trees generated: " + str(len(allTrees))))
        print(str.format("Printing all trees within {}% of minimum parsimony score found.", str(percentDifference)))

    else:
        print("Backtracking and printing on tree with lowest score: " + str(minScore))
        rootNode = backtrack(minTree)
        printTreeWrapper(rootNode)

## TESTS

def testCalculateParsimonyScore():
    rootNode = {}
    rootNode['left'] = {'state': [4], 'parent':rootNode}
    rootNode['right'] = {'state': [5], 'parent': rootNode}
    print(calculateParsimonyScore(rootNode))
    return rootNode

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
    rootNode = setupTree(leaves)
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

    runAnalysis(species, storeAllTrees=True)

if __name__ == "__main__":
    nineSpecieAnalysis()


