import os
import shutil
from glob import glob

import camelot
import pandas
from tqdm import tqdm

from files_downloader import FileDownloader
from tables import StudentGroupSchedule, ResultTable


def csv_from_pdf(pdf_path: str):

    tables = camelot.read_pdf(pdf_path, flavor='lattice', pages='1', line_scale=120)
    df = pandas.concat([table.df for table in tables])
    df.to_csv(f'{pdf_path}.csv', index=False)


os.mkdir('temp')
print('Getting endpoints...')
fd = FileDownloader()
print(f'Total: {len(fd.endpoints)}\n')
print('Downloading files...\n')
fd.run()

rt = ResultTable()
pdfs = glob('temp/*.pdf')
print('Converting files...')
for pdf in tqdm(pdfs):
    csv_from_pdf(pdf)

csvs = glob('temp/*.csv')

print('Parsing...')
for csv in csvs:
    sg = StudentGroupSchedule(csv)
    rt.add_from_student_schedule(sg.df, sg.group)

rt.to_xlsx('out.xlsx')
print('Saved result to out.xlsx')
os.rmdir('./temp')

shutil.rmtree(f'{os.getcwd()}/temp')
