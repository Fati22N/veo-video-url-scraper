# core/url_extractor.py
"""URL extraction functionality."""
import re
import time
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from config.settings import VIDEO_URL_PATTERNS, VIDEO_CONTAINER_SELECTORS
from utils.logger import setup_logger

logger = setup_logger(__name__)


class URLExtractor:
    """Extracts video URLs from Veo pages."""

    def __init__(self, driver, timeout=30):
        self.driver = driver
        self.timeout = timeout

    def extract_video_url_from_html(self, html_content: str) -> str:
        """Extract video URL from page HTML content."""
        for pattern in VIDEO_URL_PATTERNS:
            matches = re.findall(pattern, html_content)
            for match in matches:
                if 'video.mp4' in match:
                    logger.info(f"Found video URL with pattern: {pattern}")
                    return match if match.startswith('http') else urljoin('https://c.veocdn.com/', match)
                elif 'veocdn.com' in match:
                    if re.search(r'/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/', match):
                        logger.info(f"Found Veo CDN URL with pattern: {pattern}")
                        return match

        logger.debug("No video URL patterns matched in HTML content")
        return None

    def _wait_for_video_container(self, wait_timeout=10):
        """Wait for video container to load."""
        for selector in VIDEO_CONTAINER_SELECTORS:
            try:
                WebDriverWait(self.driver, wait_timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.info(f"Found element with selector: {selector}")
                return True
            except TimeoutException:
                continue
        return False

    def get_video_url(self, page_url: str) -> str:
        """Get video URL from a Veo match page."""
        try:
            logger.info(f"Navigating to: {page_url}")
            self.driver.get(page_url)

            # Wait for initial load
            time.sleep(3)

            # Wait for video container
            element_found = self._wait_for_video_container()

            if not element_found:
                logger.warning("No video container found with common selectors, trying page source...")

            # Get page source and extract URL
            page_source = self.driver.page_source
            video_url = self.extract_video_url_from_html(page_source)

            if video_url:
                logger.info(f"Found video URL: {video_url}")
                return video_url
            else:
                logger.warning(f"No video URL found for: {page_url}")
                self._log_alternative_mp4_urls(page_source)
                return None

        except TimeoutException:
            logger.error(f"Timeout waiting for page: {page_url}")
            return None
        except WebDriverException as e:
            logger.error(f"WebDriver error processing {page_url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error processing {page_url}: {str(e)}")
            return None

    def _log_alternative_mp4_urls(self, page_source: str):
        """Log alternative MP4 URLs found in page source."""
        mp4_patterns = re.findall(r'https?://[^"\']+\.mp4[^"\']*', page_source)
        if mp4_patterns:
            logger.info(f"Found other MP4 URLs: {mp4_patterns[:3]}")