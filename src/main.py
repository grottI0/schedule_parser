import os
from glob import glob

import camelot
import pandas
from tqdm import tqdm

from files_downloader import FileDownloader
from tables import StudentGroupSchedule, ResultTable


def csv_from_pdf(pdf_path: str):

    tables = camelot.read_pdf(pdf_path, flavor='lattice', pages='1', line_scale=120)
    df = pandas.concat([table.df for table in tables])
    df.to_csv(f'../temp/{pdf_path}.csv', index=False)


os.mkdir('../temp')
fd = FileDownloader()
while len(fd.endpoints) == 0:
    fd = FileDownloader()
    print(fd.endpoints)
    fd.run()

rt = ResultTable()
pdfs = glob('../temp/*.pdf')

for pdf in tqdm(pdfs):
    csv_from_pdf(pdf)

csvs = glob('../temp/*.csv')

for csv in csvs:
    sg = StudentGroupSchedule(csv)
    rt.add_from_student_schedule(sg.df, sg.group)

rt.to_xlsx('../out.xlsx')
