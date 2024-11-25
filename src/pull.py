#!/usr/bin/python3

import argparse
import sys
import os
import requests
import pdfkit
from edgar import *

parser = argparse.ArgumentParser(description="Process some arguments.")

parser.add_argument(
    "ticker", 
    type=str, 
    help="Ticker for the company"
)

parser.add_argument(
    "--count", 
    type=int, 
    default=2, 
    help="The number of items to process (>2)"
)


args = parser.parse_args()

print(f"Ticker: {args.ticker}")
print(f"Count: {args.count}")

if args.count < 2:
   parser.error("# of items to process must be > 2")

set_identity("fintwit.dev@gmail.com")
user_agent = "Fintwit Developer (fintwit.dev@gmail.com)"
headers = { 'User-Agent': user_agent }
cheader = { 'custom-header': [('User-Agent', user_agent)], }

ticker = args.ticker
c = Company(ticker)
filings = c.get_filings(form="8-K").latest(args.count)
#print(filings.company_name, filings.cik)
filings

print("Filings for Company = ",filings.company_name,"CIK = ",filings.cik,"\n")
for f in filings:
    #print("Filing Date = ",f.filing_date, "Accession_No = ",f.accession_no)
    filing = Filing(company=filings.company_name, cik=filings.cik, form='8-K', filing_date=f.filing_date, accession_no=f.accession_no)
    attachments = filing.attachments
    exhibits = attachments.exhibits
    #print(exhibits)
    results = exhibits.query("document_type in ['EX-99.1', 'EX-99.01']")
    for r in results:
       fname = ticker + "_" + str(f.filing_date) + ".pdf"
       try:
          print("Fetching",r.url, fname)
          pdfkit.from_url(r.url, fname, options=cheader)
       except OSError as e:
          print("Encountered error in Fetching", r.url)
       except Exception as e:
          print("Encountered an exception in Fetching", r.url)
