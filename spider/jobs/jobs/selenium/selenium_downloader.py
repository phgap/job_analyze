# -*- coding: utf-8 -*-

from selenium import webdriver
import os
import sys
import time


class SeleniumDownloader(object):
    def __init__(self):
        path = os.path.dirname(os.path.abspath(__file__))
        if sys.platform == "win32":
            filename = r'\chromedriver.exe'
        else:
            filename = r'/chromedriver'

        # 使用headless无界面浏览器模式
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(path + filename, chrome_options=chrome_options)

    def load(self, url):
        self.driver.get(url)
        # 返回body内容
        time.sleep(1)
        return self.driver.page_source

    def next_page_by_click(self, selector):
        self.driver.find_element_by_css_selector(selector).click()
        time.sleep(1)
        return self.driver.page_source

    def get_status_code(self):
        pass

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    s = SeleniumDownloader()
    s.load("https://www.baidu.com")
    # s.next_page_by_click('')
