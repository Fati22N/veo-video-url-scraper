# config/settings.py
"""Configuration settings for the application."""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directories
DATA_DIR = os.path.join(BASE_DIR, 'data')
INPUT_DIR = os.path.join(DATA_DIR, 'input')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')
LOG_DIR = os.path.join(OUTPUT_DIR, 'logs')

# Create directories if they don't exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# File paths
INPUT_FILE = os.path.join(INPUT_DIR, 'urls.txt')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'video_urls.csv')
DEBUG_FILE = os.path.join(OUTPUT_DIR, 'page_debug.html')

# Selenium settings
DRIVER_TIMEOUT = 30
DELAY_BETWEEN_REQUESTS = 3
WAIT_TIMEOUT = 10

# Chrome options
CHROME_OPTIONS = [
    "--headless=new",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1920,1080",
    "--disable-blink-features=AutomationControlled"
]

CHROME_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ChromeDriver paths to check
CHROMEDRIVER_PATHS = [
    '/usr/local/bin/chromedriver',
    '/usr/bin/chromedriver',
    '/snap/bin/chromedriver',
    os.path.expanduser('~/chromedriver'),
    'chromedriver'
]

# Chrome browser paths to check
CHROME_BROWSER_PATHS = [
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium-browser',
    '/snap/bin/chromium'
]

# URL patterns for video extraction
VIDEO_URL_PATTERNS = [
    r'https://c\.veocdn\.com/[^"\']+/standard/machine/[^"\']+/video\.mp4',
    r'data-video-url="([^"]+)"',
    r'src="(https://c\.veocdn\.com/[^"]+)"',
    r'video-src="([^"]+)"',
    r'"url":"(https://c\.veocdn\.com[^"]+)"'
]

# Video container selectors
VIDEO_CONTAINER_SELECTORS = [
    'div[data-cy="match-page-player-container"]',
    'video',
    '.video-player',
    '[class*="video"]',
    '[class*="player"]'
]