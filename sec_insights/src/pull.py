#!/usr/bin/python3

import argparse
import os
import requests
import pdfkit
import datetime
import json
import shutil
from edgar import Company, Filing, set_identity

from sec_insights.utils.constants import MASTER_CONFIG, ASSETS_DIR
from sec_insights.utils.logger import configure_logger

if not shutil.which("wkhtmltopdf"):
    print("wkhtmltopdf not found! Please install it.")
    exit(1)

logger = configure_logger(
    log_file_name="sec_pull_{}.log".format(
        datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ),
)

def process_filings(ticker, count, form="8-K"):
    """
    Fetch and process the latest SEC filings for a given company ticker.

    Args:
        ticker (str): The company's stock ticker symbol.
        count (int): Number of filings to process.
        form (str): Form type to process (default: "8-K").
    """
    logger.info(f"Processing filings for Ticker: {ticker}, Count: {count}, Form: {form}")

    # Set user-agent for requests
    user_agent = "Fintwit Developer (fintwit.dev@gmail.com)"
    set_identity("fintwit.dev@gmail.com")
    options = {'custom-header': [('User-Agent', user_agent)]}

    try:
        filings = Company(ticker).get_filings(form="8-K").latest(count)
        logger.info(f"Found filings for Company = {filings.company_name}, CIK = {filings.cik}\n")


        for filing in filings:
            filing_details = Filing(
                company=filings.company_name,
                cik=filings.cik,
                form="8-K",
                filing_date=filing.filing_date.strftime("%Y-%m-%d"),
                accession_no=filing.accession_no
            )
            results = filing_details.attachments.exhibits.query("document_type in ['EX-99.1', 'EX-99.01']")

            for result in results:
                filing_date_str = filing.filing_date.strftime("%Y-%m-%d")
                filing_dir = os.path.join(ASSETS_DIR, ticker, form, filing_date_str)
                pdf_filename = f"{ticker}_{filing_date_str.replace('-', '')}_{filing.accession_no}.pdf"
                pdf_path = os.path.join(filing_dir, pdf_filename)

                # Check if the PDF already exists
                if not os.path.exists(pdf_path):
                    # Create the directory if it does not exist
                    os.makedirs(filing_dir, exist_ok=True)
        
                    try:
                        logger.info(f"Fetching: {result.url} -> {pdf_filename}")
                        pdfkit.from_url(result.url, pdf_path, options=options)
                        logger.info(f"Successfully converted {result.url} -> {pdf_filename}")
                    except OSError as e:
                        logger.error(f"OS error while processing URL {result.url}: {e}")
                    except Exception as e:
                        logger.error(f"Unexpected error while processing URL {result.url}: {e}")
                else:
                    logger.info(f"Skipping already pulled filing: {pdf_filename}")
                    continue
    except Exception as e:
        logger.error(f"Error fetching filings for Ticker: {ticker}: {e}")

def process_all_tickers(count, form):
    """
    Process filings for all tickers listed in the master configuration file.

    Args:
        count (int): Number of filings to process per ticker.
        form (str): Form type to process.
    """
    if not os.path.exists(MASTER_CONFIG):
        logger.error(f"Master config file {MASTER_CONFIG} not found!")
        return

    with open(MASTER_CONFIG, "r") as config_file:
        tickers = json.load(config_file).get("tickers", [])

    if not tickers:
        logger.error("No tickers found in the configuration file.")
        return

    for ticker in tickers:
        process_filings(ticker, count, form)

def main():
    parser = argparse.ArgumentParser(description="Process SEC filings for given tickers.")
    parser.add_argument(
        "--ticker",
        type=str,
        nargs="?",
        default=None,
        help="Ticker for the company (optional if --all is used)."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process filings for all tickers in the configuration file."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=2,
        help="The number of items to process per ticker (must be >= 2)."
    )
    parser.add_argument(
        "--form",
        type=str,
        default="8-K",
        help="SEC form type to process (default: '8-K')."
    )

    args = parser.parse_args()

    if args.count < 2:
        parser.error("The number of items to process must be >= 2.")

    if args.all:
        logger.info(f"Processing filings for all tickers in the configuration file with form: {args.form}.")
        process_all_tickers(args.count, args.form)
    elif args.ticker:
        logger.info(f"Processing filings for single ticker: {args.ticker} with form: {args.form}.")
        process_filings(args.ticker, args.count, args.form)
    else:
        parser.error("You must specify either a ticker or use the --all flag.")

if __name__ == "__main__":
    main()
