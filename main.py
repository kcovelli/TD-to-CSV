from PIL import Image
import pytesseract
from datetime import datetime as dt
from pdf2image import convert_from_path
import os

pages = []

DIR_NAME = 'statements'

P0_ROW0_Y = 585
PN_ROW0_Y = 497
ROW_SECTION_X = (120, 375, 860)
ROW_SECTION_WIDTH = (135, 465, 110)
ROW_BORDER_SCAN_COL = 348
SCAN_STEP = 1
TABLE_END_SCAN_COL = 345

# pdfs = ['mar19', 'feb19', 'jan19', 'dec18']


def convert(pdf_file):
    """
        convert the given pdf file into images, and write the images to disk

        :param pdf_file path to the pdf file
        :return number of pages in the pdf
    """
    # Store images of all the pages of the PDF in global variable
    # TODO: wtf was i thinking fix this, return list of pages
    global pages
    pages = []

    # If images have already been created from previous execution, don't re convert
    i = 0
    if not os.path.isfile(pdf_file[:-4:] + "_0.png"):
        print("converting pdf to images.......")
        pages = convert_from_path(pdf_file)

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
    return ROW_SECTION_X[field], y0, ROW_SECTION_X[field] + ROW_SECTION_WIDTH[field], y1


def read_table(start_y, max_rows, p):

    actual_rows = -1
    y0 = start_y

    for r in range(max_rows):
        y1 = y0

        # figure out row height
        while pages[p].getpixel((ROW_BORDER_SCAN_COL, y1)) == (255, 255, 255) and y1 < 2199:
            y1 += SCAN_STEP

        if pages[p].getpixel((TABLE_END_SCAN_COL, y1)) == (0, 0, 0) or y1 == 5499:
            # then this is the last row on this page
            actual_rows = r + 1

        y1 -= SCAN_STEP

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
    while os.path.isfile(name + ' ' + str(i) + '.csv'):
        i += 1
    fp = open(name + ' ' + str(i) + '.csv', 'w')
    for r in data:
        fp.write(r[0].strftime('%b %d %y') + ',' + r[1] + (',-' if r[2] < 0 else ',') + '$' +
                 str(int(((r[2] // 100) ** 2) ** 0.5)) + '.' + str(r[2] % 100) + '\n')
    fp.close()


if __name__ == '__main__':

    file_names = os.listdir(DIR_NAME)

    imgs = []
    data = []
    for month in file_names:
        print(month, ".....")
        num_page = convert(DIR_NAME + '/' + month)

        for i in range(num_page):
            # 2nd and last page always have garbage on them
            if i != 1 and i != num_page - 1:
                read_table(P0_ROW0_Y if i == 0 else PN_ROW0_Y, 100, i)

    for row in imgs:
        date_str = pytesseract.image_to_string(row[0])
        desc = pytesseract.image_to_string(row[1])
        amnt_str = pytesseract.image_to_string(row[2])

        print(date_str, desc, amnt_str)

        # TODO: get year from (490, 358, 23, 19)

        try:
            date = dt.strptime(date_str + " 20", "%b %d %y")
        except ValueError:
            date = dt.strptime(date_str + " 20", "%b%d %y")

        amnt = int(amnt_str.replace('$', '').replace('.', ''))

        data.append((date, desc.replace('\n', ' ').replace(',', ' '), amnt))
        print(data[-1])

    data.sort()
    export()
