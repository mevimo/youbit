import time
from typing import Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
import browser_cookie3
from webdriver_manager.chrome import ChromeDriverManager


from selenium.webdriver.support.expected_conditions import element_to_be_clickable, text_to_be_present_in_element

class Uploader:
    def __init__(self, browser: str, headless: bool = True) -> None:
        """Initiliazes the selenium webdriver and injects it with the proper cookies.
        Make sure have gone to 'studio.youtube.com' with the account you wish to use, before
        using this. It will not traverse dialogue popups that you might encounter while going
        there for the first time, such as the one that asks for a channel name.
        Make sure there are no popups about anything when you go to 'studio.youtube.com'
        on the account in question.

        :param browser: The browser to extract YouTube cookies from. The currently logged in
            account will be used for upload. Supported arguments are 'chrome', 'firefox',
            'opera', 'edge', 'chromium', and 'brave'.
        :type browser: str
        :param headless: Hide the browser windows, defaults to True
        :type headless: bool, optional
        :raises ValueError: If the passer 'browser' argument is not recognized. 
        """
        options: Any = Options()
        options.add_argument("--disable-gpu")
        if headless:
            options.add_argument("--headless")
        options.add_argument("--window-size=1280,800")
        self.browser = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=options
        )

        if browser == 'chrome':
            cookiejar = browser_cookie3.chrome()
        elif browser == 'firefox':
            cookiejar = browser_cookie3.firefox()
        elif browser == 'opera':
            cookiejar = browser_cookie3.opera()
        elif browser == 'edge':
            cookiejar = browser_cookie3.edge()
        elif browser == 'chromium':
            cookiejar = browser_cookie3.chromium()
        elif browser == 'brave':
            cookiejar = browser_cookie3.brave()
        else:
            raise ValueError("Incompatible 'browser' argument.")

        self.browser.get("https://www.youtube.com")
        for cookie in cookiejar:
            if cookie.domain == ".youtube.com":
                self.browser.add_cookie(
                    {
                        "name": cookie.name,
                        "value": cookie.value,
                        "domain": cookie.domain,
                    }
                )
        self.browser.add_cookie(
            {
                'name': 'CONSENT',
                'value': 'YES+yt.453767233.en+FX+299',
                'domain': '.youtube.com'
            }
        )

    def upload(self, filepath: str, title: str, desc: str):
        self.browser.get("https://studio.youtube.com/")
        self.browser.find_element(By.CSS_SELECTOR, "#upload-icon > .remove-defaults").click()
        self.browser.find_element(By.CSS_SELECTOR, 'input[name="Filedata"]').send_keys(filepath)
        # while True:
        #     try:
        #         title_element = self.browser.find_element(By.ID, "textbox")
        #         break
        #     except NoSuchElementException:
        #         time.sleep(0.1)
        def title_textbox_available(driver):
            return driver.find_element(By.ID, "textbox")
        title_element = WebDriverWait(self.browser, timeout=10).until(title_textbox_available)
        title_element.send_keys(title)

        desc_element = self.browser.find_element(By.CSS_SELECTOR, "#description-textarea > #container > #outer > #child-input > #container-content #textbox")
        desc_element.send_keys(desc)

        not_for_kids = self.browser.find_element(By.NAME, "VIDEO_MADE_FOR_KIDS_NOT_MFK")
        not_for_kids.find_element(By.ID, "radioLabel").click()

        self.browser.find_element(By.ID, "next-button").click()
        self.browser.find_element(By.ID, "next-button").click()
        self.browser.find_element(By.ID, "next-button").click()

        unlisted = self.browser.find_element(By.NAME, "UNLISTED")
        unlisted.find_element(By.ID, "radioLabel").click()

        # status = self.browser.find_element_by_xpath(
        #     "/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[1]/ytcp-video-upload-progress/span"
        # )
        # while 'Uploading' in status.text:
        #     if callback:
        #         try:
        #             pos = int(status.text[10:12])
        #         except IndexError:
        #             pos = 0
        #         callback(pos, 100)
        #     time.sleep(0.5)
        # while status.text != "Checks complete. No issues found.":
        #     time.sleep(1)

        def url_not_empty(driver):
            return driver.find_element(By.CSS_SELECTOR, ".video-url-fadeable > .ytcp-video-info").text
        video_url = WebDriverWait(self.browser, timeout=20).until(url_not_empty)


        # watch_url = ''
        # while len(watch_url) == 0:
        #     time.sleep(0.1)
        #     watch_url = self.browser.find_element(By.CSS_SELECTOR, ".video-url-fadeable > .ytcp-video-info").text
        # while True:
        #     try:
        #         self.browser.find_element(By.ID, "done-button").click()
        #         break
        #     except ElementClickInterceptedException:
        #         time.sleep(0.1)

        done_btn = self.browser.find_element(By.ID, "done-button")
        WebDriverWait(self.browser, timeout=20).until(element_to_be_clickable(done_btn))
        
        self.browser.quit()
        return video_url


##TODO remove this in production
if __name__ == "__main__":
    uploader = Uploader(browser='firefox', headless=False)
    # uploader.browser.get('https://studio.youtube.com/')
    url = uploader.upload(
        filepath="E:/test_video_encode.mp4",
        title="testtitle",
        desc="testdescription"
    )
    print('------------------------------')
    print(type(url))
    print(url)
