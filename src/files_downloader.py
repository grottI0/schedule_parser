import os
import re
from time import sleep
from glob import glob

from selenium.webdriver import Chrome, ChromeOptions
from bs4 import BeautifulSoup


class FileDownloader:

    def __init__(self):
        self.endpoints = self.get_files_urls()

        self.BATCH_SIZE = 25
        self.INDEX = 0
        self.ROOT_URL = "https://mtuci.ru"

    @staticmethod
    def get_driver(download: bool = False) -> Chrome:

        options = ChromeOptions()

        if download:
            chrome_prefs = {
                "download.prompt_for_download": False,
                "plugins.always_open_pdf_externally": True,
                "download.open_pdf_in_system_reader": False,
                "profile.default_content_settings.popups": 0,
                "download.default_directory": "/home/denis/PycharmProjects/parser/temp"
            }
            options.add_experimental_option("prefs", chrome_prefs)

        return Chrome(options=options)

    @staticmethod
    def get_file_name(endpoint) -> str:
        return endpoint.split('/')[-1]

    def check_group(self, s: str) -> bool:
        s = self.get_file_name(s)

        return s[0] in 'BMZ' and 'TSZOPB' not in s and 'SiSS' not in s

    def get_files_urls(self) -> list:

        driver = self.get_driver()
        driver.get(self.ROOT_URL+'/time-table')
        sleep(1)
        html = driver.page_source
        driver.close()

        soup = BeautifulSoup(html, "html.parser")

        content = soup.body.find_all('a', href=re.compile('.*.pdf$'))

        return [_['href'] for _ in content if self.check_group(_['href'])]

    def download_one(self, endpoint: str) -> None:
        driver = self.get_driver(download=True)
        driver.get(self.ROOT_URL+endpoint)
        sleep(1.5)
        driver.close()

    def download_all(self) -> None:
        driver = self.get_driver(download=True)

        for d in self.endpoints[100:115]:
            driver.get(self.ROOT_URL + d)
            sleep(1.5)
        driver.close()

    def download_batch(self):
        driver = self.get_driver(download=True)
        for e in self.endpoints[self.INDEX:self.BATCH_SIZE]:
            driver.get(self.ROOT_URL + e)
            sleep(1.5)
        driver.close()
        self.INDEX += self.BATCH_SIZE

    @staticmethod
    def remove_pdfs():
        for f in glob("*.pdf"):
            os.remove(f)
