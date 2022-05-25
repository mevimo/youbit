from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
##TODO: cleanup imports once this script is finalized
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

##TODO add constants here for XPATHS for easy updates
##TODO add multi browser support, detect installed browsers and use one

class Uploader:

  def __init__(self, headless: bool = False):
    """
    Initializes the selenium webdriver.
    """
    options = Options()
    options.add_argument("--disable-gpu")
    if headless:
      options.add_argument("--headless")
    options.add_argument("--window-size=1280,800")
    self.browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
  def inject_cookies(self, cookies_path: str):
    """
    Inject cookies into the webdriver.
    """
    self.browser.get('https://www.youtube.com')
    with open(cookies_path, 'r') as f:
        cookies = json.load(f)
    for c in cookies:
        # no expiry means it doesn not expire lol
        c = {'name':c['name'], 'value':c['value'], 'domain':c['domain']}
        self.browser.add_cookie(c)
    ##TODO detect rotten cookies here somewhere

  def upload(self, filepath: str, title: str, desc: str, callback = None):
    self.browser.get('https://studio.youtube.com/')
    self.browser.find_element_by_id('create-icon').click()
    self.browser.find_element_by_id('text-item-0').click() # 'upload videos' button
    self.browser.find_element_by_css_selector('input[name="Filedata"]').send_keys(filepath)
    time.sleep(4) # wait for upload animation

    title_input = self.browser.find_element_by_id('textbox')
    title_input.send_keys(title)

    desc_container = self.browser.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[2]/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-mention-input/div')
    desc_container.send_keys(desc)

    not_for_kids = self.browser.find_element_by_name('VIDEO_MADE_FOR_KIDS_NOT_MFK')
    not_for_kids.find_element_by_id('radioLabel').click()

    self.browser.find_element_by_id('next-button').click()
    self.browser.find_element_by_id('next-button').click()
    self.browser.find_element_by_id('next-button').click()

    unlisted = self.browser.find_element_by_name('UNLISTED')
    unlisted.find_element_by_id('radioLabel').click()

    status = self.browser.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[1]/ytcp-video-upload-progress/span')
    # while 'Uploading' in status.text:
    #     if callback:
    #         try:
    #             pos = int(status.text[10:12])
    #         except IndexError:
    #             pos = 0
    #         callback(pos, 100)
    #     time.sleep(0.5)
    while status.text != 'Checks complete. No issues found.':
        time.sleep(1)
        
    self.browser.find_element_by_id('done-button').click()
    time.sleep(4)
    watch_url = self.browser.find_element_by_id('watch-url').text #should probably use selenium methods to wait until it finds this html element
    self.browser.quit()
    return watch_url


##TODO remove this in production
if __name__ == '__main__':
    uploader = Uploader()
    uploader.inject_cookies(cookies_path='E:/cook.json')
    uploader.upload(filepath='E:/yb-output.mp4', title='testtitle', desc='testdescription')