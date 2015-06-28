import random
def neighborhood(coordPivot = [0, 1, 0, 1, 0, 1, 0]):
    ABOUT = "\n".join(["This proc takes a binary coordinate such as 0101010",
                       "(here of size L = 7) and returns a set of distance=1 neighborhood",
                       "coordinates (aka as the Hamming distance of 1). The size of this set is L.",
                       "See the example below."])
    thisProc = "B_coord.neighborhood"
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
    thisProc = "B.coord.distance"
    if bstrL == "?":
        print("Valid query is '" + thisProc + " ??'")
        return

    if bstrL == "??":
        print("\n".join(["This procedure takes two binary strings and returns",
                         "the value of the Hamming distance between the strings."]))
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
    intMax = int(pow(2, maxBits)) - 1
    bstr = []
    if val > intMax:
        print("\nERROR from $thisProc ...\
          maxBits=$maxBits cannot represent an integer=$val \n")
    elif val < 0:
        print("\nERROR from $thisProc ... negative input value, val = $val \n")
    elif val > 0:
        nBits = int(log(val, 2.0))
        remainder = val
        #print(str(int(nBits)))
        for i in range(int(nBits), -1, -1):
            base = pow(2, i)
            quotient = remainder/base
            remainder = remainder % int(base)
            bstr.append(quotient)
   # print(str(bstr))
#    else:
 #        bstr.append(0)
    #print(str(bstr))
    numZeros = maxBits - len(bstr)
    #print("maxBits: " + str(maxBits) + " len(str(bstr)): " + str(len(str(bstr))) + " numZeros: " + str(numZeros))
    zeros = []
    for i in range(numZeros):
        zeros.append(0)
    #zeros.append(bstr)
    #bstr = zeros
#    print("bstr: " + str(bstr))
    return zeros + bstr
def rand(L = 41, weightFactor = None):
    coord = []
    if weightFactor == None:
        for i in range(L):
            coord.append(int(.5 + random.random()))
    return coord

def rank(bstr = [0, 0, 0, 1, 1, 0, 1]):
    return bstr.count(1)