from datetime import datetime as dt
# from typing import Dict, Tuple, List
import re
import os

RED = "\033[1;31m"
BLUE = "\033[1;34m"
PRUP = "\033[1;35m"
CYAN = "\033[1;36m"
YELLO = "\033[1;33m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"


def export(data, name='data'):
    i = 0
    while os.path.isfile(name + ' ' + str(i) + '.csv'):
        i += 1
    fp = open(name + ' ' + str(i) + '.csv', 'w')
    for r in data:
        a = [r[0].strftime('%b %d %y'), r[1], format_money(r[2]), format_money(r[3]) if len(r) > 3 else '',
             str(r[4]) if len(r) > 4 else '', str(r[5]) if len(r) > 5 else '']
        fp.write(','.join(a) + '\n')
    fp.close()


def imp(d, filename):
    with open(filename) as f:
        for line in f:
            r = line.split(',')
            date = dt.strptime(r[0], '%b %d %y')
            amnt = int(r[2].replace('$', '').replace('.', ''))

            d.append([date, r[1], amnt])
    return d


def reformat(filename='accountactivity.csv'):
    data = []
    with open(filename) as f:
        for line in f:
            r = line.split(',')
            if r[2] == '' or re.match('.*TFR-TO C/C', r[1]) is not None or r[1].startswith('TD MUTUAL FUNDS'):
                continue

            date = dt.strptime(r[0], "%m/%d/%Y")
            amnt = int(r[2].replace('.', ''))

            data.append((date, r[1], amnt))
    return data


def format_money(s: int):
    return ('-' if s < 0 else '') + '$' + str(int(((s // 100) ** 2) ** 0.5)) + '.' + (
        '00' if s % 100 == 0 else str(s % 100))


def pprint(*args):
    print(*args, RESET, sep='')


'''def print_transaction(data, i, dic):
    pprint(BLUE, dt.strftime(data[i][0], '%b %d %y'), '\t')  # print date
    pprint(BOLD, CYAN, data[i][1], '\t\t')  # print description
    pprint(BOLD, RED, format_money(data[i][2]))  # print amount
    print()
    if data[i][1] in dic:  # if this description has been seen before show average price and most common ratio
        arr = dic[data[i][1]]
        pprint(PRUP, 'Average is:\t', CYAN, format_money(arr[0]), '\t')
        common_ratio = max(arr[2], key=lambda x: x[1])
        pprint(YELLO, common_ratio[0], '\n')
'''


# noinspection PyShadowingNames
def print_transaction(trans, dic):
    pprint(BLUE, dt.strftime(trans[0], '%b %d %y'), '\t',  # date
           BOLD, CYAN, trans[1], '\t\t',  # description
           BOLD, RED, format_money(trans[2]))  # amount

    # if this description has been seen before show average price and most common ratio
    if trans[1] in dic:
        trans_info = dic[trans[1]]
        common_tup = find_common(trans_info[2])
        pprint(PRUP, BOLD, '\t\t\tAverage Price: ', CYAN, format_money(trans_info[0]), '\t\t',
               PRUP, 'Usual: ', YELLO, common_tup[0], ' ', common_tup[1])


# history = {index:(ratio, note) ...}
# return the most common ratio/note tuple
def find_common(history):
    d = {}
    for a in history.values():  # iterate over dict, store count for each unique (ratio, note) tuple in a dict
        d[a] = d[a] + 1 if a in d else 1

    m = -1
    for k in d.keys():  # find max of all unique (ratio, note) dict counts
        m = k if m == -1 or d[k] > d[m] else m

    return m


#   inputs:
#   '' - use default ratio for this description
#   '1' - ratio = 1
#   '5' - ratio = 0.5
#   '0' - ratio = 0
#   '0?\.\d' - ratio = 0.x
#   '[150]|(0?\.\d) .+' - add everything after the ratio to the transaction notes
#   'pause' - exit input loop, keep track of index we stopped at
#   'save' - exit input loop, write all data to csv
#   'skip' - skip current transaction
#   'back' - go back to last transaction
#   'history' - print history for current transaction

# stores all data from csv files
data = []

# stores results of input,
# dic[description][2] is history of all ratio/notes made at each index
# dic[description] = [  average_price, num, {index:(ratio, note) ...}  ]
dic = {}

# regexes to match commands
ratio_with_desc = r'([150]|(0?\.\d+))( .+)?'
command = r'^(pause|save|skip|back|history) *$'

big = re.compile(r'^$|' + ratio_with_desc + '|' + command)
rwd = re.compile(ratio_with_desc)
cmd = re.compile(command)

# do import
imp(data, 'data 0.csv')
imp(data, 'data 1.csv')

# main loop
loop_running = True
i = 0
while loop_running:
    row = data[i]  # current transaction
    print_transaction(row, dic)

    # get user input
    input_good = False
    while not input_good:
        s = input()
        input_good = bool(big.match(s))
        if input_good and s == '' and not row[1] in dic:
            pprint(BOLD, RED, "Don't have default for this description yet")
            input_good = False

    # noinspection PyUnboundLocalVariable
    if s == '' or rwd.match(s):  # if updating current transaction
        ratio = -1
        note = ''

        if s is not '':  # if not using defaults
            x = s.split(' ')
            ratio = float(x[0] if x[0] is not '5' else '0.5')
            note = x[1] if len(x) > 1 else ''

            if not row[1] in dic:  # if this description has not been seen before
                dic[row[1]] = [0, 0, {}]

        elif s == '' and row[1] in dic.keys():  # if using defaults
            common = find_common(dic[row[1]][2])  # find most common (ratio, note) pair
            ratio, note = common[0], common[1]
        else:
            assert False

        arr = dic[row[1]]
        arr[0] = int((arr[0] + row[2] * ratio) // (arr[1] + 1))  # adjust average price
        arr[1] += 1
        arr[2][i] = (ratio, note)

        row.extend([int(row[2] * ratio), ratio, note])

        i += 1
    elif cmd.match(s):
        if s == 'back':
            i -= 1
        elif s == 'skip':
            i += 1
        elif s == 'pause':

    else:
        assert False
