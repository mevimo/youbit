"""
Uploads videos to YouTube using Selenium.
"""
import time
from pathlib import Path
import logging

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from webdriver_manager.chrome import ChromeDriverManager
import browser_cookie3

from youbit.settings import Browser


C_YOUTUBE_URL = "https://www.youtube.com"
C_YOUTUBE_STUDIO_URL = "https://studio.youtube.com"
C_SLEEP_COEFFICIENT = 1
C_XPATH_UPLOAD_STATUS = (
    "/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/"
    "ytcp-animatable[2]/div/div[1]/ytcp-video-upload-progress/span"
)


class Uploader:
    def __init__(
        self, browser: Browser, headless: bool = True, suppress: bool = True
    ) -> None:
        options: Options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        if suppress:
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
        if headless:
            options.add_argument("--headless")
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
            )
        logging.getLogger("WDM").setLevel(
            logging.NOTSET
        )  # Turns off logging from webdriver_manager
        service = Service(ChromeDriverManager().install())
        self.browser = webdriver.Chrome(service=service, options=options)

        self._inject_user_cookies(browser)
        self._inject_youtube_consent_cookie()

    def upload(self, input_file: Path, description: str, title: str) -> str:
        self.browser.get(C_YOUTUBE_STUDIO_URL)
        self._sleep_long()

        self.browser.find_element(By.ID, "upload-icon").click()
        self._insert_video_file(input_file)
        self._insert_video_title(title)
        self._insert_video_description(description)
        self._set_not_for_kids()

        for _ in range(3):
            self.browser.find_element(By.ID, "next-button").click()

        self._sleep_short()
        self._set_video_as_unlisted()
        video_url = self._get_video_url()
        self._wait_for_upload_finish()
        self._click_done_btn()

        self._wait_until_last_dialog_available()
        self._sleep_short()
        self.browser.quit()
        return video_url

    def _inject_user_cookies(self, browser: Browser) -> None:
        supported_browsers = {
            Browser.CHROME: browser_cookie3.chrome,
            Browser.FIREFOX: browser_cookie3.firefox,
            Browser.OPERA: browser_cookie3.opera,
            Browser.EDGE: browser_cookie3.edge,
            Browser.CHROMIUM: browser_cookie3.chromium,
            Browser.BRAVE: browser_cookie3.brave,
        }
        cookiejar = supported_browsers[browser]()

        self.browser.get(C_YOUTUBE_URL)
        for cookie in cookiejar:
            if cookie.domain == ".youtube.com":
                self.browser.add_cookie(
                    {
                        "name": cookie.name,
                        "value": cookie.value,
                        "domain": cookie.domain,
                    }
                )

    def _inject_youtube_consent_cookie(self) -> None:
        self.browser.add_cookie(
            {
                "name": "CONSENT",
                "value": "YES+yt.453767233.en+FX+299",
                "domain": ".youtube.com",
            }
        )

    def _insert_video_file(self, input_file) -> None:
        self.browser.find_element(By.CSS_SELECTOR, 'input[name="Filedata"]').send_keys(
            str(input_file)
        )

    def _insert_video_title(self, title: str) -> None:
        title_element: WebElement = WebDriverWait(self.browser, timeout=10).until(
            lambda driver: driver.find_element(By.ID, "textbox")
        )
        self._sleep_short()
        title_element.send_keys(Keys.RETURN)
        title_element.send_keys(title)

    def _insert_video_description(self, description: str) -> None:
        ActionChains(self.browser).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(
            description
        ).perform()

    def _set_not_for_kids(self) -> None:
        not_for_kids = self.browser.find_element(By.NAME, "VIDEO_MADE_FOR_KIDS_NOT_MFK")
        not_for_kids.find_element(By.ID, "radioLabel").click()

    def _set_video_as_unlisted(self) -> None:
        self.browser.find_element(By.NAME, "UNLISTED").find_element(
            By.ID, "radioLabel"
        ).click()

    def _get_video_url(self) -> str:
        def url_not_empty(driver):
            return driver.find_element(
                By.CSS_SELECTOR, ".video-url-fadeable > .ytcp-video-info"
            ).text

        video_url = WebDriverWait(self.browser, timeout=20).until(url_not_empty)
        return video_url

    def _wait_for_upload_finish(self) -> None:
        status = self.browser.find_element(By.XPATH, C_XPATH_UPLOAD_STATUS)
        while "Uploading" in status.text:
            time.sleep(0.5)

    def _click_done_btn(self) -> None:
        done_btn = self.browser.find_element(By.ID, "done-button")
        WebDriverWait(self.browser, timeout=20).until(element_to_be_clickable(done_btn))
        done_btn.click()

    def _wait_until_last_dialog_available(self) -> None:
        def last_dialog_available(driver: WebDriver):
            return driver.find_elements(
                By.CSS_SELECTOR,
                "tp-yt-paper-dialog > .header > .header-content > #dialog-title",
            )

        WebDriverWait(self.browser, timeout=20).until(last_dialog_available)

    def _sleep_short(self) -> None:
        time.sleep(0.5 * C_SLEEP_COEFFICIENT)

    def _sleep_long(self) -> None:
        time.sleep(1 * C_SLEEP_COEFFICIENT)
