from itertools import permutations
import numpy as np

def load_permulst(numTasks):
    permulst = np.loadtxt("data/permu{}.csv".format(numTasks), dtype=np.int8 , delimiter=',')
    return permulst 

def generate_permulst( ni, nj):
    for n in range (ni, nj+1):
        perm = permutations([a for a in range (0,n)])
        print(perm)
        p = np.array([a for a in perm], dtype=np.int8)
        fname = "data/permu{}.csv".format(n)
        np.savetxt(fname, p, fmt='%i', delimiter=",")


#For Testing Purpose
if __name__ == "__main__":    
    import os, sys
    sys.path.append(os.getcwd())
    print(os.getcwd(), sys.path)
    import time
    # generate_permulst(4,4)
    generate_permulst(12,20)
