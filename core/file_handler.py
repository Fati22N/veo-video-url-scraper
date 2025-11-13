# core/file_handler.py
"""File handling operations."""
import csv
from typing import List, Tuple

from config.settings import INPUT_FILE, OUTPUT_FILE, DEBUG_FILE
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FileHandler:
    """Handles file operations for the application."""

    @staticmethod
    def read_urls_from_file(filename: str = INPUT_FILE) -> List[str]:
        """Read URLs from text file."""
        urls = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    url = line.strip()
                    if url and url.startswith('http'):
                        urls.append(url)
            logger.info(f"Read {len(urls)} URLs from {filename}")
            return urls
        except Exception as e:
            logger.error(f"Error reading file {filename}: {str(e)}")
            return []

    @staticmethod
    def save_to_csv(results: List[Tuple[str, str]], output_file: str = OUTPUT_FILE):
        """Save results to CSV file."""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Base URL', 'Video URL', 'Status'])

                for base_url, video_url in results:
                    status = 'Success' if video_url else 'Failed'
                    writer.writerow([
                        base_url,
                        video_url if video_url else 'N/A',
                        status
                    ])

            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {str(e)}")

    @staticmethod
    def save_debug_html(html_content: str, debug_file: str = DEBUG_FILE):
        """Save page source for debugging."""
        try:
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.debug(f"Debug HTML saved to {debug_file}")
        except Exception as e:
            logger.warning(f"Could not save debug HTML: {e}")