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


def testCalculateParsimonyScore():
    rootNode = {}
    rootNode['left'] = {'state': [4]}
    rootNode['right'] = {'state': [4,5]}
    print(calculateParsimonyScore(rootNode))

def testCalculateParsimonyScore3Levels():
    rootNode = {}
    rootNode['left'] = {}
    rootNode['right'] = {}

    rootNode['left']['left'] = {'state': [6]}
    rootNode['left']['right'] = {'state': [7]}
    rootNode['right']['left'] = {'state': [7]}
    rootNode['right']['right'] = {'state': [8]}

    print(calculateParsimonyScore(rootNode))

if __name__ == "__main__":
    testCalculateParsimonyScore3Levels()

