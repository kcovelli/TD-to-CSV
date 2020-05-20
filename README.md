# TD-to-CSV

TD bank doesn't let you export credit card transactions as a CSV, only as PDFs with unselectable text, and only one PDF 
for each month at that. This program uses OCR to convert the transaction PDFs to CSVs.

# Usage

1) clone the repo
2) Go to https://easyweb.td.com/ and login
3) Go to Accounts > Statements and Documents and select your account from the "Get statements by account" dropdown. 
   - Note this program only works for credit card accounts as the statements for other accounts are formatted 
   differently (also other kinds of accounts let you download a CSV directly for some reason)
4) Download all the PDFs to a folder called `statements` in the root directory of the repo
5) run `td_to_csv.py`

The CSVs will be saved in a file called `data 0.csv` by default (incrementing the number on subsequent executions). Change
 the constants `DIR_NAME` or `CSV_NAME` in `td_to_csv.py` to change the directory to put PDFs, or default CSV file name 
 respectively. 
