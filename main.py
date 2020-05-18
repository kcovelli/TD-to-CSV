from PIL import Image
import pytesseract
from datetime import datetime as dt
from pdf2image import convert_from_path
import os

# directory to search for bank statement pdfs
DIR_NAME = 'statements'

# constants for determining pixel coordinates of statement info. Dependant on the resolution the PDFs are converted to.
P0_ROW0_Y = 585  # y value of first row of table on first page
PN_ROW0_Y = 497  # y value of first row of table on subsiquent page
ROW_SECTION_X = (120, 375, 860)  # x values of the entries on each row
ROW_SECTION_WIDTH = (135, 465, 110)  # width of each entry on each row
ROW_BORDER_SCAN_COL = 348  # which x-value to scan to find border between table rows
SCAN_STEP = 1  # how many pixels to skip when scanning for next row. Setting to >1 introduces risk of missing row border
TABLE_END_SCAN_COL = 345  # which x-value to scan to find end border of entire table


def convert(pdf_file, discard_second_and_last=False):
    """
        Convert the given pdf file into images, and write the images to disk

        :param pdf_file: path to the pdf file
        :param discard_second_and_last: whether to include the second page and
               last page in return list. In TD credit card statements these pages never contain any transactions,
               so no point in returning/storing them, but if this function is used for another application this may not
               be desierable
        :return list of images for each page in the pdf
    """
    return_arr = []
    # If images have already been created from previous execution, don't re-convert
    if not os.path.isfile(pdf_file[:-4:] + "_0.png"):
        print(f"converting {pdf_file} to images.......")
        all_page_imgs = convert_from_path(pdf_file)

        # Iterate through all the page images stored above
        img_name_num = 0
        for page_num, page_img in enumerate(all_page_imgs):

            # only store converted images to disk if we shouldnt discard the current page
            if not discard_second_and_last or (page_num != 1 and page_num != len(all_page_imgs) - 1):
                filename = pdf_file[:-4:] + "_" + str(img_name_num) + ".png"

                # Save the image of the page in system
                page_img.save(filename, 'PNG')
                return_arr.append(page_img)
                img_name_num += 1

    # pages are already on disk, read all converted images sequentially
    else:
        page_num = 0
        while os.path.isfile(pdf_file[:-4:] + "_" + str(page_num) + ".png"):
            return_arr.append(Image.open(pdf_file[:-4:] + "_" + str(page_num) + ".png"))
            page_num += 1

    return return_arr


def _get_rect(field, y0, y1):
    """
        Get the bounding box for the given field of the row between y0 and y1

        :param field: index of the table field to extract
        :param y0: y coordinate of the top of the bounding box
        :param y1: y coordinate of the top of the bounding box
        :return: (x0, y0, x1, y1) where (x0, y0) is the top left corner of the bounding box and (x1, y1)
                 is the bottom right
    """
    return ROW_SECTION_X[field], y0, ROW_SECTION_X[field] + ROW_SECTION_WIDTH[field], y1


def crop_page_img(page_img, start_y, max_rows):
    """
        Given a statement image, returns a list of tuples containing the images of each field of each row in the table on
        the given page

        :param page_img:
        :param start_y:
        :param max_rows:
        :return:
    """
    actual_rows = -1
    y0 = start_y

    imgs = []
    for r in range(max_rows):
        y1 = y0

        # figure out row height
        while page_img.getpixel((ROW_BORDER_SCAN_COL, y1)) == (255, 255, 255) and y1 < 2199:
            y1 += SCAN_STEP

        if page_img.getpixel((TABLE_END_SCAN_COL, y1)) == (0, 0, 0) or y1 == 5499:
            # then this is the last row on this page
            actual_rows = r + 1

        y1 -= SCAN_STEP

        row_imgs = list(page_img.crop(_get_rect(j, y0, y1)) for j in range(3))
        imgs.append(tuple(row_imgs))
        y0 = y1 + 6

        if actual_rows == r + 1:
            pt = pytesseract.image_to_string(row_imgs[1])
            if pt == 'NET AMOUNT OF MONTHLY\nACTIVITY' or pt == '':
                imgs.pop()
                actual_rows -= 1

            print(actual_rows)
            break
    return imgs


def export(data, name='data'):
    """
        Write the given transaction data to a CSV file

        :param data: Iterable containing the (datetime, string, int) triples for the transaction data
        :param name: name/path of the csv file to write.
    """
    i = 0
    while os.path.isfile(name + ' ' + str(i) + '.csv'):
        i += 1
    fp = open(name + ' ' + str(i) + '.csv', 'w')
    for r in data:
        fp.write(r[0].strftime('%b %d %y') + ',' + r[1] + (',-' if r[2] < 0 else ',') + '$' +
                 str(int(((r[2] // 100) ** 2) ** 0.5)) + '.' + str(r[2] % 100) + '\n')
    fp.close()


if __name__ == '__main__':

    all_files = os.listdir(DIR_NAME)

    transaction_list = []
    for file_name in all_files:

        # we only care about the pdf files in the directory
        if not file_name.endswith('.pdf'):
            continue

        print(file_name, ".....")

        # convert the pdf into images, and discard the 2nd and final pages which never contain transactions
        pages = convert(DIR_NAME + '/' + file_name, discard_second_and_last=True)

        # get date that statement was issued to find correct year for transactions
        statement_date_img = pages[0].crop((373, 353, 373 + 278, 353 + 32))  # only valid for this resolution
        statement_date_str = pytesseract.image_to_string(statement_date_img)
        statement_date = dt.strptime(statement_date_str, "%B %d, %Y")
        print(statement_date)

        # if statement was issued in January, then any transactions from December should be in the year before
        def get_year(d):
            return statement_date.year - 1 if (d.month is 12 and statement_date.month is 1) else statement_date.year

        # extract the image for each date, description, and amount of each transaction
        # file_row_imgs will be a list of tuples containing the image for each part of a transaction
        file_row_imgs = []
        for i, page in enumerate(pages):
            file_row_imgs.extend(crop_page_img(page, P0_ROW0_Y if i == 0 else PN_ROW0_Y, 100))

        # iterate over each transaction and use pytesseract to perform OCR
        for row in file_row_imgs:
            # extract date, description, and amount strings from image tuple
            date_str = pytesseract.image_to_string(row[0])
            desc = pytesseract.image_to_string(row[1])
            amnt_str = pytesseract.image_to_string(row[2])

            print(date_str, desc, amnt_str)

            # OCR sometimes doesn't put a space between the month and the day, so conversion may fail
            try:
                date = dt.strptime(date_str + ' 20', "%b %d %y")
            except ValueError:
                date = dt.strptime(date_str + ' 20', "%b%d %y")

            # figure out what year the transaction should have occured in and set the datetime object apropriately
            date.replace(year=get_year(date))
            # convert amount string to integer number of cents
            amnt = int(amnt_str.replace('$', '').replace('.', ''))
            # replace any newlines and commas so CSV doesn't get screwed up
            desc = desc.replace('\n', ' ').replace(',', ' ')

            # append transaction to overall transaction list
            transaction_list.append((date, desc, amnt))

    transaction_list.sort()
    export(transaction_list)
