import random as r
import matplotlib.pyplot as plt
import threading
import cProfile, pstats


# create n*n matrix with random connections. if num_mastermind > 1, then there will be multiple rows with all 0s
# matrix[i][j] == 1 means i knows j
def make_matrix(num_mastermind, matrix, n, mastermind_index, num_checks):

    for _ in range(n):
        s = bin(r.getrandbits(n))[2:0]
        s = '0'*(n-len(s))+s
        arr = []
        for digit in s:
            num_checks[0] += 1
            arr.append(1 if digit=='1' else 0)
        matrix.append(arr)

    #matrix = [[1 if digit=='1' else 0 for digit in bin(r.getrandbits(n))[2:]] for _ in range(n)]

    if num_mastermind is 1:
        for i, row in enumerate(matrix):
            row[mastermind_index] = 1
            row[i] = 0
        matrix[mastermind_index] = [0]*n

    elif num_mastermind > 1:
        fake_masterminds = r.sample(range(n), num_mastermind)
        for x in fake_masterminds:
            for i, row in enumerate(matrix):
                row[x] = 1 if i not in fake_masterminds else 0
                row[i] = 0
            matrix[x] = [0] * n

# print the matrix
def print_matrix(matrix):
    for row in matrix:
        print(row)
    print()

# check if the given suspect is the mastermind
# i.e if the suspect knows anyone, or anyone does not know the suspect
def check_mastermind(suspect, matrix, n):
    for j in range(n):
        # if the suspect knows j, or j does not know the suspect
        if matrix[suspect][j] or (not matrix[j][suspect] and j != suspect):
            return False

    return True

# find and return the index of the mastermind. return -1 if there is none
def find_mastermind(matrix, n):
    candidates = list(range(n))
    for i in candidates:

        still_suspected = []
        prime_suspect = True

        for j in candidates:
            # if i knows j and j does not know i then j is safe
            if matrix[i][j] and not matrix[j][i]:
                still_suspected.append(j)
                prime_suspect = False

        # i didnt know any of the remaining suspects, so either i is the mastermind or there is no mastermind
        if prime_suspect:
            if check_mastermind(i, matrix, n):
                #print(f'{i} is the mastermind')
                return i
            else:
                #print('There is no mastermind')
                return -1

        candidates = still_suspected


def run(num_checks, n):

    num_mastermind = r.randint(0,1)

    if num_mastermind == 1:
        mastermind_index = n-1#.randint(0, n - 1)
    else:
        mastermind_index = -1

    matrix = []
    make_matrix(num_mastermind, matrix, n, mastermind_index, num_checks)
    #print_matrix()
    if find_mastermind(matrix, n) == mastermind_index :
        pass # print("Correct!!\n")
    else:
        assert False

step = 20
max = 2000
num_threads = 4

def thread_function(checks, offset):

    for i in range(10*(offset+1), max, step*num_threads):
        num_checks = [0]
        n = i
        print(f'Thread #{offset}, n={n}')
        run(num_checks, n)
        checks.append((n, num_checks[0]))
        #
        # if i % 500 == 0:
        #     x_val = list(range(10, i+1, step))
        #     plt.plot(x_val, checks)
        #     plt.show()

thread_list = []
c = []

for i in range(num_threads):
    thread_list.append(threading.Thread(target=thread_function, args=(c, i)))
    thread_list[i].start()

for i in range(num_threads):
    thread_list[i].join()


x_val = [i[0] for i in c]
y_val = [i[1] for i in c]
plt.plot(x_val, y_val)

# cProfile.run('run()', 'restats')
# p = pstats.Stats('restats').strip_dirs().sort_stats('ncalls')
# p.print_stats('csc263a5q3.py')