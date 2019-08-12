from datetime import datetime as dt
# from typing import Dict, Tuple, List
import re
import os

RED = "\033[0;31m"
BLUE = "\033[0;34m"
PRUP = "\033[0;35m"
CYAN = "\033[0;36m"
YELLO = "\033[0;33m"
GREEN = "\033[0;32m"
WHITE = '\033[0;37m"'
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"

GAP = 45


# export the given array to a csv file
def export(_data, name='data'):
    if os.path.isfile(name + '.csv'):
        i = 0
        while os.path.isfile(name + ' ' + str(i) + '.csv'):
            i += 1
        name = name + ' ' + str(i)

    fp = open(name + '.csv', 'w')
    for r in _data:  # write data to file
        a = [r[0].strftime('%b %d %y'), r[1], format_money(r[2]), format_money(r[3]) if len(r) > 3 else '',
             str(r[4]) if len(r) > 4 else '', str(r[5]) if len(r) > 5 else '']
        fp.write(','.join(a) + '\n')
    fp.close()


def imp(d, _dic, filename):
    with open(filename) as f:
        for i, line in enumerate(f):
            r = line.split(',')
            date = dt.strptime(r[0], '%b %d %y')
            base_amnt = int(r[2].replace('$', '').replace('.', ''))

            # if we have saved data from previous execution, update dict and d
            extra_arr = []
            if len(r) > 3 and r[3] is not '' and r[4] is not '':
                extra_arr.append(int(r[3].replace('$', '').replace('.', '')))
                extra_arr.append(float(r[4]))
                extra_arr.append(r[5].replace('\n', ''))

                if not r[1] in _dic:  # if this description has not been seen before
                    _dic[r[1]] = [0, 0, {}]

                hist = _dic[r[1]]
                hist[0] = int((hist[0] * hist[1] + base_amnt) // (hist[1] + 1))  # adjust average price
                hist[1] += 1
                hist[2][i] = (extra_arr[1], extra_arr[2])

            arr = [date, r[1], base_amnt]
            arr.extend(extra_arr)
            d.append(arr)
    return d


def reformat(filename='accountactivity.csv'):
    _data = []
    with open(filename) as f:
        for line in f:
            r = line.split(',')
            if r[2] == '' or re.match('.*TFR-TO C/C', r[1]) is not None or r[1].startswith('TD MUTUAL FUNDS'):
                continue

            date = dt.strptime(r[0], "%m/%d/%Y")
            amnt = int(r[2].replace('.', ''))

            _data.append((date, r[1], amnt))
    return _data


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
def print_transaction(trans, _dic):
    blank = GAP - len(trans[1])
    pprint(BLUE, dt.strftime(trans[0], '%b %d %y'), '\t',  # date
           BOLD, CYAN, trans[1], '.' * blank,  # description
           BOLD, RED, format_money(trans[2]))  # amount

    # if this description has been seen before show average price and most common ratio
    if trans[1] in _dic:
        trans_info = _dic[trans[1]]
        common_tup = find_common(trans_info[2])
        pprint(PRUP, BOLD, '\t\t\tAverage Price: ', YELLO, format_money(trans_info[0]), '\t\t',
               BOLD, PRUP, 'Usual: ', RESET, YELLO, common_tup[0], ' ', common_tup[1])


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
def start(_data, _dic, index=0):
    # main loop
    loop_running = True
    i = index
    while loop_running:
        row = _data[i]  # current transaction
        print_transaction(row, _dic)

        # get user input
        input_good = False
        while not input_good:
            s = input()
            input_good = bool(big.match(s))
            if not input_good:
                pprint(BOLD, RED, "Bad input")
            elif input_good and s == '' and not row[1] in _dic:
                pprint(BOLD, RED, "Don't have default for this description yet")
                input_good = False

        # noinspection PyUnboundLocalVariable
        if s == '' or rwd.match(s):  # if updating current transaction
            if s is not '':  # if not using defaults
                x = s.split(' ')
                ratio = float(x[0] if x[0] is not '5' else '0.5')
                note = x[1] if len(x) > 1 else ''

                if not row[1] in _dic:  # if this description has not been seen before
                    _dic[row[1]] = [0, 0, {}]

            elif s == '' and row[1] in _dic.keys():  # if using defaults
                if i in _dic[row[1]][2].keys():
                    i += 1
                    continue
                common = find_common(_dic[row[1]][2])  # find most common (ratio, note) pair
                ratio, note = common[0], common[1]
            else:
                assert False

            arr = _dic[row[1]]
            arr[0] = int((arr[0] * arr[1] + row[2]) // (arr[1] + 1))  # adjust average price
            arr[1] += 1
            arr[2][i] = (ratio, note)

            if len(row) == 3:
                row.extend([int(row[2] * ratio), ratio, note])
            elif len(row) == 6:
                row[3:7] = [int(row[2] * ratio), ratio, note]
            else:
                assert False

            i += 1
        elif cmd.match(s):
            if s == 'back':
                i -= 1
            elif s == 'skip':
                i += 1
            elif s.startswith('goto'):
                x = s.split(' ')
                i = int(x[1])
            elif s == 'pause':
                print(i)
                return i
            elif s == 'history':
                if row[1] in _dic:
                    for h in _dic[row[1]][2].keys():
                        trans = _data[h]
                        pprint(BLUE, dt.strftime(trans[0], '%b %d %y'), '\t',  # date
                               BOLD, RED, format_money(trans[2]), '\t',  # amount
                               YELLO, _dic[row[1]][2][h][0], '  ',  # ratio
                               YELLO, _dic[row[1]][2][h][1], '\n\n')  # note
                    else:
                        pprint(BOLD, RED, 'No history yet')
            elif s == 'save':
                # filename = 'data_' + dt.now().strftime('%b%m_%I-%M-%S%p')
                filename = 'last_' + str(i)
                export(_data, filename)

        else:
            assert False


def resume():
    global data, dic, end
    start(data, dic, end)


# stores all data from csv files
data = []

# stores results of input,
# dic[description][2] is history of all ratio/notes made at each index
# dic[description] = [  average_price, num, {index:(ratio, note) ...}  ]
dic = {}

# regexes to match commands
ratio_with_desc = r'^([150]|(0?\.\d+))( .+)?$'
command = r'^(pause|save|skip|back|history|goto \d+) *$'

big = re.compile(r'^$|' + ratio_with_desc + '|' + command)
rwd = re.compile(ratio_with_desc)
cmd = re.compile(command)

# do import
# check if there is a saved "last" file
last_arr = [int(x[5:-4]) for x in os.listdir() if len(x) >= 10 and re.match(r'last_\d+\.csv', x)]
if len(last_arr) > 0:
    index = max(last_arr)
    imp(data, dic, f'last_{index}.csv')
else:
    index = 0
    imp(data, dic, 'master.csv')
data.sort()
end = start(data, dic, index)
