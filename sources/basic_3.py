import os
import sys
#from resource import *
import time
import psutil


data_folder = 'datapoints'

##################### Cost #####################
# mismatch cost
MISMATCH = [[0, 110, 48, 94],
            [110, 0, 118, 48],
            [48, 118, 0, 110],
            [94, 48, 110, 0]]

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


def main():
    ############ Generate two sequences from input txt file#############
    fullpath_in = os.path.join(os.getcwd(), file_in)
    # fullpath_in = file_in
    arr_seq = generate_string(fullpath_in)

    start_time = time.time()

    ########### Bottom-up (Get the value of optimal solution) ##########
    # OPT[i][j] denotes the minimum cost of an alignment between {x_1x_2...x_i} and {y_1y_2...y_j}.
    # Initialize opt
    m = len(arr_seq[0])  # the length of sequence 0
    n = len(arr_seq[1])  # the length of sequence 1

    opt = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize column 0 & row 0 to i*GAP
    opt[0][:] = [i*GAP for i in range(n + 1)]
    for i in range(m + 1):
        opt[i][0] = i*GAP

    # Get the value of optimal solution
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            opt[i][j] = min(MISMATCH[INDEX[arr_seq[0][i-1]]][INDEX[arr_seq[1][j-1]]]+opt[i-1][j-1],
                            GAP+opt[i-1][j], GAP + opt[i][j-1]
                            )

    ############# Top-down (Get the optimal solution) ###################
    opt_seq0 = ""
    opt_seq1 = ""

    i, j = m, n

    while i > 0 and j > 0:
        if opt[i][j] == MISMATCH[INDEX[arr_seq[0][i-1]]][INDEX[arr_seq[1][j-1]]]+opt[i-1][j-1]:
            opt_seq0 = arr_seq[0][i-1] + opt_seq0
            opt_seq1 = arr_seq[1][j-1] + opt_seq1
            i -= 1
            j -= 1
        elif opt[i][j] == GAP+opt[i][j-1]:
            opt_seq0 = "_" + opt_seq0
            opt_seq1 = arr_seq[1][j-1] + opt_seq1
            j -= 1
        elif opt[i][j] == GAP+opt[i-1][j]:
            opt_seq0 = arr_seq[0][i-1] + opt_seq0
            opt_seq1 = "_" + opt_seq1
            i -= 1

    while i > 0:
        opt_seq0 = arr_seq[0][i-1] + opt_seq0
        opt_seq1 = "_" + opt_seq1
        i -= 1
    while j > 0:
        opt_seq0 = "_" + opt_seq0
        opt_seq1 = arr_seq[1][j-1] + opt_seq1
        j -= 1

    end_time = time.time()
    time_taken = (end_time - start_time)*1000

    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss/1024)

    #################### Write output txt file ############################
    fullpath_out = os.path.join(
        os.getcwd(), file_out)
    #fullpath_out = file_out
    with open(fullpath_out, 'w+') as f:
        # the minimum cost of alignment(the value of optimal solution)
        f.write(str(opt[m][n]))
        f.write('\n')
        # optimal sequence0
        f.write(opt_seq0)
        f.write('\n')
        # optimal sequence1
        f.write(opt_seq1)
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
