import random
def neighborhood(coordPivot = [0, 1, 0, 1, 0, 1, 0]):
    thisCmd = "B.coord.neighborhood"
    ABOUT = "\n".join("This command {} takes a binary coordinate such as 0101010 (here of",
                       "size L = 7) and returns a set of all ** adjacent coordinates **, i.e. the",
                       "coordinates with the Hamming distance of 1 from the input coordinate.",
                       "The size of this set is L.").format(thisCmd)
                       
    if coordPivot == "?":
        print("Valid query is '" + thisCmd + " ??'")
        return
                           
    if coordPivot == "??":
        print ABOUT
        return
                       
    L = len(coordPivot)
    coordNeighbors = []

    for i in range(L):
        bit = coordPivot[i]
        if bit:
            coordPivot[i] = 0
        else:
            coordPivot[i] = 1
        coordAdj = str(coordPivot)
        coordNeighbors.append(coordAdj)

    print("coordPivot\n" + coordPivot + "\ncoordNeighbors\n" + coordNeighbors)
    return coordNeighbors

def distance(bstrL = [0, 1, 0, 1], bstrR = [1, 0, 0, 1]):
    thisCmd = "B.coord.distance"
    ABOUT = """This procedure takes two binary strings and returns
        the value of the Hamming distance between the strings.
        """
    if bstrL == "?":
        print("Valid query is '" + thisCmd + " ??'")
        return

    if bstrL == "??":
        print ABOUT
        return
    
    L = len(bstrL)
    dist = 0
    if L != len(bstrR):
        print("ERROR ... unequal length strings: " + str(len(bstrL)) + " vs " + str(len(bstrR)))
        return
    for j in range(L):
        bL = bstrL[j]
        bR = bstrR[j]
        if bL != bR:
            dist += 1
    return dist    

def from_int(val = 31, maxBits = 5):
    thisCmd = "B.coord.from_int"
    ABOUT = """This procedure takes an integer and the length of the binary string that
        can represent this integer and returns a binary string that actually
        represents this integer.
        """
    
    if val == "?":
        print("Valid query is '" + thisCmd + " ??'")
        return

    if val == "??":
        print ABOUT
        return
    
    intMax = int(pow(2, maxBits)) - 1
    bstr = []
    if val > intMax:
        print("\nERROR from {} ..."
          "maxBits={} cannot represent an integer={} \n").format(thisCmd, maxBits, val)
    elif val < 0:
        print("\nERROR from {} ... negative input value, val = {} \n").format(thisCmd, val)
    elif val > 0:
        nBits = int(log(val, 2.0))
        remainder = val
        for i in range(int(nBits), -1, -1):
            base = pow(2, i)
            quotient = remainder/base
            remainder = remainder % int(base)
            bstr.append(quotient)

    numZeros = maxBits - len(bstr)

    zeros = []
    for i in range(numZeros):
        zeros.append(0)

    return zeros + bstr

def rand(L = 41, weightFactor = None):
    thisCmd = "B.coord.rand"
    ABOUT = """This proc takes an integer L, and optionally a weightFactor > 0 and <= 1.
        By default, weightFactor = NA, and an unbiased binary coordinate of length L
        is returned. For weightFactor=0.5, a biased random coordinate of length L
        is returned: it will have  a random distribution of exactly L/2 'ones'
        for L even and (L+1)/2 'ones' for L odd.
        """
    
    if L == "?":
        print("Valid query is '" + thisCmd + " ??'")
        return

    if L == "??":
        print ABOUT
        return
    
    coord = []
    if weightFactor == None:
        for i in range(L):
            coord.append(int(.5 + random.random()))
    return coord

def rank(bstr = "0001101"):
    thisCmd = "B.coord.rank"
    ABOUT = """This proc takes a binary coordinate as a string such as '010101' and
        returns its weight number as the number of 'ones', which can also be
        interpreted as the distance from '000000' or as 'the rank' of the
        coordinate in the Hasse graph with respect to its 'bottom' coordinate
        of all 'zeros'.
        """
    
    if bstr == "?":
        print("Valid query is '" + thisCmd + " ??'")
        return

    if bstr == "??":
        print ABOUT
        return

    return bstr.count(1)