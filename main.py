from PIL import Image
import pytesseract
from datetime import datetime as dt
from pdf2image import convert_from_path
import os

pages = []

p0_row0_y = 1460
pn_row0_y = 1240
x = (310, 940, 2000)
w = (300, 1150, 430)

pdfs = ['aug', 'jul', 'jun', 'may', 'nov', 'oct', 'sep']


def convert(pdf_file):
    # Store images of all the pages of the PDF in global variable
    global pages
    pages = []

    # If images have already been created from previous execution, don't re convert
    i = 0
    if not os.path.isfile(pdf_file[:-4:] + "_0.png"):
        print("converting pdf to images.......")
        pages = convert_from_path(pdf_file, 500)

        # Iterate through all the pages stored above
        for page in pages:
            filename = pdf_file[:-4:] + "_" + str(i) + ".png"
            # Save the image of the page in system
            page.save(filename, 'PNG')
            i += 1

    else:
        while os.path.isfile(pdf_file[:-4:] + "_" + str(i) + ".png"):
            pages.append(Image.open(pdf_file[:-4:] + "_" + str(i) + ".png"))
            i += 1

    return i


def get_rect(field, y0, y1):
    return x[field], y0, x[field] + w[field], y1


def read_table(start_y, max_rows, p):
    actual_rows = -1
    y0 = start_y

    for r in range(max_rows):
        y1 = y0

        # figure out row height
        while pages[p].getpixel((927, y1)) == (255, 255, 255) and y1 < 5499:
            y1 += 1

        if pages[p].getpixel((920, y1)) == (0, 0, 0) or y1 == 5499:
            # then this is the last row on this page
            actual_rows = r + 1

        y1 -= 1

        row_imgs = list(pages[p].crop(get_rect(j, y0, y1)) for j in range(3))
        imgs.append(tuple(row_imgs))
        y0 = y1 + 6

        if actual_rows == r + 1:
            pt = pytesseract.image_to_string(row_imgs[1])
            if pt == 'NET AMOUNT OF MONTHLY\nACTIVITY' or pt == '':
                imgs.pop()
                actual_rows -= 1
            print(actual_rows)
            break


def pretty():
    s = ''
    for r in data:
        s += r[0].strftime('%b %d') + ': ' + r[1] + (' -' if r[2] < 0 else ' ') + \
             '$' + str(int(((r[2] // 100) ** 2) ** 0.5)) + '.' + str(r[2] % 100) + '\n'
    return s


def export(name='data'):
    i = 0
    while os.path.isfile(name+' '+str(i)+'.csv'):
        i+=1
    fp = open(name+' '+str(i)+'.csv', 'w')
    for r in data:
        fp.write(r[0].strftime('%b %d %y') + ',' + r[1] + (',-' if r[2] < 0 else ',') + '$' +
                 str(int(((r[2] // 100) ** 2) ** 0.5)) + '.' + str(r[2] % 100) + '\n')
    fp.close()


imgs = []
data = []
for month in pdfs:
    print(month, ".....", sep='')
    num_page = convert(month + '.pdf')

    for i in range(num_page):
        if i != 1 and i != num_page - 1:
            read_table(p0_row0_y if i == 0 else pn_row0_y, 100, i)

for row in imgs:
    date_str = pytesseract.image_to_string(row[0])
    desc = pytesseract.image_to_string(row[1])
    amnt_str = pytesseract.image_to_string(row[2])

    print(date_str, desc, amnt_str)

    date = dt.strptime(date_str + " 18", "%b %d %y")
    amnt = int(amnt_str.replace('$', '').replace('.', ''))

    data.append((date, desc.replace('\n', ' ').replace(',', ' '), amnt))
    print(data[-1])

data.sort()
export()
