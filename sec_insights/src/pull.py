#!/usr/bin/python3

import argparse
import os
import requests
import pdfkit
import datetime
import shutil
from edgar import Company, Filing, set_identity

from sec_insights.utils.logger import configure_logger

if not shutil.which("wkhtmltopdf"):
    print("wkhtmltopdf not found! Please install it.")
    exit(1)

logger = configure_logger(
    log_file_name="sec_pull_{}.log".format(
        datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ),
)

def process_filings(ticker, count):
    """
    Fetch and process the latest SEC filings for a given company ticker.

    Args:
        ticker (str): The company's stock ticker symbol.
        count (int): Number of filings to process.
    """
    logger.info(f"Processing filings for Ticker: {ticker} with count: {count}")

    # Set user-agent for requests
    user_agent = "Fintwit Developer (fintwit.dev@gmail.com)"
    set_identity("fintwit.dev@gmail.com")
    options = { 'custom-header': [('User-Agent', user_agent)] }

    try:
        filings = Company(ticker).get_filings(form="8-K").latest(count)
        logger.info(f"Filings for Company = {filings.company_name}, CIK = {filings.cik}\n")

        for filing in filings:
            filing_details = Filing(
                company=filings.company_name,
                cik=filings.cik,
                form="8-K",
                filing_date=filing.filing_date,
                accession_no=filing.accession_no
            )
            results = filing_details.attachments.exhibits.query("document_type in ['EX-99.1', 'EX-99.01']")

            for result in results:
                pdf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "filings", ticker))
                os.makedirs(pdf_dir, exist_ok=True)
                pdf_filename = f"{ticker}_{str(filing.filing_date).replace('-', '')}.pdf"
    
                try:
                    logger.info(f"Fetching: {result.url} -> {pdf_filename}")
                    pdfkit.from_url(result.url, os.path.join(pdf_dir, pdf_filename), options=options)
                    logger.info(f"Successfully converted {result.url} -> {pdf_filename}")
                except OSError as e:
                    logger.error(f"OS error while processing URL {result.url}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error while processing URL {result.url}: {e}")
    except Exception as e:
        logger.error(f"Error fetching filings for Ticker: {ticker}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Process SEC filings for a given company.")
    parser.add_argument(
        "ticker",
        type=str,
        help="Ticker for the company"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=2,
        help="The number of items to process (must be >= 2)"
    )

    args = parser.parse_args()

    if args.count < 2:
        parser.error("The number of items to process must be >= 2")

    print(f"Processing filings for ticker: {args.ticker}, Count: {args.count}")
    process_filings(args.ticker, args.count)


if __name__ == "__main__":
    main()