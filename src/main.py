import os
import shutil
from glob import glob
from time import sleep

import camelot
import pandas
from tqdm import tqdm
from pypdf import PdfReader
from pypdf.errors import PdfStreamError

from files_downloader import FileDownloader
from tables import StudentGroupSchedule, ResultTable


def csv_from_pdf(pdf_path: str):

    tables = camelot.read_pdf(pdf_path, flavor='lattice', pages='1-end',
                              line_scale=120)
    df = pandas.concat([table.df for table in tables])
    df.to_csv(f'{pdf_path}.csv', index=False)


def convert_pdfs():
    pdfs = glob('temp/*.pdf')
    print('Converting files...')
    for pdf in tqdm(pdfs):
        csv_from_pdf(pdf)


def delete_useless(pdfs):
    for pdf in pdfs:
        reader = PdfReader(pdf)

        if 'Расписание учебных занятий' not in reader.pages[0].extract_text():
            os.remove(pdf)


os.mkdir('temp')
print('Getting endpoints...')
fd = FileDownloader()
print(f'Total: {len(fd.endpoints)}\n')
print('Async downloading...\n')

fd.run()

delete_useless(glob('temp/*.pdf'))

try:
    convert_pdfs()
except PdfStreamError:
    print('Async download failed...')
    print('Sync download through webdriver...')
    driver = fd.get_driver(download=True)
    shutil.rmtree(f'{os.getcwd()}/temp')
    for e in tqdm(fd.endpoints):
        driver.get(fd.ROOT_URL + e)
        sleep(2)
    driver.close()
    convert_pdfs()

rt = ResultTable()

csvs = glob('temp/*.csv')

print('Parsing...')
for csv in csvs:
    sg = StudentGroupSchedule(csv)
    rt.add_from_student_schedule(sg.df, sg.group)

rt.to_xlsx('out.xlsx')

print('Saved result to out.xlsx')

shutil.rmtree(f'{os.getcwd()}/temp')
