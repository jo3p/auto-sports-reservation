import platform
from selenium.webdriver.chrome.options import Options


class WebDriver:
    """
    Extends the chromedriver class to be used as context manager.
    """
    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()


def create_chrome_options():
    if platform.system() == 'Linux':
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        return opts
    else:
        opts = Options()
        return opts


chrome_options = create_chrome_options()
