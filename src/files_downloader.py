import os
import re
from time import sleep
from glob import glob
import asyncio

import aiohttp
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, ChromeOptions


class FileDownloader:

    def __init__(self):
        self.ROOT_URL = "https://mtuci.ru"
        self.endpoints = self.get_files_urls(asyncio.run(self.get_html(self.ROOT_URL+'/time-table')))
        if len(self.endpoints) == 0:
            driver = self.get_driver()
            driver.get(self.ROOT_URL + '/time-table')
            sleep(3)
            self.endpoints = self.get_files_urls(driver.page_source)
            driver.close()

    def run(self):
        asyncio.run(self.download_files())

    @staticmethod
    def get_driver(download: bool = False) -> Chrome:

        options = ChromeOptions()
        options.add_argument('headless')

        if download:
            chrome_prefs = {
                "download.prompt_for_download": False,
                "plugins.always_open_pdf_externally": True,
                "download.open_pdf_in_system_reader": False,
                "profile.default_content_settings.popups": 0,
                "download.default_directory": f"{os.getcwd()}/temp"
            }
            options.add_experimental_option("prefs", chrome_prefs)

        return Chrome(options=options)

    async def download_files(self):
        async with aiohttp.ClientSession() as session:
            for endpoint in self.endpoints:
                async with session.get(self.ROOT_URL + endpoint) as response:
                    assert response.status == 200
                    with open(f'temp/{self.get_file_name(endpoint)}', "wb") as f:
                        while True:
                            chunk = await response.content.readany()
                            if not chunk:
                                break
                            f.write(chunk)

    @staticmethod
    async def get_html(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                a = await response.text()

        return a

    @staticmethod
    def get_file_name(endpoint) -> str:
        return endpoint.split('/')[-1]

    def check_group(self, s: str) -> bool:
        s = self.get_file_name(s)

        return s[0] in 'BMZ' and 'TSZOPB' not in s and 'SiSS' not in s

    def get_files_urls(self, html) -> list:
        soup = BeautifulSoup(html, "html.parser")
        content = soup.body.find_all('a', href=re.compile('.*.pdf$'))
        return [_['href'] for _ in content if self.check_group(_['href'])]
