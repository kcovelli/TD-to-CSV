import random as r
import matplotlib.pyplot as plt
import threading
import cProfile, pstats


# create n*n matrix with random connections. if num_mastermind > 1, then there will be multiple rows with all 0s
# matrix[i][j] == 1 means i knows j
def make_matrix(num_mastermind, matrix, n, mastermind_index, num_checks):
    for i in range(n):
        s = bin(r.getrandbits(n))[2:0]
        s = '0' * (n - len(s)) + s
        arr = []  # 1 if x > i else 0 for x in range(n)]
        for digit in s:
            arr.append(1 if digit == '1' else 0)
        matrix.append(arr)

    # matrix = [[1 if digit=='1' else 0 for digit in bin(r.getrandbits(n))[2:]] for _ in range(n)]

    if num_mastermind is 1:
        for i, row in enumerate(matrix):
            row[mastermind_index] = 1
            row[i] = 0
        matrix[mastermind_index] = [0] * n

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
def find_mastermind(matrix, n, num_checks):
    candidates = list(range(n))
    for i in candidates:

        still_suspected = []
        prime_suspect = True

        for j in candidates:
            num_checks[0] += 1

            # if i knows j and j does not know i then j is safe
            if matrix[i][j] and not matrix[j][i]:
                still_suspected.append(j)
                prime_suspect = False

        # i didnt know any of the remaining suspects, so either i is the mastermind or there is no mastermind
        if prime_suspect:
            if check_mastermind(i, matrix, n):
                # print(f'{i} is the mastermind')
                return i
            else:
                # print('There is no mastermind')
                return -1

        candidates = still_suspected


def find_mastermind2(matrix, n, num_checks):
    i = 0
    j = 1

    while j < n:
        # if i knows j then i is not the mastermind, but j might be
        # if i does not know j then j is not the mastermind but i still might be
        # therefore at each iteration we eliminate one suspect as possibly being the mastermind
        if matrix[i][j]:
            i = j
        j += 1

    # check if i is the mastermind. return i if it is, -1 otherwise. When the loop ends, i will be the only suspect
    # who could possibly be the mastermind, but since we start iterating down the ith column partway through,
    # we havent nessisarily checked if every other suspect knows them, or if there is some suspect they know.
    # Checking this only takes O(n) time though so it's fine
    for j in range(n):
        if matrix[i][j] or (not matrix[j][i] and j != i):
            return -1
    return i


def run(num_checks, n):
    num_mastermind = r.randint(0, 1)

    if num_mastermind == 1:
        mastermind_index = r.randint(0, n - 1)
    else:
        mastermind_index = -1

    matrix = []
    make_matrix(num_mastermind, matrix, n, mastermind_index, num_checks)
    # print_matrix(matrix)
    # print(find_mastermind2(matrix, n, num_checks), mastermind_index)
    result = find_mastermind2(matrix, n, num_checks)
    # print(result, mastermind_index)
    if result == mastermind_index:
        pass  # print("Correct!!\n")
    else:
        print_matrix(matrix)
        assert False


num_threads = 4


def thread_function(checks, offset, max_n, step):
    run_many(10 + step * (offset + 1), max_n, step * num_threads, checks)


def run_many(start, stop, step, runtime_arr):
    for i in range(start, stop, step):
        num_checks = [0]
        run(num_checks, 10)
        runtime_arr.append((i, num_checks[0]))


def run_infinite(n):
    i = 0
    while True:
        i += 1
        run([], n)
        if i%50000 == 0:
            print(i)


thread_list = []
c = []

# run_many(10, 1000, 5, c)
run_infinite(5)

x_val = [i[0] for i in c]
y_val = [i[1] for i in c]
plt.plot(x_val, y_val)

'''
for i in range(num_threads):
    thread_list.append(threading.Thread(target=thread_function, args=(c, i)))
    thread_list[i].start()

for i in range(num_threads):
    thread_list[i].join()



'''
# thread_function(c, 0)
# num = [0]
# x_val = [i[0] for i in c]
# y_val = [i[1] for i in c]
# plt.plot(x_val, y_val)

# cProfile.run('run()', 'restats')
# p = pstats.Stats('restats').strip_dirs().sort_stats('ncalls')
# p.print_stats('csc263a5q3.py')
