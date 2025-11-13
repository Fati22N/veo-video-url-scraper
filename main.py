# main.py
"""Main application entry point."""
import time
from typing import List, Tuple

from config.settings import INPUT_FILE, OUTPUT_FILE, DELAY_BETWEEN_REQUESTS
from core.driver_manager import DriverManager
from core.url_extractor import URLExtractor
from core.file_handler import FileHandler
from utils.logger import setup_logger

logger = setup_logger(__name__)


class VeoVideoURLScraper:
    """Main application class for scraping Veo video URLs."""

    def __init__(self):
        self.driver_manager = DriverManager()
        self.file_handler = FileHandler()
        self.results: List[Tuple[str, str]] = []

    def process_urls(self, urls: List[str]) -> List[Tuple[str, str]]:
        """Process all URLs and extract video URLs."""
        driver = self.driver_manager.setup_driver()
        if not driver:
            logger.error("Failed to setup WebDriver. Exiting.")
            return []

        url_extractor = URLExtractor(driver)

        try:
            for i, url in enumerate(urls, 1):
                logger.info(f"Processing URL {i}/{len(urls)}")

                video_url = url_extractor.get_video_url(url)
                self.results.append((url, video_url))

                # Add delay between requests (except for last one)
                if i < len(urls):
                    logger.info(f"Waiting {DELAY_BETWEEN_REQUESTS} seconds before next URL...")
                    time.sleep(DELAY_BETWEEN_REQUESTS)

        except KeyboardInterrupt:
            logger.info("Process interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {str(e)}")
        finally:
            driver.quit()
            logger.info("WebDriver closed.")

        return self.results

    def run(self):
        """Run the main application."""
        # Read URLs from file
        urls = self.file_handler.read_urls_from_file(INPUT_FILE)
        if not urls:
            logger.error(f"No URLs found in {INPUT_FILE}")
            return

        # Check if ChromeDriver is available
        if not self.driver_manager.driver_path:
            logger.error("Exiting: ChromeDriver not available")
            return

        # Process URLs
        self.process_urls(urls)

        # Save results
        self.file_handler.save_to_csv(self.results, OUTPUT_FILE)

        # Print summary
        success_count = sum(1 for _, video_url in self.results if video_url)
        failed_count = len(self.results) - success_count
        logger.info(f"Processing completed: {success_count} successful, {failed_count} failed")


def main():
    """Application entry point."""
    print(f"Input file location: {INPUT_FILE}")
    print(f"Output file location: {OUTPUT_FILE}")

    scraper = VeoVideoURLScraper()
    scraper.run()


if __name__ == "__main__":
    main()