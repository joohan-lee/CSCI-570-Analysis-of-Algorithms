import os
import sys
#from resource import *
import time
import psutil

##################### Cost #####################
# mismatch cost
MISMATCH = [
    [0, 110, 48, 94],
    [110, 0, 118, 48],
    [48, 118, 0, 110],
    [94, 48, 110, 0]
]

INDEX = {"A": 0, "C": 1, "G": 2, "T": 3}
# gap cost
GAP = 30


def generate_string(fullpath):
    # input: fullpath of input file(string)
    # output: [generated string0, generated string1]

    #################### Read file and Generate two strings ###################
    with open(fullpath, 'r') as f:
        lines = f.readlines()
        seq = ""
        arr_seq = []
        for line in lines:
            line = line.strip()  # remove '\n'
            if line.isalpha():
                if seq != "":
                    arr_seq.append(seq)
                seq = line
            elif line.isnumeric():
                idx = int(line)
                seq = seq[0:idx+1] + seq + seq[idx+1:]
        arr_seq.append(seq)
    f.close()
    return arr_seq


def basic(X, Y):
    ########### Bottom-up (Get the value of optimal solution) ##########
    # OPT[i][j] denotes the minimum cost of an alignment between {x_1x_2...x_i} and {y_1y_2...y_j}.
    # Initialize opt
    m = len(X)  # the length of sequence 0
    n = len(Y)  # the length of sequence 1

    opt = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize column 0 & row 0 to i*GAP
    opt[0][:] = [i * GAP for i in range(n + 1)]
    for i in range(m + 1):
        opt[i][0] = i * GAP

    # Get the value of optimal solution
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            opt[i][j] = min(MISMATCH[INDEX[X[i-1]]][INDEX[Y[j - 1]]] + opt[i - 1][j - 1],
                            GAP + opt[i - 1][j],
                            GAP + opt[i][j - 1])

    ############# Top-down (Get the optimal solution) ###################
    opt_seq0 = ""
    opt_seq1 = ""

    i, j = m, n

    while i > 0 and j > 0:
        if opt[i][j] == MISMATCH[INDEX[X[i-1]]][INDEX[Y[j - 1]]]+opt[i - 1][j - 1]:
            opt_seq0 = X[i - 1] + opt_seq0
            opt_seq1 = Y[j - 1] + opt_seq1
            i -= 1
            j -= 1
        elif opt[i][j] == GAP + opt[i][j - 1]:
            opt_seq0 = "_" + opt_seq0
            opt_seq1 = Y[j - 1] + opt_seq1
            j -= 1
        elif opt[i][j] == GAP+opt[i - 1][j]:
            opt_seq0 = X[i - 1] + opt_seq0
            opt_seq1 = "_" + opt_seq1
            i -= 1

    while i > 0:
        opt_seq0 = X[i - 1] + opt_seq0
        opt_seq1 = "_" + opt_seq1
        i -= 1
    while j > 0:
        opt_seq0 = "_" + opt_seq0
        opt_seq1 = Y[j - 1] + opt_seq1
        j -= 1

    return [opt_seq0, opt_seq1, opt[m][n]]


def make_alignment(X, Y, direction):
    m = len(X)  # the length of sequence 0
    n = len(Y)  # the length of sequence 1

    opt = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize column 0 & row 0 to i*GAP
    opt[0][:] = [i*GAP for i in range(n + 1)]
    for i in range(m + 1):
        opt[i][0] = i*GAP

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if direction == 0:  # forward
                opt[i][j] = min(MISMATCH[INDEX[X[i - 1]]][INDEX[Y[j - 1]]] + opt[i - 1][j - 1],
                                GAP + opt[i - 1][j],
                                GAP + opt[i][j - 1])
            else:  # backward
                opt[i][j] = min(MISMATCH[INDEX[X[m - i]]][INDEX[Y[n - j]]] + opt[i - 1][j - 1],
                                GAP + opt[i - 1][j],
                                GAP + opt[i][j - 1])
    return opt[m]


def efficient_dp(X, Y):
    m = len(X)  # the length of sequence 0
    n = len(Y)  # the length of sequence 1

    if m < 3 or n < 3:
        return basic(X, Y)

    # make new alignments with half of the first string and the entire second string
    forward = make_alignment(X[:int(m/2)], Y, direction=0)
    backward = make_alignment(X[int(m/2):], Y, direction=1)

    # combine forward and backward list
    combine = []
    for i in range(n + 1):
        combine.append(forward[i] + backward[n - i])

    # find the split point that makes the cost the smallest
    idx = combine.index(min(combine))
    left = efficient_dp(X[:int(m/2)], Y[:idx])
    right = efficient_dp(X[int(m/2):], Y[idx:])

    result = []
    for l, r in zip(left, right):
        result.append(l + r)

    return result


def main():

    ############ Generate two sequences from input txt file#############
    fullpath_in = os.path.join(os.getcwd(), file_in)
    arr_seq = generate_string(fullpath_in)

    ############### Start time #########################################
    start_time = time.time()

    X_alignment, Y_alignment, cost = efficient_dp(arr_seq[0], arr_seq[1])

    end_time = time.time()
    time_taken = (end_time - start_time)*1000

    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss/1024)

    #################### Write output txt file ############################
    fullpath_out = os.path.join(
        os.getcwd(), file_out)
    with open(fullpath_out, 'w+') as f:
        # the minimum cost of alignment(the value of optimal solution)
        f.write(str(cost))
        f.write('\n')
        # optimal sequence0
        f.write(str(X_alignment))
        f.write('\n')
        # optimal sequence1
        f.write(str(Y_alignment))
        f.write('\n')
        # time (ms)
        f.write(str(time_taken))
        f.write('\n')
        # memory(KB)
        f.write(str(memory_consumed))
    f.close()


if __name__ == "__main__":
    file_in = sys.argv[1]
    file_out = sys.argv[2]
    main()
