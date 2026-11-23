#!/usr/bin/env python3

import argparse
import os
import sys

from config import ConfigManager
from search import SearchEngine
from pdf_generator import PDFGenerator
from pdf_merger import PDFMerger
from logger import setup_logging, get_app_logger
import json

def main():
    parser = argparse.ArgumentParser(description="ExamTopics PDF Scraper")

    parser.add_argument("--exam", required=True, help="Exam code (e.g., saa-c03)")
    parser.add_argument(
        "--begin", type=int, required=True, help="Beginning question number"
    )
    parser.add_argument("--end", type=int, required=True, help="Ending question number")
    parser.add_argument(
        "--output", default="output", help="Output directory for PDF files"
    )
    parser.add_argument(
        "--config", default="settings.json", help="Configuration file path"
    )
    parser.add_argument(
        "--no-merge",
        action="store_true",
        help="Do not merge generated PDFs into a single file (default: merge is enabled)",
    )
    parser.add_argument(
        "--keep-individual",
        action="store_true",
        help="Keep individual PDF files after merging (default: delete them)",
    )

    args = parser.parse_args()

    try:
        # Initialize config manager first to get log level from settings
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()

        # Setup logging using config from settings.json (override CLI argument)
        config_log_level = config_manager.get_log_level()
        setup_logging(config_log_level)
        logger = get_app_logger()

        # Initialize components
        logger.info("Starting ExamTopics PDF Scraper...")
        search_engine = SearchEngine()
        pdf_generator = PDFGenerator()

        logger.info("Configuration loaded successfully")

        # Get exam configuration
        exam_config = config_manager.get_exam_config(args.exam)
        if not exam_config:
            logger.error(f"Exam '{args.exam}' not found in configuration")
            logger.info(f"Available exams: {config_manager.list_available_exams()}")
            return

        logger.info(f"Found exam config for: {args.exam}")

        # Validate question range
        if args.begin > args.end:
            logger.error(
                f"Begin question number ({args.begin}) cannot be greater than end question number ({args.end})"
            )
            return

        url_substring = exam_config["url_substring"]

        logger.info(f"Processing questions {args.begin} to {args.end}")

        # Track results
        successful_urls = []
        failed_questions = []
        generated_pdfs = []
        pdf_failures = []

        with open("filtered_links.json", "r", encoding="utf-8") as f:
            links = json.load(f)

        # Enumerate the links to get index and URL
        for question_num, result_url in enumerate(links, start=1):
            if result_url:
                successful_urls.append((question_num, result_url))
                logger.info(f"SUCCESS: Found URL for question {question_num}")

                # Generate PDF from the found URL
                pdf_filename = f"{args.exam}_question{question_num}.pdf"
                pdf_path = os.path.join(args.output, pdf_filename)

                logger.info(f"Generating PDF for question {question_num}...")
                pdf_success = pdf_generator.generate_pdf(result_url, pdf_path)

                if pdf_success:
                    generated_pdfs.append((question_num, pdf_path))
                    logger.info(f"PDF SUCCESS: Generated {pdf_filename}")
                else:
                    pdf_failures.append((question_num, result_url))
                    logger.error(
                        f"PDF FAILED: Could not generate PDF for question {question_num}"
                    )
            else:
                failed_questions.append(question_num)
                logger.warning(
                    f"FAILED: No valid URL found for question {question_num}"
                )


    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
