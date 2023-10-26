import os
import re
from glob import glob
import asyncio

import aiohttp
from bs4 import BeautifulSoup


class FileDownloader:

    def __init__(self):
        self.ROOT_URL = "https://mtuci.ru"
        self.endpoints = self.get_files_urls(asyncio.run(self.get_html(self.ROOT_URL+'/time-table')))

    def run(self):
        asyncio.run(self.download_files())

    async def download_files(self):
        async with aiohttp.ClientSession() as session:
            for endpoint in self.endpoints:
                async with session.get(self.ROOT_URL + endpoint) as response:
                    assert response.status == 200
                    with open(f'../temp/{self.get_file_name(endpoint)}', "wb") as f:
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

    @staticmethod
    def remove_pdfs():
        for f in glob("*.pdf"):
            os.remove(f)
