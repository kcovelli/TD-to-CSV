from datetime import datetime as dt
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
        fp.write(r[0].strftime('%b %d %y') + ',' + r[1] + (',-' if r[2] < 0 else ',') + '$' +
                 str(int(((r[2] // 100) ** 2) ** 0.5)) + '.' + str(r[2] % 100) + '\n')
    fp.close()


def imp(data, filename):
    with open(filename) as f:
        for line in f:
            r = line.split(',')
            date = dt.strptime(r[0], '%b %d %y')
            amnt = int(r[2].replace('$', '').replace('.', ''))

            data.append([date, r[1], amnt])
    return data


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
    return ('-' if s < 0 else '') + '$' + str(int(((s // 100) ** 2) ** 0.5)) + '.' + str(s % 100)

def pprint(*args):
    print(*args, end='', sep='')
    print(RESET, end='')


data = []
imp(data, 'data 0.csv')
imp(data, 'data 1.csv')

# stores results of input, dic[description] = [average_pay_ratio, average_price, num]
dic = {}

for row in data:
    pprint(BLUE, dt.strftime(row[0], '%b %d %y'), '\t')
    pprint(BOLD, CYAN, row[1], '\t\t')
    pprint(BOLD, RED, format_money(row[2]),'\n')
    if row[1] in dic:
        pprint(PRUP, 'Average is\t')
        pprint(CYAN, format_money(dic[row[1]][1]), '\t', YELLO, dic[row[1]][0])
    input_good = False
    while not input_good:
        s = input()

        ratio = 0
        if s == '':
            if row[1] in dic:
                dic[row[1]][2] += 1
                row.append(dic[row[1]][0])

