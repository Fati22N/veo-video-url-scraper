# core/driver_manager.py
"""WebDriver management and setup."""
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

from config.settings import (
    CHROMEDRIVER_PATHS,
    CHROME_BROWSER_PATHS,
    CHROME_OPTIONS,
    CHROME_USER_AGENT
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DriverManager:
    """Manages ChromeDriver installation and WebDriver setup."""

    def __init__(self):
        self.driver_path = self._get_chromedriver_path()

    def _install_chromedriver(self) -> bool:
        """Attempt to install ChromeDriver."""
        logger.info("Attempting to install ChromeDriver...")

        # Try package manager first
        if self._install_via_apt():
            return True

        # Try manual download as fallback
        if self._install_manually():
            return True

        logger.error("All installation methods failed")
        return False

    def _install_via_apt(self) -> bool:
        """Install ChromeDriver using apt package manager."""
        try:
            result = subprocess.run(
                ['sudo', 'apt', 'update'],
                capture_output=True,
                text=True
            )
            result = subprocess.run(
                ['sudo', 'apt', 'install', '-y', 'chromedriver'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info("ChromeDriver installed successfully via apt")
                return True
        except Exception as e:
            logger.warning(f"Failed to install via apt: {e}")
        return False

    def _install_manually(self) -> bool:
        """Install ChromeDriver manually from Google's servers."""
        try:
            logger.info("Trying manual ChromeDriver installation...")
            subprocess.run([
                'wget', '-N',
                'https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.183/linux64/chromedriver-linux64.zip'
            ], check=True)
            subprocess.run(['unzip', '-o', 'chromedriver-linux64.zip'], check=True)
            subprocess.run([
                'sudo', 'mv', 'chromedriver-linux64/chromedriver', '/usr/local/bin/'
            ], check=True)
            subprocess.run(['sudo', 'chmod', '+x', '/usr/local/bin/chromedriver'], check=True)
            subprocess.run([
                'rm', '-rf', 'chromedriver-linux64.zip', 'chromedriver-linux64'
            ], check=True)
            logger.info("ChromeDriver installed successfully manually")
            return True
        except Exception as e:
            logger.error(f"Manual installation failed: {e}")
            return False

    def _get_chromedriver_path(self) -> str:
        """Get ChromeDriver path from possible locations."""
        for path in CHROMEDRIVER_PATHS:
            if os.path.exists(path):
                logger.info(f"Found ChromeDriver at: {path}")
                if os.access(path, os.X_OK):
                    return path
                else:
                    logger.warning(f"ChromeDriver found but not executable: {path}")
                    try:
                        os.chmod(path, 0o755)
                        return path
                    except Exception:
                        continue

        logger.warning("ChromeDriver not found in standard locations.")

        # Try to install ChromeDriver
        if self._install_chromedriver():
            for path in CHROMEDRIVER_PATHS:
                if os.path.exists(path):
                    logger.info(f"Found ChromeDriver at: {path} after installation")
                    return path

        logger.error("Could not find or install ChromeDriver.")
        return None

    def check_chrome_browser(self) -> bool:
        """Check if Chrome browser is installed."""
        for path in CHROME_BROWSER_PATHS:
            if os.path.exists(path):
                logger.info(f"Found Chrome browser at: {path}")
                return True

        logger.error("Chrome browser not found. Please install Chrome first:")
        logger.error("sudo apt install google-chrome-stable")
        return False

    def setup_driver(self):
        """Initialize and configure the Selenium WebDriver."""
        if not self.driver_path:
            logger.error("Cannot setup driver: ChromeDriver path not found")
            return None

        if not self.check_chrome_browser():
            return None

        logger.info("Setting up Chrome WebDriver...")
        try:
            chrome_options = Options()
            for option in CHROME_OPTIONS:
                chrome_options.add_argument(option)

            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f"user-agent={CHROME_USER_AGENT}")

            service = ChromeService(executable_path=self.driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)

            # Remove webdriver property to avoid detection
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            logger.info("WebDriver setup completed successfully")
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {str(e)}")
            return None