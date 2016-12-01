import json

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

def printTree(rootNode, id):
    #Prints the tree in post order

    if 'left' in rootNode:
        printTree(rootNode['left'], "LEFT")

    if 'right' in rootNode:
        printTree(rootNode['right'], "RIGHT")

    print("BacktrackState: " + str(rootNode['backtrackState']))

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


if __name__ == "__main__":
    rootNode = testCalculateParsimonyScore3Levels()
    rootNode = backtrack(rootNode)
    printTree(rootNode, "ROOT")


