#!/usr/bin/python3

import argparse
import os
import requests
import pdfkit
import datetime
import tempfile
from edgar import Company, Filing, set_identity

from sec_insights.utils.logger import configure_logger

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
    headers = {'User-Agent': user_agent}

    try:
        # Initialize company and get filings
        company = Company(ticker)
        filings = company.get_filings(form="8-K").latest(count)

        logger.info(f"Filings for Company = {filings.company_name}, CIK = {filings.cik}\n")

        for filing in filings:
            filing_details = Filing(
                company=filings.company_name,
                cik=filings.cik,
                form="8-K",
                filing_date=filing.filing_date,
                accession_no=filing.accession_no
            )
            attachments = filing_details.attachments
            exhibits = attachments.exhibits

            # Filter for specific document type
            results = exhibits.query("document_type in ['EX-99.1']")

            for result in results:
                logger.info(f"Filing Date: {filing.filing_date}, Document URL: {result.url}")
                try:
                    # Download the document
                    response = requests.get(result.url, headers=headers)
                    if response.status_code == 200:
                        # Use tempfile to manage temporary files
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".htm") as temp_html_file:
                            temp_html_file.write(response.text.encode('utf-8'))
                            temp_html_file_path = temp_html_file.name
                            pdf_filename = f"{ticker}_{str(filing.filing_date).replace('-', '')}.pdf"

                            logger.info(f"Converting {temp_html_file_path} to {pdf_filename}")

                            # Convert HTML to PDF
                            try:
                                pdfkit.from_file(temp_html_file_path, pdf_filename)
                                logger.info(f"Converted {temp_html_file_path} to {pdf_filename}")
                            except OSError as e:
                                logger.error(f"Error during conversion: {e}")
                            except Exception as e:
                                logger.error(f"Unexpected error during conversion: {e}")

                            # Clean up temporary HTML file
                            os.remove(temp_html_file_path)
                    else:
                        logger.error(f"Failed to download the document, status code: {response.status_code}")
                except Exception as e:
                    logger.error(f"Error while processing filing {filing.filing_date}: {e}")
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