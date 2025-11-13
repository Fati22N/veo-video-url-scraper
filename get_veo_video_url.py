# get_veo_video_url
import re
import csv
import time
import logging
import os
import sys
import subprocess
from urllib.parse import urljoin

# Dependencies for dynamic scraping
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def install_chromedriver():
    """Attempt to install ChromeDriver"""
    logger.info("Attempting to install ChromeDriver...")
    try:
        # Try package manager first
        result = subprocess.run(['sudo', 'apt', 'update'], capture_output=True, text=True)
        result = subprocess.run(['sudo', 'apt', 'install', '-y', 'chromedriver'], capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("ChromeDriver installed successfully via apt")
            return True
    except Exception as e:
        logger.warning(f"Failed to install via apt: {e}")

    # Try manual download as fallback
    try:
        logger.info("Trying manual ChromeDriver installation...")
        subprocess.run([
            'wget', '-N',
            'https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.183/linux64/chromedriver-linux64.zip'
        ], check=True)
        subprocess.run(['unzip', '-o', 'chromedriver-linux64.zip'], check=True)
        subprocess.run(['sudo', 'mv', 'chromedriver-linux64/chromedriver', '/usr/local/bin/'], check=True)
        subprocess.run(['sudo', 'chmod', '+x', '/usr/local/bin/chromedriver'], check=True)
        subprocess.run(['rm', '-rf', 'chromedriver-linux64.zip', 'chromedriver-linux64'], check=True)
        logger.info("ChromeDriver installed successfully manually")
        return True
    except Exception as e:
        logger.error(f"Manual installation failed: {e}")
        return False


def get_chromedriver_path():
    """Get ChromeDriver path - try multiple locations"""
    possible_paths = [
        '/usr/local/bin/chromedriver',
        '/usr/bin/chromedriver',
        '/snap/bin/chromedriver',
        os.path.expanduser('~/chromedriver'),
        'chromedriver'
    ]

    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found ChromeDriver at: {path}")
            # Verify it's executable
            if os.access(path, os.X_OK):
                return path
            else:
                logger.warning(f"ChromeDriver found but not executable: {path}")
                try:
                    os.chmod(path, 0o755)
                    return path
                except:
                    pass

    logger.warning("ChromeDriver not found in standard locations.")

    # Try to install ChromeDriver
    if install_chromedriver():
        # Check again after installation
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found ChromeDriver at: {path} after installation")
                return path

    logger.error("Could not find or install ChromeDriver.")
    return None


def check_chrome_browser():
    """Check if Chrome browser is installed"""
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium-browser',
        '/snap/bin/chromium'
    ]

    for path in chrome_paths:
        if os.path.exists(path):
            logger.info(f"Found Chrome browser at: {path}")
            return True

    logger.error("Chrome browser not found. Please install Chrome first:")
    logger.error("sudo apt install google-chrome-stable")
    return False


DRIVER_PATH = get_chromedriver_path()


def read_urls_from_file(filename):
    """Read URLs from text file"""
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


def extract_video_url_from_page(html_content):
    """Extract video URL from page HTML source after dynamic content has loaded"""
    patterns = [
        r'https://c\.veocdn\.com/[^"\']+/standard/machine/[^"\']+/video\.mp4',
        r'data-video-url="([^"]+)"',
        r'src="(https://c\.veocdn\.com/[^"]+)"',
        r'video-src="([^"]+)"',
        r'"url":"(https://c\.veocdn\.com[^"]+)"'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, html_content)
        for match in matches:
            if 'video.mp4' in match:
                logger.info(f"Found video URL with pattern: {pattern}")
                return match if match.startswith('http') else urljoin('https://c.veocdn.com/', match)
            elif 'veocdn.com' in match:
                if re.search(r'/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/', match):
                    logger.info(f"Found Veo CDN URL with pattern: {pattern}")
                    return match

    # Additional debug: log if no patterns matched
    logger.debug("No video URL patterns matched in HTML content")
    return None


def get_video_url(driver, page_url, timeout=30):
    """Get video URL from a Veo match page using Selenium."""
    try:
        logger.info(f"Navigating to: {page_url}")
        driver.get(page_url)

        # Wait a bit for initial load
        time.sleep(3)

        # Try multiple selectors for video container
        selectors = [
            'div[data-cy="match-page-player-container"]',
            'video',
            '.video-player',
            '[class*="video"]',
            '[class*="player"]'
        ]

        element_found = False
        for selector in selectors:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.info(f"Found element with selector: {selector}")
                element_found = True
                break
            except TimeoutException:
                continue

        if not element_found:
            logger.warning("No video container found with common selectors, trying page source...")

        # Get page source and look for video URLs
        page_source = driver.page_source

        # Save page source for debugging if needed
        with open('page_debug.html', 'w', encoding='utf-8') as f:
            f.write(page_source)

        video_url = extract_video_url_from_page(page_source)

        if video_url:
            logger.info(f"Found video URL: {video_url}")
            return video_url
        else:
            logger.warning(f"No video URL found for: {page_url}")
            # Try to find any MP4 URLs in the page
            mp4_patterns = re.findall(r'https?://[^"\']+\.mp4[^"\']*', page_source)
            if mp4_patterns:
                logger.info(f"Found other MP4 URLs: {mp4_patterns[:3]}")  # Log first 3
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


def save_to_csv(results, output_file='video_urls.csv'):
    """Save results to CSV file"""
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Base URL', 'Video URL', 'Status'])

            for base_url, video_url in results:
                status = 'Success' if video_url else 'Failed'
                writer.writerow([base_url, video_url if video_url else 'N/A', status])

        logger.info(f"Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving to CSV: {str(e)}")


def setup_driver():
    """Initializes and configures the Selenium WebDriver"""
    if not DRIVER_PATH:
        logger.error("Cannot setup driver: ChromeDriver path not found")
        return None

    if not check_chrome_browser():
        return None

    logger.info("Setting up Chrome WebDriver...")
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")  # Use new headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        service = ChromeService(executable_path=DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        logger.info("WebDriver setup completed successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {str(e)}")
        return None


def main():
    input_file = 'urls.txt'
    output_file = 'video_urls.csv'
    delay_between_requests = 3  # Reduced delay for faster processing

    # Check requirements before starting
    if not DRIVER_PATH:
        logger.error("Exiting: ChromeDriver not available")
        return

    urls = read_urls_from_file(input_file)
    if not urls:
        logger.error("No URLs found in the input file. Create a file named 'urls.txt'.")
        return

    driver = setup_driver()
    if not driver:
        logger.error("Failed to setup WebDriver. Exiting.")
        return

    results = []

    try:
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing URL {i}/{len(urls)}")
            video_url = get_video_url(driver, url, timeout=30)
            results.append((url, video_url))

            if i < len(urls):
                logger.info(f"Waiting {delay_between_requests} seconds before next URL...")
                time.sleep(delay_between_requests)

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {str(e)}")
    finally:
        save_to_csv(results, output_file)
        if driver:
            driver.quit()
            logger.info("WebDriver closed.")

        success_count = sum(1 for _, video_url in results if video_url)
        failed_count = len(results) - success_count
        logger.info(f"Processing completed: {success_count} successful, {failed_count} failed")


if __name__ == "__main__":
    main()