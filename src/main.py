from glob import glob

import camelot
import pandas


def get_schedule_from_pdf(pdf_path: str):

    tables = camelot.read_pdf(pdf_path, flavor='lattice', pages='1', line_scale=120)
    df = pandas.concat([table.df for table in tables])
    df.to_csv(f'../temp/{pdf_path}.csv', index=False)


files = glob('../temp/*.pdf')
# print(len(files))
for file in files:
    get_schedule_from_pdf(file)

