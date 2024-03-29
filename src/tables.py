import re
import itertools

import pandas
from numpy import nan, isnan

from employers_tuple import employers
from data import subjects, letters_en_to_ru, days, schedule


class Element:

    def __init__(self, day: str, number: int, even: bool, subject: str, duration: str,
                 auditory: str, teacher: str, t: str, group: str):
        self.day = day
        self.number = schedule[number-1]
        self.even = even
        self.subject = subject
        self.duration = duration
        self.auditory = auditory
        self.teacher = teacher
        self.type = t
        self.group = group


class Column:

    def __init__(self, name: str):
        self.name = name
        self.elements = list()

    def add_element_(self, e: Element):
        self.elements.append(e)


class ResultTable:

    def __init__(self):
        self.columns = list()
        self.REP = {k: 0 for k in subjects}

    def add_column(self, name: str):
        self.columns.append(Column(name))

    @staticmethod
    def get_subject(s: str):
        subject = re.search(r'[\w\n\s]{0,56}', s)[0].replace('\n', '') if s is not nan else ''
        return subject.strip()

    @staticmethod
    def get_duration(s: str):
        duration = re.search(r'\([\w\s\-.]{0,15}\)', s)
        if duration is None:
            return ''
        return duration[0]

    def __contains__(self, item: str):
        for column in self.columns:
            if item in column.name:
                return True
        return False

    def __getitem__(self, item: str):
        res = list()
        for column in self.columns:
            if item in column.name:
                res.append(column)
        return res

    def insert_element(self, e: Element):

        if e.subject not in self:
            self.add_column(e.subject)
            self[e.subject][0].add_element_(e)

        else:
            exist = False
            for column in self[e.subject]:
                exist = False
                for element in column.elements:
                    if e.day == element.day and e.number == element.number and \
                            e.even == element.even and e.subject == element.subject and \
                            e.teacher in employers:
                        exist = True
                        break

                if not exist:
                    column.add_element_(e)
                    return

            if exist:
                self.REP[e.subject] += 1
                self.add_column(f'{e.subject} ({self.REP[e.subject]})')
                self[e.subject][-1].add_element_(e)
                return

    def add_from_student_schedule(self, table: pandas.DataFrame, group):
        _ = nan
        for row in table.iterrows():
            r = row[1]
            if r.iloc[0] is not nan:
                _ = r.iloc[0]

            subject = self.get_subject(r.iloc[6])
            employer = '' if isinstance(r.iloc[5], float) and isnan(r.iloc[5]) else r.iloc[5].strip()

            if subject in subjects and employer in employers:
                duration = self.get_duration(r.iloc[6])
                e_odd = Element(day=_, number=int(r.iloc[1][0]),
                                auditory=r.iloc[3], t=r.iloc[4],
                                teacher=r.iloc[5], subject=subject,
                                even=False, duration=duration, group=group)
                self.insert_element(e_odd)

            subject = self.get_subject(r.iloc[7])
            if subject in subjects and r.iloc[8] in employers:
                duration = self.get_duration(r.iloc[7])
                e_even = Element(day=_, number=int(r.iloc[1][0]),
                                 auditory=r.iloc[10], t=r.iloc[9],
                                 teacher=r.iloc[8], subject=subject,
                                 even=True, duration=duration, group=group)
                self.insert_element(e_even)

    def to_xlsx(self, xlsx_path: str):
        df = pandas.DataFrame()
        df['День'] = list(itertools.chain(*[[days[i]]*10 for i in range(len(days))]))

        _ = [[i] * 2 for i in schedule] * len(days)
        df['Пара'] = list(itertools.chain(*_))

        df['Четность'] = [r[0] % 2 != 0 for r in df.iterrows()]

        for column in self.columns:
            _ = column.name.split('\n')[0]
            df[_] = ['']*len(df)
            for element in column.elements:
                cond = (element.number == df['Пара']) & (element.even == df['Четность']) & (element.day == df['День'])

                df.loc[cond, _] = f'{element.teacher}\n{element.auditory}\n{element.type} {element.duration}\n{element.group}'

        del df['Четность']
        df.loc[df.assign(d=df['День']).duplicated(['День']), 'День'] = nan

        for i in range(6):
            buf = df.loc[i*10:(i+1)*10-1]
            buf.loc[buf.assign(d=buf['Пара']).duplicated(['Пара']), 'Пара'] = nan

        df = pandas.concat([df['День'], df['Пара'],
                           df.loc[:, (df.columns != 'День') & (df.columns != 'Пара')].sort_index(axis=1)],
                           axis=1, join='inner')

        writer = pandas.ExcelWriter(xlsx_path, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        wb = writer.book
        _format = wb.add_format({'align': 'center'})

        for i in range(1, 61):
            writer.sheets['Sheet1'].set_row(i, 80, _format)

        for i in range(len(self.columns)):
            writer.sheets['Sheet1'].set_column('A:BA', 500, _format)

        writer._save()


class StudentGroupSchedule:

    def __init__(self, csv_path: str):

        group = csv_path.split('/')[-1].split()[-1].split('.')[0]
        self.group = ''

        for i in range(len(group)):
            if group[i] in letters_en_to_ru:
                self.group += letters_en_to_ru[group[i]]
            else:
                self.group += group[i]

        self.df = pandas.read_csv(csv_path)
        self.df.dropna(how='all', axis=0, inplace=True)
